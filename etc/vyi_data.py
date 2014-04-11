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

    vote_x_times = 10 # for each project

    with Timer() as t:
        url = baseurl + '/projects/add'
        for i in range(1000):
            payload = {
                'name': 'test project {0}'.format(i),
                'initiator': random.choice(USERS)
            }
            with Timer(True):
                r = requests.post(url, data=json.dumps(payload),
                                  headers=headers)
                print i, r.status_code, r.text

        up = down = 0
        for i in range(1, vote_x_times + 1):
            url = baseurl + '/projects'
            r = requests.get(url)
            for project in r.json()['data']['projects']:
                vote = random.choice(['up', 'down'])
                if vote == 'up':
                    up += 1
                else:
                    down += 1
                print "voting '{0}' for project.id {1}".format(vote,
                                                               project['id'])
                url = baseurl + '/projects/vote'
                payload = {
                    'project_id': project['id'],
                    'vote': vote
                }
                r = requests.post(url, data=json.dumps(payload),
                                  headers=headers)
                print i, r.status_code, r.text

    print "I'm done! I did a total voting of {0} (up: {1}, down: {2}) and \
it took me {3} seconds.".format((up+down), up, down, t.secs)



if __name__ == '__main__':
    release_the_kraken()
