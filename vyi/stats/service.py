from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from ..model import CRATE_CONNECTION

import time


STATS_SCHEMA = {
    'type': 'object',
    'properties': {
        'project_id': {
            'type': 'string'
        }
    }
}


@RestService('stats')
class TeamsService(object):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(route_suffix="/refresh_ec_1", request_method="POST")
    @validate(STATS_SCHEMA)
    def stats(self, project_id):
        cursor = CRATE_CONNECTION().cursor()
        cursor.execute("SELECT votes FROM projects " \
                       "WHERE id = ?", (project_id,))
        votes = cursor.fetchone()[0]
        if not votes:
            return bad_request("unknown project")

        success, msg = insert_new_stats(project_id, votes)

        if success:
            return {"status": "success", "msg": msg}
        else:
            return bad_request("something went wrong")


def insert_new_stats(project_id, votes):
    cursor = CRATE_CONNECTION().cursor()
    # fetch again to demonstrate, that 'votes' could already be old values
    cursor.execute("SELECT votes FROM projects " \
                       "WHERE id = ?", (project_id,))
    actual_votes = cursor.fetchone()[0]
    msg = "used values:  {0}\nactual values {1}".format(votes, actual_votes)
    cursor.execute(
        "INSERT INTO stats (project_id, \"timestamp\", up, down) " \
        "VALUES (?, ?, ?, ?)",
        (
            project_id,
            time.time(),
            votes['up'],
            votes['down']
        )
    )
    return True, msg


def bad_request(msg=None):
    # TODO: 403
    br = {"status": "failed"}
    if msg:
        br['msg'] = msg
    return br


def includeme(config):
    config.add_route('stats', '/stats', static=True)
