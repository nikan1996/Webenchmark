#!/usr/bin/env python
# encoding: utf-8
"""
pure python http benchmark client
@author:nikan(859905874@qq.com)

@file: bench.py

@time: 2018/7/31 上午10:11
"""

import argparse
import sys
import time
from itertools import cycle
from typing import Text
from urllib.parse import urlparse

import gevent
import gevent.pool
from gevent.lock import Semaphore
from gevent.monkey import patch_all

patch_all()
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from requests.exceptions import ConnectionError
import urllib3

urllib3.disable_warnings()

auth_class = {'DIGEST': HTTPDigestAuth, 'BASIC': HTTPBasicAuth}


def mean(numbers: list):
    return float(sum(numbers)) / max(len(numbers), 1)


class URLContainer:
    """每个url都有3个时间connect_cost_time, process_cost_time, total_cost_time"""
    keep_alive_session = requests.session()

    def __init__(self, url):
        self.url = url
        self.start_time = None
        self.connect_time = None
        self.read_time = None
        self.end_time = None

        self.content_length = None
        self.status_code = None
        self.error = False

    @property
    def total_cost_time(self):
        return self.end_time - self.start_time

    @property
    def connect_cost_time(self):
        return self.connect_time - self.start_time

    @property
    def process_cost_time(self):
        return self.end_time - self.read_time

    def request(self, *, method='get', timeout=None, params=None, data=None, json=None, files=None, proxies=None,
                auth=None, verify=False, keep_alive=False, headers=None, cookies=None):
        """
        A request is divided into two parts:
        One for setting up connection.
        Another for receiving response body.
        :param method: get, post, put, delete.
        :param timeout: default None means infinity.
        :param params: parameters
        :param data: Content-Type: application/x-www-form-urlencoded
        :param json:  Content-Type: application/body
        :param files: Content-Type: `multipart/form-data`
        :param proxies: support http proxies and socks5 proxies
        :param auth: support basic Auth and digest Auth.
        This parameter format is "auth_method:auth_user:auth_password"
        So spilit it to three variable.
        :param verify: True when required https.Default False.
        :return: None
        """
        try:
            session = self.keep_alive_session if keep_alive else requests.session()
            self.start_time = time.time()
            r = session.request(method=method, url=self.url, params=params, data=data, files=files, proxies=proxies,
                                json=json, stream=True, timeout=timeout, verify=verify, auth=auth, headers=headers,
                                cookies=cookies)
            self.status_code = r.status_code

            self.connect_time = time.time()
            # Semaphore防止 content过大时时间计算不准确
            with Semaphore(1):
                self.read_time = time.time()
                _ = r.content
                self.end_time = time.time()
                self.content_length = len(_)
        except ConnectionError:
            print('网络连接失败， 请检查网络是否连通，或者网址是否有效')
            exit(0)
        except Exception as e:
            self.error = True
            if not self.connect_time:
                self.connect_time = time.time()

            if not self.read_time:
                self.read_time = time.time()

            if not self.end_time:
                self.end_time = time.time()


class Benchmark:
    def __init__(self, *, concurrency: int, total_requests: int, urls: list, timeout: int = None, method: Text = 'get',
                 keep_alive: bool = False, auth: Text = None, data: Text = None, json: dict = None,
                 headers: dict = None, cookies: dict = None):
        self.concurrency = concurrency
        self.total_requests = total_requests
        self.timeout = timeout
        self.method = method
        self.keep_alive = keep_alive
        self.auth = auth
        self.urls = urls
        self.data = data
        self.json = json
        self.headers = headers
        self.cookies = cookies

        self.url_containers = []
        self.pool = gevent.pool.Pool(self.concurrency)

    def start(self):
        request_number = 0
        for url in cycle(self.urls):
            if request_number < self.total_requests:
                container = URLContainer(url)
                self.url_containers.append(container)
                self.pool.spawn(container.request, method=self.method, timeout=self.timeout, keep_alive=self.keep_alive,
                                auth=self.auth, data=self.data, json=self.json, headers=self.headers,
                                cookies=self.cookies)
                request_number += 1
            else:
                break
        self.pool.join(raise_error=False)

    # def get_request_time_
    # 获取（）连接时间、处理时间、总时间）的最短时间，平均时间，中位时间和最长时间
    # TODO: nikan(859905874@qq.com)
    # 这可能不是必要的指标，但是确实能知道latency的瓶颈在哪里
    # 不过我觉得这并不重要，这些指标是可以通过外部分析获得的。

    def get_request_time_distribution(self, total_times: list):
        """得到不同百分比的耗时状态"""
        sorted_times = sorted(total_times)
        zero_percent = sorted_times[0]
        ten_percent = sorted_times[int(len(sorted_times) * 0.1) - 1]
        fifty_percent = sorted_times[int(len(sorted_times) * 0.5) - 1]
        ninety_percent = sorted_times[int(len(sorted_times) * 0.9) - 1]
        ninety_five_percent = sorted_times[int(len(sorted_times) * 0.95) - 1]
        one_hundred_percent = sorted_times[-1]
        request_time_distribution_string = '\n'.join(
            ['请求时间分布（秒）',
             '{:5}{:.3f}'.format('0%（最快）', zero_percent),
             '{:5}{:.3f}'.format('10%', ten_percent),
             '{:5}{:.3f}'.format('50%', fifty_percent),
             '{:5}{:.3f}'.format('90%', ninety_percent),
             '{:5}{:.3f}'.format('95%', ninety_five_percent),
             '{:5}{:.3f}'.format('100%（最慢）', one_hundred_percent)])
        return request_time_distribution_string

    def print_result(self):
        print('压测结果========================')
        connect_times = []
        process_times = []
        total_times = []
        non_200_responses = 0
        failed_responses = 0
        for container in self.url_containers:
            connect_times.append(container.connect_cost_time)
            process_times.append(container.process_cost_time)
            total_times.append(container.total_cost_time)
            if container.status_code != 200:
                non_200_responses += 1
            if container.error:
                failed_responses += 1
        total_time_mean = mean(total_times)
        formatted_string_one = '\n'.join(['{:20s}{}'.format('并发数：', self.concurrency),
                                          '{:20s}{}'.format('请求数：', self.total_requests),
                                          '{:20s}{}'.format('失败数：', failed_responses),
                                          '{:19s}{}'.format('非200请求数：', non_200_responses),
                                          '{:14s}{:.3f}'.format('平均请求时长（秒）：', total_time_mean),
                                          ])
        request_time_distribution_string = self.get_request_time_distribution(total_times)
        print(formatted_string_one)
        print('============================')
        print(request_time_distribution_string)
        return


