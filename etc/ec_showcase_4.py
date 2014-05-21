# -*- coding: utf-8; -*-
import sys
import requests
import json
import time

from threading import Thread, Lock
from Queue import Queue


USERS = ["elon_musk", "albert_einstein", "nikola_tesla", "lovelace"]

x_transactions = 100

max_concurrent_transactions = 1

transactions_queue = Queue(max_concurrent_transactions * 2)

lock = Lock()

BASEURL = 'http://localhost:9100'
headers = {'content-type':'application/json'}


def release_the_kraken():
    try:
        url_users = BASEURL + '/users'
        r = requests.get(url_users)
        users = [user for user in r.json()['data']['users']]

        sender = users[0]
        receiver = users[1]

        args_transaction = (sender, receiver, transactions_queue)
        start_daemons(max_concurrent_transactions, transaction,
                      args_transaction)
        start_task_and_wait(x_transactions, transactions_queue)

        print "Done!"
    except KeyboardInterrupt:
        sys.exit(1)


def start_daemons(max_concurrency, target, args):
    for _ in range(max_concurrency):
        th = Thread(target=target, args=args)
        th.setDaemon(True)
        th.start()


def start_task_and_wait(num_tasks, task_queue):
    for i in range(1, num_tasks + 1):
        task_queue.put(i)
    task_queue.join()


def transaction(sender, receiver, queue):
    while True:
        try:
            i = queue.get()
            amount = i
            cmt = "Sending {0} from {1} to {2}".format(
                amount,
                sender['nickname'],
                receiver['nickname']
            )
            url = BASEURL + '/transactions/u2u'
            payload = {
                'sender': sender['id'],
                'receiver': receiver['id'],
                'amount': amount
            }
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            rJson = r.json()
            with lock:
                print "[task_id: {0}] transaction: {1}, '{2}'".format(i, cmt,
                                                                    rJson)
        except ValueError as e:
            with lock:
                print_error(e)
        finally:
            with lock:
                queue.task_done()


def print_error(e):
    print '-'*40
    print type(e)
    print e
    print '-'*40


class Timer(object):
    """ http://www.huyng.com/posts/python-performance-analysis/ """
    def __init__(self, verbose=False):
        self.start = None
        self.secs = 0
        self.msecs = 0
        self.end = 0
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs


if __name__ == '__main__':
    release_the_kraken()
