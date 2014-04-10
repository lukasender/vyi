from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from vyi.users.model import User
from vyi.projects.model import Vote, Project
from ..model import DB_SESSION, refresher, genuuid

import transaction


PROJECT_SCHEMA = {
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
        'vote_id': {
            'type': 'string',
            'required': False
        },
        'project_id': {
            'type': 'string',
            'required': False
        },
        'project_name': {
            'type': 'string',
            'required': False
        },
        'vote': {
            'enum': ['up', 'down']
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
        queryVotes = DB_SESSION.query(Vote).order_by(Vote.id)
        # TODO: improve this.. only fetch user_ids for [project.initiator_id]
        queryUsers = DB_SESSION.query(User).order_by(User.id)
        projects = queryProjects.all()
        votes = queryVotes.all()
        users = queryUsers.all()
        result = []
        def vote(votes, project):
            for v in votes:
                if v.id == project.vote_id:
                    return v
        def user(users, project):
            for u in users:
                if u.id == project.initiator_id:
                    return u

        for project in projects:
            v = vote(votes, project)
            u = user(users, project)
            up = v.up
            down = v.down
            proj = {
                "id": project.id,
                "name": project.name,
                "initiator": u.nickname,
                "votes": {
                    "id": v.id,
                    "up": up,
                    "down": down,
                    "sum": up - down
                },
                "description": project.description
            }
            result.append(proj)
        return {"data": {"projects": result}}

    @rpcmethod_route(route_suffix="/add", request_method="POST")
    @validate(PROJECT_SCHEMA)
    @refresher
    def add(self, name, initiator):
        """ add a new project """
        query = DB_SESSION.query(User).filter(User.nickname == initiator)
        user = query.all()
        if not user or len(user) > 1:
            return bad_request()
        user = user[0]

        vote = Vote()
        vote.id = genuuid()

        project = Project()
        project.vote_id = vote.id
        project.initiator_id = user.id
        project.name = name

        DB_SESSION.add(vote)
        DB_SESSION.add(project)

        return {"status":"success"}

    @rpcmethod_route(route_suffix="/vote", request_method="POST")
    @validate(VOTE_SCHEMA)
    def vote(self, vote, vote_id=None, project_id=None, project_name=None):
        if not (vote_id and project_id and project_name):
            bad_request("either 'project_id' or 'project_name' has to be \
                        present.")
        if vote_id:
            query = DB_SESSION.query(Vote).filter(Vote.id == vote_id)
            v = query.one()
            if vote == 'up':
                v.up += 1
            else:
                v.down += 1
            transaction.commit()
            return {"status":"success"}
        else:
            return bad_request("not yet implemented. please provide a \
                                'vote_id'.")


def bad_request(msg=None):
    # TODO: 403
    br = {"status": "failed"}
    if not msg:
        br['msg'] = msg
    return br



def includeme(config):
    config.add_route('projects', '/projects', static=True)
