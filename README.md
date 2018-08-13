# 一款基于命令行的网站压测小工具Webenchmark
+ 支持HTTP GET, POST, PUT, DELETE, HEAD操作

+ 支持长连接

+ 支持多个URL混合测试

+ 支持超时时间设置

+ 支持身份认证， Basic Auth和Digest Auth。

  

##用法说明：
```shell
# 对单个请求进行get测试
webenchmark -c 10 -n 30 https://www.baidu.com
# 长连接
webenchmark -c 10 -n 30 -k True https://www.baidu.com
# 对多个URL进行混合
webenchmark -c 10 -n 30 https://www.baidu.com http://example.com/ https://www.taobao.com/
# 
# basic auth
webenchmark -a basic:test_user:test_password http://example.com/
# digest auth
webenchmark -a digest:test_user:test_passtest_password http://example.com/


```

