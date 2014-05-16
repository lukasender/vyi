from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from vyi.app.model import CRATE_CONNECTION, genid, genuuid, refresher

import time


REGISTER_SCHEMA = {
    'type': 'object',
    'properties': {
        'nickname': {
            'type': 'string'
        },
        'balance': {
            'type': 'number',
            'required': False
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
        cursor = CRATE_CONNECTION().cursor()
        users_stmt = "SELECT id, nickname FROM users ORDER BY nickname"
        user_ta_stmt = "SELECT sum(amount) FROM user_transactions "\
                       "WHERE user_id = ? AND state = ?"
        cursor.execute("REFRESH TABLE users")
        cursor.execute(users_stmt)
        users = cursor.fetchall()
        result = []
        for user in users:
            user_id = user[0]
            nickname = user[1]
            args = (user_id, "finished",)
            cursor.execute("REFRESH TABLE user_transactions")
            cursor.execute(user_ta_stmt, args)
            balance = cursor.fetchone()[0]
            result.append({
                "id": user_id,
                "nickname": nickname,
                "balance": balance
            })
        return {"data": {"users": result}}

    @rpcmethod_route(route_suffix="/register", request_method="POST")
    @validate(REGISTER_SCHEMA)
    @refresher
    def register(self, nickname, balance=0):
        """ Register a new user """
        cursor = CRATE_CONNECTION().cursor()
        user_id = genid(nickname)
        # add user
        stmt = "INSERT INTO users (id, nickname) VALUES (?, ?)"
        cursor.execute(stmt, (user_id, nickname,))
        if cursor.rowcount != 1:
            return {"status": "failed"}
        # initialise the user's transaction table
        stmt = "INSERT INTO user_transactions "\
               "(id, user_id, \"timestamp\", amount, transaction_id, state) "\
               "VALUES (?,?,?,?,?,?)"
        ta_id = genuuid()
        args = (ta_id, user_id, time.time(), balance, "register", "finished",)
        cursor.execute(stmt, args)
        if cursor.rowcount != 1:
            return {"status": "failed"}
        return {"status": "success"}


def includeme(config):
    config.add_route('users', '/users', static=True)
