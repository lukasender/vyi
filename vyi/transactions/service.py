from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from ..model import CRATE_CONNECTION, genuuid

import time


TRANSACTIONS_SCHEMA = {
    'type': 'object',
    'properties': {
        'sender': {
            'type': 'string'
        },
        'receiver': {
            'type': 'string'
        },
        'amount': {
            'type': 'number'
        }
    }
}

STATE = [
"initial",
"in progress",
"committed",
"finished"
]

MAX_RETRIES = 10


@RestService('transactions')
class TransactionsService(object):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route()
    def transactions(self):
        pass

    @rpcmethod_route(route_suffix="/u2p", request_method="POST")
    @validate(TRANSACTIONS_SCHEMA)
    def transaction_user_to_project(self, project_id):
        pass

    @rpcmethod_route(route_suffix="/u2u", request_method="POST")
    @validate(TRANSACTIONS_SCHEMA)
    def transaction_user_to_user(self, sender, receiver, amount):
        if amount <= 0:
            return bad_request("'amount' must be a number > 0.")
        cursor = self._cursor()
        cursor.execute("REFRESH TABLE users")
        if not self._user_exists(sender):
            return bad_request("unknown 'sender'")
        if not self._user_exists(receiver):
            return bad_request("unknown 'receiver'")
        try:
            sender_user_id = self._user_balance_sufficient(sender, amount)
            # what we really would want to have is something like the
            # following:
            #
            #   WITH sufficient_balance AS (
            #       SELECT
            #           genuuid(),
            #           time.time(),
            #           sender,
            #           receiver,
            #           amount,
            #           "u2u"
            #           "initial"
            #       FROM users
            #       WHERE users.id = sender
            #       AND users.amount >= amount
            #   )
            #   INSERT INTO transactions
            #   SELECT * FROM sufficient_balance;
            stmt = "INSERT INTO transactions "\
                   "(id,\"timestamp\",sender,receiver,amount,type,state) "\
                   "VALUES (?, ?, ?, ? ,?, ?, ?)"
            transaction_id = genuuid()
            args = (
                transaction_id,
                time.time(),
                sender,
                receiver,
                amount,
                "u2u",
                "initial",
            )
            cursor.execute(stmt, args)
            if cursor.rowcount == 1:
                return {"status":"success"}
            return bad_request("could not add the new transaction.")
        except (NoResultFound, MultipleResultsFound):
            return bad_request("user balance insufficient.")

    @rpcmethod_route(route_suffix="/process", request_method="POST")
    def process_transactions(self):
        cursor = self._cursor()
        stmt = "SELECT id, sender, receiver, amount, type, state "\
               "FROM transactions WHERE state = ?"
        cursor.execute(stmt, ("initial",))
        transactions = cursor.fetchall()
        failed_transactions = []
        def _process_transaction(transaction_type):
            if transaction_type == "u2u":
                return self._process_transactions_u2u
            if transaction_type == "u2p":
                return self._process_transactions_u2p

        for t in transactions:
            transaction = {
                'id': t[0],
                'sender': t[1],
                'receiver': t[2],
                'amount': t[3],
                'type': t[4],
                'state': t[5]
            }
            process = _process_transaction(transaction['type'])
            successful = process(transaction)
            if not successful:
                failed_transactions.append(transaction)
        print failed_transactions
        return {
            "status":"success",
            "msg":"processed all transactions",
            "failed": failed_transactions
        }

    def _process_transactions_u2u(self, transaction):
        successful = self._set_transaction_state(transaction, "in progress")
        if not successful:
            return False
        try:
            sender = transaction['sender']
            receiver = transaction['receiver']
            amount = transaction['amount']
            successful = False
            tries = MAX_RETRIES
            while not successful and tries > 0:
                tries -= 1
                s_version, s_balance = self._get_balance_for(sender)
                new_balance = s_balance - amount
                successful = self._update_user_balance(
                        user_id=sender,
                        orig_version=s_version,
                        new_balance=new_balance
                    )
            if not successful:
                return False
            # reset for second account
            tries = MAX_RETRIES
            successful = False
            while not successful and tries > 0:
                r_version, r_balance = self._get_balance_for(receiver)
                tries -= 1
                new_balance = r_balance + amount
                successful = self._update_user_balance(
                        user_id=receiver,
                        orig_version=r_version,
                        new_balance=new_balance
                    )
            if not successful:
                return False
            return self._set_transaction_state(transaction, "committed")
        except (NoResultFound, MultipleResultsFound), e:
            print e
            return False

    def _process_transactions_u2p(self, transaction):
        pass

    def _set_transaction_state(self, transaction, state):
        cursor = self._cursor()
        stmt = "UPDATE transactions "\
               "SET state = ? WHERE id = ?"
        cursor.execute(stmt, (state, transaction['id'],))
        if cursor.rowcount == 1:
            return True
        return False

    def _get_balance_for(self, user_id):
        cursor = self._cursor()
        cursor.execute("REFRESH TABLE users")
        stmt = "SELECT _version, balance FROM users WHERE id = ?"
        cursor.execute(stmt, (user_id,))
        return cursor.fetchone()

    def _update_user_balance(self, user_id, orig_version, new_balance):
        cursor = self._cursor()
        stmt = "UPDATE users "\
               "SET balance = ? " \
               "WHERE id = ? AND _version = ?"
        cursor.execute(stmt, (new_balance, user_id, orig_version))
        if cursor.rowcount == 1:
            return True
        return False

    def _user_balance_sufficient(self, sender, amount):
        cursor = self._cursor()
        stmt = "SELECT _id FROM users WHERE id = ? AND balance >= ?"
        cursor.execute(stmt, (sender, amount,))
        return cursor.fetchone()

    def _user_exists(self, user_id):
        cursor = self._cursor()
        stmt = "SELECT id FROM users WHERE id = ?"
        cursor.execute(stmt, (user_id,))
        return cursor.rowcount == 1

    def _cursor(self):
        return CRATE_CONNECTION().cursor()


def bad_request(msg=None):
    # TODO: 403
    br = {"status": "failed"}
    if msg:
        br['msg'] = msg
    return br


def includeme(config):
    config.add_route('transactions', '/transactions', static=True)
