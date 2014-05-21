# -*- coding: utf-8; -*-
import sys
import requests
import random
import json
import time

from threading import Thread, Lock
from Queue import Queue


USERS = ["elon_musk", "albert_einstein", "nikola_tesla", "lovelace"]

vote_x_times = 50

max_concurrent_votes = 4
max_concurrent_refreshes = 1

refresh_vote_ec_1_queue = Queue(max_concurrent_votes * 2)
refresh_ec_1_queue = Queue(max_concurrent_refreshes * 2)

lock = Lock()

BASEURL = 'http://localhost:9100'
headers = {'content-type':'application/json'}


def release_the_kraken():
    try:
        voting_refresh = {'up': 0, 'down': 0}
        url_projects = BASEURL + '/projects'
        url_users = BASEURL + '/users'
        r = requests.get(url_projects)
        p_ids = [project['id'] for project in r.json()['data']['projects']]
        r = requests.get(url_users)
        users = [user for user in r.json()['data']['users']]

        user = random.choice(users)
        vote_ec_1_url = BASEURL + '/projects/vote_ec_1'
        refresh_ec_1_url = BASEURL + '/stats/refresh_ec_1'


        refresh_vote_args_ec_1 = (p_ids[1], refresh_vote_ec_1_queue,
                                  voting_refresh, vote_ec_1_url)
        refresh_args_ec_1 = (p_ids[1], refresh_ec_1_queue, refresh_ec_1_url)

        print "--> starting to vote (ec_1) and refresh the stats"
        start_daemons(max_concurrent_votes, vote, refresh_vote_args_ec_1)
        start_daemons(max_concurrent_refreshes, refresh, refresh_args_ec_1)
        for i in range(vote_x_times):
            refresh_vote_ec_1_queue.put(i)
            refresh_ec_1_queue.put(i)
        refresh_vote_ec_1_queue.join()
        refresh_ec_1_queue.join()

    except KeyboardInterrupt:
        sys.exit(1)


def start_daemons(max_concurrency, target, args):
    for _ in range(max_concurrency):
        th = Thread(target=target, args=args)
        th.setDaemon(True)
        th.start()


def start_task_and_wait(num_tasks, task_queue):
    for i in range(num_tasks):
        task_queue.put(i)
    task_queue.join()


def vote(project_id, queue, voting, url):
    while True:
        try:
            i = queue.get()
            v = random.choice(['up', 'down'])
            payload = {
                'project_id': project_id,
                'vote': v,
                'task_id': i
            }
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            rJson = r.json()
            with lock:
                print "[task_id: {0}]: voted for p.id '{1}': {2}".format(
                    i, project_id, v
                )
                msg = rJson['msg'] if rJson['status'] == 'failed' else ''
                if v == 'up':
                    voting['up'] += 1
                else:
                    voting['down'] += 1
                print '[task_id: {0}]: {1}: {2}, {3}'.format(
                    i,
                    r.status_code,
                    r.text, msg
                )
        except ValueError as e:
            with lock:
                print_error(e)
        finally:
            with lock:
                queue.task_done()


def refresh(project_id, queue, url):
    while True:
        try:
            i = queue.get()
            payload = {"project_id": project_id}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            rJson = r.json()
            with lock:
                print "[task_id: {0}]: refreshed for p.id '{1}'".format(
                    i, project_id
                )
                used = rJson['msg']['used']
                actual = rJson['msg']['actual']
                if used['up'] != actual['up'] or used['down'] != actual['down']:
                    print "[task_id: {0}]: different:".format(i)
                    print "used:   {0}".format(used)
                    print "actual: {0}".format(actual)
                else:
                    print "[task_id: {0}]: no conflict.".format(i)
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
