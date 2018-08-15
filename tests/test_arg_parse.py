#!/usr/bin/env python
# encoding: utf-8
"""

@author:nikan(859905874@qq.com)

@file: test_arg_parse.py

@time: 2018/8/13 下午2:56
"""
from bench import parse_args


def test_parse_args():
    command = "http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 1, 'total_requests': 1, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-k http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 1, 'total_requests': 1, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': True, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}


    command = "-c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-m POST -c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'POST',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-m POST -d test -c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'POST',
     'keep_alive': False, 'auth': None, 'data': 'test', 'json': None, 'headers': None, 'cookies': None}

    command = "-m POST -j {'test':'test_json'} -c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'POST',
     'keep_alive': False, 'auth': None, 'data': None, 'json': {'test':'test_json'}, 'headers': None, 'cookies': None}


    command = "-m PUT -c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'PUT',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}


    command = "-m DELETE -c 10 -n 100 http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 10, 'total_requests': 100, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'DELETE',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-a Basic:nikan:wrong_pass http://127.0.0.1:5000"
    args = parse_args(command.split())
    from requests.auth import HTTPBasicAuth
    assert args == {'concurrency': 1, 'total_requests': 1, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': False, 'auth': HTTPBasicAuth('nikan', 'wrong_pass'), 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-a Digest:nikan:wrong_pass http://127.0.0.1:5000"
    args = parse_args(command.split())
    from requests.auth import HTTPDigestAuth
    assert args == {'concurrency': 1, 'total_requests': 1, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': False, 'auth': HTTPDigestAuth('nikan', 'wrong_pass'), 'data': None, 'json': None, 'headers': None, 'cookies': None}

    command = "-H {'user-agent':'hahah'} -C {'a':'1'} http://127.0.0.1:5000"
    args = parse_args(command.split())
    assert args == {'concurrency': 1, 'total_requests': 1, 'urls': ['http://127.0.0.1:5000'], 'timeout': None, 'method': 'GET',
     'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': {'user-agent':'hahah'}, 'cookies': {'a':'1'}}

    command = "-f correct_file"
    args = parse_args(command.split())
    assert args == {'concurrency': 1, 'total_requests': 5, 'urls': ['http://example.com/', 'http://example.com/1', 'http://example.com/2', 'http://example.com/3', 'http://example.com/4'], 'timeout': None, 'method': 'GET', 'keep_alive': False, 'auth': None, 'data': None, 'json': None, 'headers': None, 'cookies': None}
