from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate
from crate.client.exceptions import ProgrammingError

from vyi.users.model import User
from ..model import DB_SESSION, genid, refresher


REGISTER_SCHEMA = {
    'type': 'object',
    'properties': {
        'nickname': {
            'type': 'string'
        }
    }
}


@RestService('users')
class UserService(object):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route()
    def list(self):
        """ List all registered users """
        query = DB_SESSION.query(User).order_by(User.nickname)
        users = query.all()
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "nickname": user.nickname
            })
        return {"data": {"users": result}}

    @rpcmethod_route(route_suffix="/register", request_method="POST")
    @validate(REGISTER_SCHEMA)
    @refresher
    def register(self, nickname):
        """ Register a new user """
        user = User()
        user.id = genid(nickname)
        user.nickname = nickname
        try:
            DB_SESSION.add(user)
            return {"status": "success"}
        except ProgrammingError:
            # TODO: this does not seem to work... exception won't be catched.
            return {"status": "failed"}


def includeme(config):
    config.add_route('users', '/users', static=True)
