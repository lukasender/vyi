# -*- coding: utf-8; -*-
import requests
import random
import json
import time


USERS = ["lumannnn", "luibär", "albert_einstein", "nikola_tesla"]


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


def release_the_kraken():
    baseurl = 'http://localhost:9100'

    vote_x_times = 100

    with Timer() as t:
        url = baseurl + '/projects'
        r = requests.get(url)
        p_ids = [project['id'] for project in r.json()['data']['projects']]

        errors = []

        project_id = random.choice(p_ids)
        up = down = 0
        for i in range(vote_x_times):
            vote = random.choice(['up', 'down'])
            if vote == 'up':
                up += 1
            else:
                down += 1
            print "voting for project.id '{0}': {1}".format(project_id, vote)
            url = baseurl + '/projects/vote_ec'
            payload = {
                'project_id': project_id,
                'vote': vote
            }
            with Timer(True):
                r = requests.post(url, data=json.dumps(payload),
                                  headers=headers)
                rJson = r.json()
                if rJson['status'] == 'failed':
                    errors.append(rJson['msg'])
                print i, r.status_code, r.text

    print "I'm done! I did a total voting of {0} (up: {1}, down: {2}) " \
          "for project_id '{3}' and " \
          "it took me {4} seconds.".format((up+down), up, down,
                                           project_id, t.secs)
    print errors


if __name__ == '__main__':
    release_the_kraken()
