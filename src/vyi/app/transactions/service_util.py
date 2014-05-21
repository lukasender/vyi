import time

from vyi.app.model import genuuid
from crate.client.exceptions import ProgrammingError

MAX_RETRIES = 10


class TransactionUtil(object):

    def __init__(self, connection):
        self.cursor = connection.cursor()

    def set_transaction_state(self, transaction, state):
        """
        Update the state of a given transaction.
        """
        # refresh and get the actual value
        self.refresh("transactions")
        stmt = "SELECT _version, state FROM transactions WHERE id = ?"
        self.cursor.execute(stmt, (transaction['id'],))
        _version, orig_state = self.cursor.fetchone()
        # update
        stmt = "UPDATE transactions "\
               "SET state = ? WHERE id = ? AND _version = ? AND state = ?"
        self.cursor.execute(stmt, (state, transaction['id'], _version,
                                   orig_state))
        return self.cursor.rowcount == 1

    def get_balance_for(self, user_id):
        self.refresh("users")
        self.refresh("user_transactions")
        stmt = "SELECT sum(amount) "\
               "FROM user_transactions WHERE user_id = ? AND state = ?"
        self.cursor.execute(stmt, (user_id, "finished",))
        return self.cursor.fetchone()[0]

    def update_user_balance(self, user_id, transaction_id, amount, state):
        try:
            stmt = "INSERT INTO user_transactions (id, user_id, "\
                   "\"timestamp\", amount, transaction_id, state) "\
                   "VALUES (?,?,?,?,?,?)"
            args = (genuuid(), user_id, time.time(), amount,
                    transaction_id, state,)
            self.cursor.execute(stmt, args)
            return self.cursor.rowcount == 1
        except ProgrammingError, e:
            print e
            return False

    def update_pending_user_transaction(self, transaction_id, user_id):
        cursor = self.cursor
        self.refresh("user_transactions")
        stmt = "UPDATE user_transactions "\
               "SET state = ? "\
               "WHERE transaction_id = ? AND user_id = ?"
        args = ("finished", transaction_id, user_id,)
        cursor.execute(stmt, args)
        return cursor.rowcount == 1

    def user_balance_sufficient(self, sender, amount):
        return self.get_balance_for(sender) >= amount

    def get_user_transaction(self, transaction):
        cursor = self.cursor
        transaction_id = transaction['id']
        sender = transaction['sender']
        self.refresh("user_transactions")
        stmt = "SELECT id, transaction_id, user_id, \"timestamp\", state, "\
               "amount, _version FROM user_transactions "\
               "WHERE transaction_id = ?"
        cursor.execute(stmt, (transaction_id,))
        user_transactions = cursor.fetchall()

        def create_user_transaction(user_transaction):
            return {
                'id': user_transaction[0],
                'transaction_id': user_transaction[1],
                'user_id': user_transaction[2],
                'timestamp': user_transaction[3],
                'state': user_transaction[4],
                'amount': user_transaction[5],
                '_version': user_transaction[6],
            }

        result = {}
        assert len(user_transactions) <= 2
        for user_transaction in user_transactions:
            u_ta_dict = create_user_transaction(user_transaction)
            if u_ta_dict['user_id'] == sender:
                result['sender'] = u_ta_dict
            else:
                result['receiver'] = u_ta_dict
        return result

    def user_exists(self, user_id):
        stmt = "SELECT id FROM users WHERE id = ?"
        self.cursor.execute(stmt, (user_id,))
        return self.cursor.rowcount == 1

    def refresh(self, table):
        self.cursor.execute("REFRESH TABLE {0}".format(table))
