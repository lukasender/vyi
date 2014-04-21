# -*- coding: utf-8; -*-
import sys
import requests
import random
import json
import time

from threading import Thread, Lock
from Queue import Queue


USERS = ["lumannnn", "luibär", "albert_einstein", "nikola_tesla"]

vote_x_times = 1000

max_concurrent_connections = 4
q = Queue(max_concurrent_connections * 2)

lock = Lock()

BASEURL = 'http://localhost:9100'
headers = {'content-type':'application/json'}


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


def vote(project_id, queue, voting):
    while True:
        try:
            i = queue.get()
            v = random.choice(['up', 'down'])
            url = BASEURL + '/projects/vote_ec'
            payload = {
                'project_id': project_id,
                'vote': v
            }
            with Timer(True):
                r = requests.post(url, data=json.dumps(payload),
                                  headers=headers)
                rJson = r.json()
                lock.acquire()
                print "voted for project.id '{0}': {1}".format(project_id, v)
                msg = rJson['msg'] if rJson['status'] == 'failed' else ''
                if v == 'up':
                    voting['up'] += 1
                else:
                    voting['down'] += 1
                print 'task {0}, {1}: {2}, {3}'.format(i, r.status_code,
                                                       r.text, msg)
                lock.release()
        except Exception as e:
            lock.acquire()
            print '-'*40
            print r.reason, r.text
            print e
            print '-'*40
            lock.release()
        finally:
            lock.acquire()
            print '`--- finishing task {0}'.format(i)
            queue.task_done()
            lock.release()


def release_the_kraken():
    try:
        voting = {'up': 0, 'down': 0}
        with Timer() as t:
            url = BASEURL + '/projects'
            r = requests.get(url)
            p_ids = [project['id'] for project in r.json()['data']['projects']]

            errors = []

            project_id = random.choice(p_ids)
            for i in range(max_concurrent_connections):
                th = Thread(target=vote, args=(project_id, q, voting,))
                th.daemon = True
                th.start()

            for i in range(vote_x_times):
                q.put(i)
            q.join()

            up = voting['up']
            down = voting['down']
            print "I'm done! I did a total voting of {0} (up: {1}, down: {2}) "\
                  "for project_id '{3}' and " \
                  "it took me {4} seconds.".format((up+down), up, down,
                                                   project_id, t.secs)
            print errors
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    release_the_kraken()
