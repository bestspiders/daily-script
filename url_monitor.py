#!/usr/bin/env python

#
# Check if a website is loading and contains a nominated string.
#-*- coding:utf-8 -*-
# Usage:


import errno
import re,os
import sys
import time,datetime
import urllib,urllib2,optparse,ConfigParser,subprocess,socket,struct
try:
    import json
except:
    import simplejson as json


class pyZabbixSender:
    '''
    This class allows you to send data to a Zabbix server, using the same
    protocol used by the zabbix_server binary distributed by Zabbix.
    '''
    ZABBIX_SERVER = "127.0.0.1"
    ZABBIX_PORT   = 10051

    # Return codes when sending data:
    RC_OK            =   0  # Everything ok
    RC_ERR_FAIL_SEND =   1  # Error reported by zabbix when sending data
    RC_ERR_PARS_RESP =   2  # Error parsing server response
    RC_ERR_CONN      = 255  # Error talking to the server
    RC_ERR_INV_RESP  = 254  # Invalid response from server


    def __init__(self, server=ZABBIX_SERVER, port=ZABBIX_PORT, verbose=False):
        self.zserver = server
        self.zport   = port
        self.verbose = verbose
        self.timeout = 5         # Socket connection timeout.
        self.__data = []         # This is to store data to be sent later.


    def __str__(self):
        '''
        This allows you to obtain a string representation of the internal data
        '''
        return str(self.__data)


    def __createDataPoint(self, host, key, value, clock=None):
        '''
        Creates a dictionary using provided parameters, as needed for sending this data.
        '''
        obj = {
            'host': host,
            'key': key,
            'value': value,
        }
        if clock:
            obj['clock'] = clock
        return obj


    def __send(self, mydata):
        '''
        This is the method that actually sends the data to the zabbix server.
        '''
        socket.setdefaulttimeout(self.timeout)
        data_length = len(mydata)
        data_header = str(struct.pack('q', data_length))
        data_to_send = 'ZBXD\1' + str(data_header) + str(mydata)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.zserver, self.zport))
            sock.send(data_to_send)
        except Exception, err:
            err_message = u'Error talking to server: %s\n' %str(err)
            sys.stderr.write(err_message)
            return self.RC_ERR_CONN, err_message

        response_header = sock.recv(5)
        if not response_header == 'ZBXD\1':
            err_message = u'Invalid response from server. Malformed data?\n---\n%s\n---\n' % str(mydata)
            sys.stderr.write(err_message)
            return self.RC_ERR_INV_RESP, err_message

        response_data_header = sock.recv(8)
        response_data_header = response_data_header[:4]
        response_len = struct.unpack('i', response_data_header)[0]
        response_raw = sock.recv(response_len)
        sock.close()
        response = json.loads(response_raw)
        match = re.match('^.*failed.+?(\d+).*$', response['info'].lower() if 'info' in response else '')
        if match is None:
            err_message = u'Unable to parse server response - \n%s\n' % str(response)
            sys.stderr.write(err_message)
            return self.RC_ERR_PARS_RESP, response
        else:
            fails = int(match.group(1))
            if fails > 0:
                if self.verbose is True:
                    err_message = u'Failures reported by zabbix when sending:\n%s\n' % str(mydata)
                    sys.stderr.write(err_message)
                return self.RC_ERR_FAIL_SEND, response
        return self.RC_OK, response


    def addData(self, host, key, value, clock=None):
        obj = self.__createDataPoint(host, key, value, clock)
        self.__data.append(obj)


    def clearData(self):
        self.__data = []


    def getData(self):
        copy_of_data = []
        for data_point in self.__data:
            copy_of_data.append(data_point.copy())
        return copy_of_data


    def printData(self):
        for elem in self.__data:
            print str(elem)
        print 'Count: %d' % len(self.__data)


    def removeDataPoint(self, data_point):
        if data_point in self.__data:
            self.__data.remove(data_point)
            return True

        return False


    def sendData(self, packet_clock=None, max_data_per_conn=None):
        if not max_data_per_conn or max_data_per_conn > len(self.__data):
            max_data_per_conn = len(self.__data)

        responses = []
        i = 0
        while i*max_data_per_conn < len(self.__data):

            sender_data = {
                "request": "sender data",
                "data": [],
            }
            if packet_clock:
                sender_data['clock'] = packet_clock

            sender_data['data'] = self.__data[i*max_data_per_conn:(i+1)*max_data_per_conn]
            to_send = json.dumps(sender_data)

            response = self.__send(to_send)
            responses.append(response)
            i += 1

        return responses


    def sendDataOneByOne(self):
        retarray = []
        for i in self.__data:
            if 'clock' in i:
                (retcode, retstring) = self.sendSingle(i['host'], i['key'], i['value'], i['clo                                  ck'])
            else:
                (retcode, retstring) = self.sendSingle(i['host'], i['key'], i['value'])

            retarray.append((retcode, i))
        return retarray


    def sendSingle(self, host, key, value, clock=None):
        sender_data = {
            "request": "sender data",
            "data": [],
        }

        obj = self.__createDataPoint(host, key, value, clock)
        sender_data['data'].append(obj)
        to_send = json.dumps(sender_data)
        return self.__send(to_send)


    def sendSingleLikeProxy(self, host, key, value, clock=None, proxy=None):
        # Proxy was not specified, so we'll do a "normal" sendSingle operation
        if proxy is None:
            return sendSingle(host, key, value, clock)

        sender_data = {
            "request": "history data",
            "host": proxy,
            "data": [],
        }

        obj = self.__createDataPoint(host, key, value, clock)
        sender_data['data'].append(obj)
        to_send = json.dumps(sender_data)
        return self.__send(to_send)

