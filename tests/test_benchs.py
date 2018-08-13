#!/usr/bin/env python
# encoding: utf-8
"""

@author:nikan(859905874@qq.com)

@file: test_benchs.py

@time: 2018/8/5 下午5:09
"""
import gevent
from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from bench import start_bench
from tests.config import USER
from tests.local_server import run

local_server_exception = []


def setup_module(module):
    """ setup any state specific to the execution of the given module."""
    gevent.spawn(run)


def test_bench_get():
    def test_get():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/test_get', 'http://127.0.0.1:22222/test_get2']
        timeout = None
        method = 'GET'
        keep_alive = False
        auth = None
        data = None
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    def test_timeout():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/random_sleep']
        timeout = 1
        method = 'GET'
        keep_alive = False
        auth = None
        data = None
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    global local_server_exception
    local_server_exception = []
    test_get()
    assert local_server_exception == []
    test_timeout()


def test_bench_post():
    def test_post_data():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/test_post_data']
        timeout = None
        method = 'POST'
        keep_alive = False
        auth = None
        data = 'test'
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    def test_post_json():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/test_post_data']
        timeout = None
        method = 'POST'
        keep_alive = False
        auth = None
        data = None
        json = {'test': 'test_json'}
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    global local_server_exception
    local_server_exception = []
    test_post_data()
    test_post_json()
    assert local_server_exception == []


def test_bench_put():
    def test_put_data():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/test_put_data']
        timeout = None
        method = 'PUT'
        keep_alive = False
        auth = None
        data = None
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    global local_server_exception
    local_server_exception = []
    test_put_data()
    assert local_server_exception == []


def test_bench_delete():
    def test_delete():
        concurrency = 10
        total_requests = 10
        urls = ['http://127.0.0.1:22222/test_delete']
        timeout = None
        method = 'DELETE'
        keep_alive = False
        auth = None
        data = None
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    global local_server_exception
    local_server_exception = []
    test_delete()
    assert local_server_exception == []


def test_bench_auth():
    def test_auth(auth):
        concurrency = 1
        total_requests = 1
        urls = ['http://127.0.0.1:22222/test_auth']
        timeout = None
        method = 'GET'
        keep_alive = False
        auth = auth
        data = None
        json = None
        headers = None
        cookies = None
        start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies)

    global local_server_exception

    local_server_exception = []
    auth = HTTPBasicAuth(USER['user'], USER['password'])
    test_auth(auth)

    assert local_server_exception == []
    auth = HTTPBasicAuth('asdasd', USER['password'])
    test_auth(auth)
    assert local_server_exception != []

    local_server_exception = []
    auth = HTTPDigestAuth('nasd', USER['password'])
    test_auth(auth)
    assert local_server_exception != []

    local_server_exception = []
    auth = HTTPDigestAuth(USER['user'], USER['password'])
    test_auth(auth)
    assert local_server_exception == []
