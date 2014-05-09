# -*- coding: utf-8; -*-
import sys
import requests
import random
import json
import time

from threading import Thread, Lock
from Queue import Queue


USERS = ["lumannnn", "luibär", "albert_einstein", "nikola_tesla"]

comment_x_times = 1000

max_concurrent_comments = 3

commenting_queue = Queue(max_concurrent_comments * 2)

lock = Lock()

BASEURL = 'http://localhost:9100'
headers = {'content-type':'application/json'}


def release_the_kraken():
    try:
        url_projects = BASEURL + '/projects'
        url_users = BASEURL + '/users'
        r = requests.get(url_projects)
        p_ids = [project['id'] for project in r.json()['data']['projects']]
        r = requests.get(url_users)
        users = [user for user in r.json()['data']['users']]

        proj_id = p_ids[0]
        user = random.choice(users)

        args_comments = (proj_id, user, commenting_queue)
        start_daemons(max_concurrent_comments, comment, args_comments)
        start_task_and_wait(comment_x_times, commenting_queue)

        print "Done!"
        print "User '{0}' commented {1} times for project_id {2}'".format(
            user['nickname'], comment_x_times, proj_id
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


def comment(project_id, user, queue):
    while True:
        try:
            i = queue.get()
            cmt = "A comment {0}, by {1}".format(i, user['nickname'])
            url = BASEURL + '/projects/comment'
            payload = {
                'project_id': project_id,
                'user_id': user['id'],
                'comment': cmt
            }
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            rJson = r.json()
            with lock:
                print "[task_id: {0}] commented: {1}, '{2}'".format(i, cmt,
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
