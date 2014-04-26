from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql import text

from vyi.users.model import User
from vyi.projects.model import Project
from ..model import DB_SESSION, CRATE_CONNECTION, Base, refresher

import transaction


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

    @rpcmethod_route(route_suffix="/vote", request_method="POST")
    @validate(VOTE_SCHEMA)
    @refresher
    def vote(self, vote, project_id, task_id=None):
        query = DB_SESSION.query(Project).filter(Project.id == project_id)
        project = query.one()
        if vote == 'up':
            project.votes['up'] += 1
        else:
            project.votes['down'] += 1
        transaction.commit()
        if task_id is not None:
            print "executed by task_id '{0}'".format(task_id)
        return {"status":"success"}

    @rpcmethod_route(route_suffix="/vote_ec", request_method="POST")
    @validate(VOTE_SCHEMA)
    def vote_ec(self, vote, project_id, task_id=None):
        successful = False
        max_retries = retries = 5
        while not successful and retries > 0:
            cursor = CRATE_CONNECTION().cursor()
            cursor.execute("REFRESH TABLE projects")
            cursor.fetchall()
            cursor.execute("SELECT _version, projects.id, projects.votes " \
                           "FROM projects WHERE projects.id = ?", (project_id,))
            _version, proj_id, votes = cursor.fetchone()
            print "[task_id: {0}]: _version: {1}, proj_id: "\
                  "{2}, votes: {3}, try: {4}".format(
                task_id, _version, proj_id, votes, max_retries - retries + 1
            )
            update_stmt = prepare_update_statement(vote)
            new_vote = increase_vote(vote, votes)
            cursor.execute(update_stmt, (new_vote, _version, proj_id,))
            if cursor.rowcount == 1:
                successful = True
            else:
                retries -= 1

        if successful:
            return {
                "status":"success",
                "msg": "[task_id: {0}] successful after {1} (re)tries".format(
                    task_id, max_retries - retries + 1
                )
            }
        else:
            return {"status":"failed", "msg": "something went wrong."}


def prepare_update_statement(vote):
    update_stmt = "UPDATE projects " \
                  "SET projects.votes['{0}'] = ? " \
                  "WHERE _version = ? AND projects.id = ?"
    if vote == "up":
        update_stmt = update_stmt.format('up')
    else:
        update_stmt = update_stmt.format('down')
    return update_stmt


def increase_vote(vote, votes):
    v = votes['up'] + 1 if vote == "up" else votes['down'] + 1
    return v


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