def start_bench(concurrency, total_requests, urls, timeout, method, keep_alive, auth, data, json, headers, cookies):
    bench_instance = Benchmark(concurrency=concurrency, total_requests=total_requests, urls=urls,
                               timeout=timeout, method=method, keep_alive=keep_alive, auth=auth, data=data, json=json,
                               headers=headers, cookies=cookies)
    bench_instance.start()
    bench_instance.print_result()


def parse_args(shell_args):
    parser = argparse.ArgumentParser(prog='webenchmark', description='HTTP压测小工具🎂 Author: Ni Kan(859905874@qq.com)')
    parser.add_argument('-c', '--concurrency', dest='concurrency', type=int, default=1, help='并发数')
    parser.add_argument('-n', '--number', dest='total_requests', type=int, help='请求数')
    parser.add_argument('-m', '--method', dest='method', default='get', help='请求方式{GET,POST,DELETE,PUT,HEAD,OPTIONS}')
    parser.add_argument('-f', '--file', dest='file_path', help='文件路径')
    parser.add_argument('-d', '--data', dest='data', help='post/put 数据')
    parser.add_argument('-j', '--json', dest='json', help='post/put json 数据')
    parser.add_argument('-t', '--timeout', dest='timeout', type=int, help='超时时间')
    parser.add_argument('-k', '--keep-alive', dest='keep_alive', default=False, action='store_true', help='是否启用长连接')
    parser.add_argument('-a', '--auth', dest='auth', help='身份认证 eg. basic:user:password')
    parser.add_argument('-H', '--headers', dest='headers', help='请求头')
    parser.add_argument('-C', '--cookies', dest='cookies', type=str, help='请求cookies')
    parser.add_argument('urls', nargs='*', help='请求URL(一个或多个)')

    parser.add_argument('--version', action='version', version='%(prog)s {}'.format('1.0'), help="当前版本")
    if len(sys.argv) == 1:
        parser.print_help()
        return
    else:
        if shell_args is None:
            shell_args = sys.argv[1:]
        args = parser.parse_args(shell_args)

        urls = args.urls
        if args.file_path:
            with open(args.file_path) as open_file:
                urls = [_.strip() for _ in open_file]

        def uri_validator(x):
            try:
                result = urlparse(x)
                return result.scheme and result.netloc
            except:
                return False

        for url in urls:
            if not uri_validator(url):
                print('URL校验失败，请检查你的URL是否有效')
                return
        concurrency = args.concurrency
        total_requests = args.total_requests or len(urls)
        timeout = args.timeout
        method = args.method.upper()
        keep_alive = args.keep_alive
        auth_str = args.auth
        auth = None
        if auth_str:
            (auth_method, auth_user, auth_password) = auth_str.split(':')
            auth = auth_class[auth_method.upper()](auth_user, auth_password)

        data = args.data
        _json = eval(args.json) if args.json else None
        headers = eval(args.headers) if args.headers else None
        cookies = eval(args.cookies) if args.cookies else None
        return {
            'concurrency': concurrency,
            'total_requests': total_requests,
            'urls': urls,
            'timeout': timeout,
            'method': method,
            'keep_alive': keep_alive,
            'auth': auth,
            'data': data,
            'json': _json,
            'headers': headers,
            'cookies': cookies
        }


def run():
    args = None
    # try:
    args = parse_args(sys.argv[1:])
    # except Exception:
    #     print('请检查命令是否正确')
    if args:
        print('正在进行压测.....')
        start_bench(concurrency=args['concurrency'], total_requests=args['total_requests'], urls=args['urls'],
                    timeout=args['timeout'], method=args['method'], keep_alive=args['keep_alive'], auth=args['auth'],
                    data=args['data'], json=args['json'],
                    headers=args['headers'], cookies=args['cookies'])


if __name__ == '__main__':
    run()
