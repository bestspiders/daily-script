# bound_symbol_unzip.py <br>
**Python ENV:** 2.7+ <br>
针对日期格式清理:catalina.2018-09-21.out <br>
使用例子: <br>
```
python bound_symbol_unzip.py -t 3 -l 11 -p /usr/local/tomcat/logs -d 1
```

-t : 需要压缩的包天数（距离当天的时间）<br>
-l : 压缩包保留天数 (距离今天的时间) <br>
-d : 源文件保留天数 (距离今天的时间) <br>
-p : 压缩的目录 <br>

# old_bound_symbol_unzip.py <br>
**Python ENV:** 2.4+ <br>
同上，但是可以适用比较老的系统 <br>
参数同上解释<br>
# no_bound_symbol_unzip.py <br>
**Python ENV:** 2.7+ <br>
针对日期格式清理:catalina.20180921.out <br>
使用例子: <br>
```
python bound_symbol_unzip.py -t 3 -l 11 -p /usr/local/tomcat/logs -d 1
```
参数同上解释<br>

# send_log_zabbix.py <br>
针对tomcat当天日志关键词检查报警<br>

使用例子<br>
**使用前需要在/tmp/创建tomcat_check.log**
**写入输出化参数，如下**
```
[check_log]
last_line = 1
last_time = 2018-09-21
```
需要把1替换成需要从哪行检查
2018-09-21替换成当天日期
```
python send_log_zabbix.py -p /usr/local/tomcat/logs -t 300 -c jdbc,exception -k jdbc_key,exception_key -r 10051 -s 172.16.1.1 -l host_name
```
参数
```
  -h, --help            show this help message and exit
  -p PATH, --path=PATH  tomcat logs path
  -t WAIT_TIME, --wait_time=WAIT_TIME
                        loop wait time
  -c CHECK_LIST, --check_list=CHECK_LIST
                        check key list
  -k KEY_LIST, --key_list=KEY_LIST
                        server key list
  -r PORT, --port=PORT  server port
  -s SERVER_HOST, --server_host=SERVER_HOST
                        server host ip
  -l HOST_NAME, --host_name=HOST_NAME
                        local host name

```

# url_monitor.py <br>

env:Python2.4+<br>

针对指定url监控<br>

例子<br>

```
python /nas/nas_log/wangxin/url_monitor.py -r http://192.168.1.2:9999 -u http://222.222.222.222/index.html -k monitor_index -p 10051 -s 10.200.22.22 -l 0.0.0.0 -t 10
```

参数<br>

```
  -h, --help            show this help message and exit
  -u REQ_URL, --req_url=REQ_URL
                        requests url
  -t TIME_OUT, --time_out=TIME_OUT
                        load web time out
  -k KEY_LIST, --key_list=KEY_LIST
                        server key list
  -p PORT, --port=PORT  server port
  -s SERVER_HOST, --server_host=SERVER_HOST
                        server host ip
  -l HOST_NAME, --host_name=HOST_NAME
                        local host name
  -r PROXY_IP, --proxy_ip=PROXY_IP
                        proxy ip
```

