# -*- coding: utf-8; -*-
import sys
import requests
import random
import json
import time

from threading import Thread, Lock
from Queue import Queue


USERS = ["lumannnn", "luibär", "albert_einstein", "nikola_tesla"]

vote_x_times = 100
comment_x_times = 1000

max_concurrent_votes = 2

voteing_ec_1_queue = Queue(max_concurrent_votes * 2)
voteing_ec_2_queue = Queue(max_concurrent_votes * 2)

lock = Lock()

BASEURL = 'http://localhost:9100'
headers = {'content-type':'application/json'}


def release_the_kraken():
    try:
        voting_ec_1 = {'up': 0, 'down': 0}
        voting_ec_2 = {'up': 0, 'down': 0}
        url_projects = BASEURL + '/projects'
        url_users = BASEURL + '/users'
        r = requests.get(url_projects)
        p_ids = [project['id'] for project in r.json()['data']['projects']]
        r = requests.get(url_users)
        users = [user for user in r.json()['data']['users']]

        proj_id = p_ids[0]
        user = random.choice(users)
        vote_ec_1_url = BASEURL + '/projects/vote_ec_1'
        vote_ec_2_url = BASEURL + '/projects/vote_ec_2'
        vote_args_ec_1 = (proj_id, voteing_ec_1_queue,
                          voting_ec_1, vote_ec_1_url)
        vote_args_ec_2 = (proj_id, voteing_ec_2_queue,
                          voting_ec_2, vote_ec_2_url)

        print "--> starting to vote (ec_1)"
        start_daemons(max_concurrent_votes, vote, vote_args_ec_1)
        start_task_and_wait(vote_x_times, voteing_ec_1_queue)

        print "--> starting to vote (ec_2)"
        start_daemons(max_concurrent_votes, vote, vote_args_ec_2)
        start_task_and_wait(vote_x_times, voteing_ec_2_queue)

        up_ec_1 = voting_ec_1['up']
        down_ec_1 = voting_ec_1['down']

        up_ec_2 = voting_ec_2['up']
        down_ec_2 = voting_ec_2['down']

        print "Done!"
        print "I did a total voting (ec_1) of {0} (down: {1}, up: {2}) "\
              "for project_id '{3}'".format(
                (up_ec_1+down_ec_1), down_ec_1, up_ec_1, proj_id
              )
        print "I did a total voting (ec_2) of {0} (down: {1}, up: {2}) "\
              "for project_id '{3}'".format(
                (up_ec_2+down_ec_2), down_ec_2, up_ec_2, proj_id
              )
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
