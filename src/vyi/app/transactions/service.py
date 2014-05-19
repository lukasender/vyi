from lovely.pyrest.rest import RestService, rpcmethod_route
from lovely.pyrest.validation import validate

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from ..model import genuuid, CRATE_CONNECTION

from .service_util import TransactionUtil

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


@RestService('transactions')
class TransactionsService(object):

    def __init__(self, request):
        self.request = request
        self.cursor = CRATE_CONNECTION().cursor()
        self.util = TransactionUtil(CRATE_CONNECTION())

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
        self.util.refresh("users")
        if not self.util.user_exists(sender):
            return bad_request("unknown 'sender'")
        if not self.util.user_exists(receiver):
            return bad_request("unknown 'receiver'")
        try:
            self.util.user_balance_sufficient(sender, amount)
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
            self.cursor.execute(stmt, args)
            if self.cursor.rowcount == 1:
                return {"status":"success"}
            return bad_request("could not add the new transaction.")
        except (NoResultFound, MultipleResultsFound):
            return bad_request("user balance insufficient.")

    @rpcmethod_route(route_suffix="/process", request_method="POST")
    def process_transactions(self):
        cursor = self.cursor
        self.util.refresh("transactions")
        stmt = "SELECT id, sender, receiver, amount, type, state "\
               "FROM transactions WHERE state != ?"
        cursor.execute(stmt, ("finished",))
        transactions = cursor.fetchall()
        failed_transactions = []
        for t in transactions:
            transaction = {
                'id': t[0],
                'sender': t[1],
                'receiver': t[2],
                'amount': t[3],
                'type': t[4],
                'state': t[5]
            }
            successful = self._process_transactions(transaction)
            if not successful:
                failed_transactions.append(transaction)
        return {
            "status":"success",
            "msg":"processed all transactions",
            "failed_transactions": failed_transactions
        }

    def _process_transactions(self, transaction):
        def __get_process(state):
            if state == 'initial':
                return self._process_transaction_initial
            elif state == 'in progress':
                return self._process_transaction_inprogress
            elif state == 'committed':
                return self._process_transaction_committed
            return self._process_critial_error

        process = __get_process(transaction['state'])
        return process(transaction)

    def _process_transaction_initial(self, transaction):
        """
        Processes a transaction with the state 'initial'.
        """
        ok = self.util.set_transaction_state(transaction, 'in progress')
        # TODO in progress by...
        if not ok:
            return False
        ok = self._update_balance_sender(transaction, 'pending')
        if not ok:
            return False
        # reset for second account
        ok = self._update_balance_receiver(transaction, 'pending')
        if not ok:
            return False
        ok = self.util.set_transaction_state(transaction, 'committed')
        if not ok:
            return False
        ok = self._update_pending_user_transaction_sender(transaction)
        if not ok:
            return False
        ok = self._update_pending_user_transaction_receiver(transaction)
        if not ok:
            return False
        # TODO, remove 'in progress by'
        return self.util.set_transaction_state(transaction, 'finished')

    def _process_transaction_inprogress(self, transaction):
        """
        A transaction was found with state 'in progress'.
        This process needs to check if any other process is processing the
        given transaction.
        If another process is processing the transaction, this process will do
        nothing.
        If not, this process continues accordingly.
        """
        # TODO
        # check if an other process is processing this transaction?
        user_transactions = self.util.get_user_transaction(transaction)
        u_ta_sender = user_transactions.get('sender', None)
        u_ta_receiver = user_transactions.get('receiver', None)
        if u_ta_sender is None:
            ok = self._update_balance_sender(transaction, 'pending')
            if not ok:
                return False
        if u_ta_receiver is None:
            ok = self._update_balance_receiver(transaction, 'pending')
            if not ok:
                return False
        ok = self.util.set_transaction_state(transaction, 'committed')
        if not ok:
            return False
        ok = self._update_pending_user_transaction_sender(transaction)
        if not ok:
            return False
        ok = self._update_pending_user_transaction_receiver(transaction)
        if not ok:
            return False
        return self.util.set_transaction_state(transaction, "finished")

    def _process_transaction_committed(self, transaction):
        """
        A transaction was found with the state 'committed'.
        This process needs to check if any other process is processing the
        given transaction.
        If another process is processing the transaction, this process will do
        nothing.
        If not, this process continues accordingly.
        """
        # TODO
        # check if an other process is processing this transaction?
        user_transactions = self.util.get_user_transaction(transaction)
        u_ta_sender = user_transactions['sender']
        u_ta_receiver = user_transactions['receiver']
        if u_ta_sender['state'] == 'pending':
            ok = self._update_pending_user_transaction_sender(transaction)
            if not ok:
                return False
        if u_ta_receiver['state'] == 'pending':
            ok = self._update_pending_user_transaction_receiver(transaction)
            if not ok:
                return False
        return self.util.set_transaction_state(transaction, 'finished')

    def _process_critial_error(self, transaction):
        """
        Mother of god! A critical error occurred. Only a human can now help...
        """
        # TODO
        # notify a human
        pass

    def _update_balance_sender(self, transaction, state):
        ta_id = transaction['id']
        sender = transaction['sender']
        amount = -transaction['amount']
        return self.util.update_user_balance(
            user_id=sender,
            transaction_id=ta_id,
            amount=amount,
            state=state
        )

    def _update_balance_receiver(self, transaction, state):
        ta_id = transaction['id']
        receiver = transaction['receiver']
        amount = transaction['amount']
        return self.util.update_user_balance(
            user_id=receiver,
            transaction_id=ta_id,
            amount=amount,
            state=state
        )

    def _update_pending_user_transaction_sender(self, transaction):
        transaction_id = transaction['id']
        user_id = transaction['sender']
        return self.util.update_pending_user_transaction(transaction_id,
                                                         user_id)

    def _update_pending_user_transaction_receiver(self, transaction):
        transaction_id = transaction['id']
        user_id = transaction['receiver']
        return self.util.update_pending_user_transaction(transaction_id,
                                                         user_id)

def bad_request(msg=None):
    # TODO: 403
    br = {"status": "failed"}
    if msg:
        br['msg'] = msg
    return br


def includeme(config):
    config.add_route('transactions', '/transactions', static=True)
