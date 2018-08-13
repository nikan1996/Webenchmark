#!/usr/bin/env python
# encoding: utf-8
"""
启动一个本地服务，用于测试
@author:nikan(859905874@qq.com)

@file: local_server.py

@time: 2018/8/1 上午2:49
"""

import time

import random
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth, HTTPDigestAuth, MultiAuth
from gevent.pywsgi import WSGIServer

from tests.config import TEST_PORT, USER

app = Flask(__name__)
basic_auth = HTTPBasicAuth()
digest_auth = HTTPDigestAuth()

auth = MultiAuth(digest_auth, basic_auth)
app.config['SECRET_KEY'] = 'secret'


@basic_auth.get_password
def get_pw(username):
    if username in USER['user']:
        return USER['password']
    else:
        from tests import test_benchs
        test_benchs.local_server_exception.append('No auth')
        return None


@digest_auth.get_password
def get_pw(username):
    if username in USER['user']:
        return USER['password']
    else:
        from tests import test_benchs
        test_benchs.local_server_exception.append('No auth')
        return None


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/test_auth')
@auth.login_required
def auth_test():
    print('hahahashabi')
    return 'Auth OK!'


@app.route('/random_sleep')
def hello_sleep():
    sleep_second = random.randint(2, 3)
    time.sleep(sleep_second)
    return 'Hello, Sleep for {}s'.format(sleep_second)


@app.route('/test_get')
def get():
    return 'i love h'


@app.route('/test_get2')
def get2():
    return 'i love h'


@app.route('/test_post_data', methods=['POST'])
def post_data():
    data = request.get_data()
    if not data:
        from tests import test_benchs
        test_benchs.local_server_exception.append('No data')
    return 'test_post_data {}'.format(data)


@app.route('/test_post_json', methods=['POST'])
def post_json():
    json = request.get_json()
    if not json:
        from tests import test_benchs
        test_benchs.local_server_exception.append('No json')
    return 'test_post_json {}'.format(json)


# @app.route('/test_post_file', methods=['POST'])
# def test_post_file():
#     file = request.files
#     return 'test_post_file'

@app.route('/test_put_data', methods=['PUT'])
def put_data():
    return 'test_put_data'


@app.route('/test_delete', methods=['DELETE'])
def delete():
    return 'test_delete'


def run():
    print('Testing server is serving on {}...'.format(TEST_PORT))
    WSGIServer(('localhost', TEST_PORT), app).serve_forever()


if __name__ == '__main__':
    run()
