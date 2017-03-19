#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import md5
import time

from grab import Grab
from grab.error import GrabTimeoutError
from redis import StrictRedis   # service redis-server start
import ujson


REDIS_CFG = {
    'host': 'localhost',
    'port': 6379
}


class Pep8(object):
    starting = 'http://pep8online.com'
    form_action = 'http://pep8online.com/checkresult'

    def __init__(self):
        self.g = Grab()
        self.redis = StrictRedis(**REDIS_CFG)

    def pep8(self, tested_file='file.py', ignore_codes=None, ignore_type=''):
        return self.get_and_filter(self.query_file(tested_file), ignore_codes, ignore_type)

    def pep8s(self, tested_string, ignore_codes=None, ignore_type=''):
        if ignore_codes is None:
            ignore_codes = []
        return self.get_and_filter(self.query_string(tested_string), ignore_codes, ignore_type)

    def get_and_filter(self, result, ignore_codes=None, ignore_type=''):
        if ignore_codes is None:  # in fact it is never modified, but to be sure
            ignore_codes = []
        return filter(lambda problem: problem[0][:1] not in ignore_type and problem[0] not in ignore_codes, result)

    def query_file(self, tested_file):
        with open(tested_file) as f:
            content = f.read()
        return self.query_string(content)

    def query_string(self, tested_string):
        redis_key = md5.md5(tested_string).hexdigest()
        msg = 'Served from '
        starting = time.time()
        redis_value = self.redis.get(redis_key)
        if redis_value:
            msg += 'redis'
            problems = ujson.loads(redis_value)
        else:
            msg += 'pep8online.com'
            self.g.go(self.starting)        # except grab.error.GrabTimeoutError
            gff = self.g.doc.form_fields()
            gff['code'] = tested_string
            self.g.go(self.form_action, post=gff)
            problems = self.parse_response()
            self.redis.set(redis_key, ujson.dumps(problems))
        log_it = self.redis.get('config_log')
        if log_it is None or log_it == '1':
            msg += ', %.3f seconds.' % (time.time() - starting)
            print(msg)
        return problems

    def parse_response(self):
        problems = []
        for problem in self.g.doc.tree.cssselect('.tr-result'):
            tds = problem.findall('td')
            problems.append((tds[0].text_content().strip(), tds[1].text.strip(), tds[2].text.strip(), tds[3].text.strip()))
        return problems


if __name__ == '__main__':
    pep8 = Pep8()
    print(pep8.pep8())
