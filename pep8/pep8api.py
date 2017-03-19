#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import md5
import random
import ujson
from flask import Flask, request, render_template
from redis import StrictRedis   # service redis-server start
from pep8 import Pep8, REDIS_CFG


redis = StrictRedis(**REDIS_CFG)
app = Flask(__name__)
app.debug = True
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/ping')
def ping():
    return 'pong'

@app.route('/check_pep8', methods=['GET'])
def check_pep8_form():
    redis_key = 'ip_' + request.remote_addr
    redis_value = md5.md5(str(random.randint(0, 100000))).hexdigest()
    redis.set(redis_key, redis_value)
    kwargs = {'xx': redis_value}
    return render_template('check_pep8_form.html', **kwargs)

@app.route('/check_pep8', methods=['POST'])
def check_pep8():
    redis_key = 'ip_' + request.remote_addr
    if redis.get(redis_key) != request.values.get('xx'):
    #if 'aa' == request.values.get('code'):
        return 10**7 * 'blbci '
    code = request.values.get('code')
    ignore_codes = [c.strip() for c in request.values.get('ignore_codes', '').split(',')]
    ignore_type = ''.join({c.strip()[:1].upper() for c in request.values.get('ignore_type', '').split(',')})
    if code:
        pep8 = Pep8()
        result = pep8.pep8s(code, ignore_codes=ignore_codes, ignore_type=ignore_type)
        return ujson.dumps(result)
    else:
        return "Co jako validovat ??", 403   # 403 = Forbidden



if __name__ == "__main__":
    app.run(host = '0.0.0.0', threaded=True)   # nebo processes=3
    # 192.168.xxx.xxx
    # http://askubuntu.com/questions/224392/how-to-allow-remote-connections-to-flask
    #   netstat -tupln | grep ':5000'                    # zda server naslouchá
    #   iptables -I INPUT -p tcp --dport 5000 -j ACCEPT  # povolit
