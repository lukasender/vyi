from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from vyi.app.users.model import User
from vyi.app.projects.model import Project
from ..model import DB_SESSION, CRATE_CONNECTION, refresher

import time


PROJECTS_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string'
        },
        'initiator': {
            'type': 'string'
        }
    }
}

VOTE_SCHEMA = {
    'type': 'object',
    'properties': {
        'project_id': {
            'type': 'string'
        },
        'vote': {
            'enum': ['up', 'down']
        },
        'task_id': {
            'type': 'number',
            'required': False
        }
    }
}

COMMENT_SCHEMA = {
    'type': 'object',
    'properties': {
        'project_id': {
            'type': 'string'
        },
        'user_id': {
            'type': 'string'
        },
        'comment': {
            'type': 'string'
        }
    }
}


@RestService('projects')
class ProjectService(object):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route()
    def list(self):
        """ List all projects """
        queryProjects = DB_SESSION.query(Project).order_by(Project.name)
        #queryVotes = DB_SESSION.query(Vote).order_by(Vote.id)
        # TODO: improve this.. only fetch user_ids for [project.initiator_id]
        queryUsers = DB_SESSION.query(User).order_by(User.id)
        projects = queryProjects.all()
        users = queryUsers.all()
        result = []
        def user(users, project):
            for u in users:
                if u.id == project.initiator_id:
                    return u

        for project in projects:
            u = user(users, project)
            result.append(create_project(project, u))
        return {"data": {"projects": result}}

    @rpcmethod_route(route_suffix="/{project_id}")
    def list_project(self, project_id):
        queryProject = DB_SESSION.query(Project).filter(
                                  Project.id == project_id)
        try:
            project = queryProject.one()
            queryUser = DB_SESSION.query(User).filter(
                                   User.id == project.initiator_id)
            user = queryUser.one()
            return {"data": {"projects": [create_project(project, user)]}}
        except (NoResultFound, MultipleResultsFound):
            return bad_request("not found")

    @rpcmethod_route(route_suffix="/add", request_method="POST")
    @validate(PROJECTS_SCHEMA)
    @refresher
    def add(self, name, initiator):
        """ add a new project """
        query = DB_SESSION.query(User).filter(User.nickname == initiator)
        try:
            user = query.one()
        except (NoResultFound, MultipleResultsFound):
            return bad_request('failed for {0}'.format(initiator))

        project = Project()
        project.initiator_id = user.id
        project.name = name
        project.votes = {'up': 0, 'down': 0}
        DB_SESSION.add(project)
        return {"status":"success"}

    @rpcmethod_route(route_suffix="/vote_ec_1", request_method="POST")
    @validate(VOTE_SCHEMA)
    def vote_ec_1(self, vote, project_id, task_id=None):
        successful = False
        max_retries = retries = 5
        while not successful and retries > 0:
            current_retries = max_retries - retries + 1
            cursor = CRATE_CONNECTION().cursor()
            cursor.execute("REFRESH TABLE projects")
            cursor.execute("SELECT _version, projects.id, projects.votes " \
                           "FROM projects WHERE projects.id = ?", (project_id,))
            _version, proj_id, votes = cursor.fetchone()
            print "[task_id: {task_id}]: _version: {ver}, proj_id: "\
                  "{p_id}, votes: {votes}, tries: {tries}".format(
                task_id=task_id,
                ver=_version,
                p_id=proj_id,
                votes=votes,
                tries=current_retries
            )
            new_vote = votes['up'] + 1 if vote == "up" else votes['down'] + 1
            upd_stmt = "UPDATE projects " \
                       "SET projects.votes['{0}'] = ? " \
                       "WHERE _version = ? AND projects.id = ?"
            if vote == "up":
                upd_stmt = upd_stmt.format('up')
            else:
                upd_stmt = upd_stmt.format('down')
            cursor.execute(upd_stmt, (new_vote, _version, proj_id,))
            if cursor.rowcount == 1:
                successful = True
            else:
                retries -= 1

        if successful:
            return {
                "status":"success",
                "msg": "[task_id: {0}] successful after {1} (re)tries".format(
                    task_id,
                    max_retries - retries + 1
                )
            }
        else:
            return {"status":"failed", "msg": "something went wrong."}

    @rpcmethod_route(route_suffix="/vote_ec_2", request_method="POST")
    @validate(VOTE_SCHEMA)
    def vote_ec_2(self, vote, project_id, task_id=None):
        cursor = CRATE_CONNECTION().cursor()
        cursor.execute("REFRESH TABLE projects")
        cursor.execute("SELECT projects.id " \
                       "FROM projects WHERE projects.id = ?", (project_id,))
        proj_id = cursor.fetchone()
        if not proj_id:
            return bad_request("unknown project")
        else:
            print "[task_id: {task_id}]: proj_id: {p_id}".format(
                task_id=task_id,
                p_id=proj_id
            )
            stmt = "INSERT INTO votes " \
                   "(project_id, up, down) " \
                   "VALUES (?, ?, ?)"
            print stmt
            up = down = 0
            if vote == "up":
                up = 1
            else:
                down = 1
            cursor.execute(
                stmt,
                (project_id, up, down)
            )
            return {"status": "success"}

    @rpcmethod_route(route_suffix="/comment", request_method="POST")
    @validate(COMMENT_SCHEMA)
    def comment(self, project_id, user_id, comment):
        cursor = CRATE_CONNECTION().cursor()
        timestamp = time.time()
        cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
        p_id = cursor.fetchone()
        cursor.execute("SELECT id from users WHERE id = ?", (user_id,))
        u_id = cursor.fetchone()
        if not p_id:
            return bad_request("unknown project")
        elif not u_id:
            return bad_request("unknown user")
        else:
            stmt = "INSERT INTO comments " \
                   "(project_id, user_id, " \
                   "comment, timestamp) " \
                   "VALUES (?, ?, ?, ?)"
            print stmt
            cursor.execute(
                stmt,
                (project_id, user_id, comment, timestamp)
            )
            return {"status": "success"}


def create_project(project, user):
    up = project.votes['up']
    down = project.votes['down']
    proj = {
        "id": project.id,
        "name": project.name,
        "initiator": user.nickname,
        "votes": {
            "up": up,
            "down": down,
            "sum": up - down
        },
        "description": project.description
    }
    return proj


def bad_request(msg=None):
    # TODO: 403
    br = {"status": "failed"}
    if msg:
        br['msg'] = msg
    return br


def includeme(config):
    config.add_route('projects', '/projects', static=True)