class RedirctHandler(urllib2.HTTPRedirectHandler):
    """docstring for RedirctHandler"""
    def http_error_301(self, req, fp, code, msg, headers):
        pass
    def http_error_302(self, req, fp, code, msg, headers):
        pass

def getUnRedirectUrl(url,timeout=10):
    req = urllib2.Request(url)
    debug_handler = urllib2.HTTPHandler(debuglevel = 1)
    opener = urllib2.build_opener(debug_handler, RedirctHandler)
    html = None
    response = None
    try:
        response = opener.open(url,timeout=timeout)
        start = time.time()
        html = response.read()
        end=time.time()
        response.close()
        return round(end-start)
    except:
        if response:
            response.close()
        return round(timeout,2)

def zabbix_send_value(zabbix_host,zabbix_port,local_host,zabbix_single_key,send_value):
    zabbix = pyZabbixSender(server=zabbix_host, port=int(zabbix_port))
    zabbix.addData(host=local_host, key=zabbix_single_key, value=send_value)
    zabbix.printData()
    results = zabbix.sendData()
    for res in results:
        print "Result: %s -> %s" % (str(res[0]), res[1])
    zabbix.clearData()

#url = sys.argv[1]
#search = sys.argv[2]
parser=optparse.OptionParser()
parser.add_option("-u","--req_url",dest="req_url",help='requests url')
parser.add_option("-t","--time_out",dest="time_out",help="load web time out")
parser.add_option("-k","--key_list",dest="key_list",help="server key list")
parser.add_option("-p","--port",dest="port",help="server port")
parser.add_option("-s","--server_host",dest="server_host",help="server host ip")
parser.add_option("-l","--host_name",dest="host_name",help="local host name")
parser.add_option("-r","--proxy_ip",dest="proxy_ip",help="proxy ip")
options,args=parser.parse_args()

check_url,url_timeout=options.req_url,options.time_out
req_list=[]
if options.proxy_ip:
    proxy_support = urllib2.ProxyHandler({"http":options.proxy_ip,'https':options.proxy_ip})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
for number in range(0,10):
    try:
        req=urllib2.Request(check_url)
        f = urllib2.urlopen(req,timeout =int(url_timeout) )
        start = time.time()
        page = f.read()
        end = time.time()
        f.close()
        req_list.append(round(end-start,2))
    except:
        req_list.append(round(url_timeout,2))
avg_number=sum(req_list)/len(req_list)
print avg_number
zabbix_send_value(zabbix_host=options.server_host,zabbix_port=options.port,local_host=options.                                  host_name,zabbix_single_key=options.key_list,send_value=avg_number)