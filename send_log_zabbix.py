#-*- coding:utf-8 -*-
import os,re,time,datetime,shutil,collections
import optparse,ConfigParser,subprocess,socket,struct,sys
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
                (retcode, retstring) = self.sendSingle(i['host'], i['key'], i['value'], i['clock'])
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

def zabbix_send_value(zabbix_host,zabbix_port,local_host,zabbix_single_key,send_value):
    zabbix = pyZabbixSender(server=zabbix_host, port=int(zabbix_port))
    zabbix.addData(host=local_host, key=zabbix_single_key, value=send_value)
    zabbix.printData()
    results = zabbix.sendData()
    for res in results:
        print "Result: %s -> %s" % (str(res[0]), res[1])
    zabbix.clearData()

parser=optparse.OptionParser()
parser.add_option("-p","--path",dest="path",help="tomcat logs path")
parser.add_option("-t","--wait_time",dest="wait_time",help="loop wait time")
parser.add_option("-c","--check_list",dest="check_list",help="check key list")
parser.add_option("-k","--key_list",dest="key_list",help="server key list")
parser.add_option("-r","--port",dest="port",help="server port")
parser.add_option("-s","--server_host",dest="server_host",help="server host ip")
parser.add_option("-l","--host_name",dest="host_name",help="local host name")
options,args=parser.parse_args()
tomcat_path,script_wait_time,script_check_list,zabbix_key,zabbix_port,zabbix_host,local_host=options.path,options.wait_time,options.check_list,options.key_list,options.port,options.server_host,options.host_name
while True:
    now_time=datetime.date.today().strftime('%Y-%m-%d')
    conf = ConfigParser.ConfigParser()
    conf.read('/tmp/tomcat_check.log')
    last_time=conf.get('check_log','last_time')
    last_line=conf.get('check_log','last_line')
    cal_dic,key_dic={},{}
    for every_key in script_check_list.split(','):
        cal_dic[every_key]=0
    check_key_list=script_check_list.split(',')
    zabbix_key_list=zabbix_key.split(',')
    for number in range(0,len(check_key_list)):
        key_dic[check_key_list[number]]=zabbix_key_list[number]
    if now_time==last_time:
        with open(tomcat_path+'/catalina.'+now_time+'.out') as rd_logs:
            logs_content=rd_logs.read()
        logs_lines=logs_content.split('\n')
        for line_number in range(int(last_line),len(logs_lines)):
            for every_key in script_check_list.split(','):
                if every_key in logs_lines[line_number]:
                    cal_dic[every_key]=cal_dic[every_key]+1
    else:
        with open(tomcat_path+'/catalina.'+last_time+'.out') as rd_logs:
            logs_content=rd_logs.read()
        logs_lines=logs_content.split('\n')
        for line_number in range(int(last_line),len(logs_lines)):
            for every_key in script_check_list.split(','):
                if every_key in logs_lines[line_number]:
                    cal_dic[every_key]=cal_dic[every_key]+1
        if os.path.exists(tomcat_path+'/catalina.'+now_time+'.out'):
            with open(tomcat_path+'/catalina.'+now_time+'.out') as now_rd_logs:
                now_logs_content=now_rd_logs.read()
            now_logs_lines=now_logs_content.split('\n')
            for now_line_number in range(0,len(now_logs_lines)):
                for every_key in script_check_list.split(','):
                    if every_key in now_logs_lines[now_line_number]:
                        cal_dic[every_key]=cal_dic[every_key]+1
    print cal_dic
    for every_key in cal_dic:
        zabbix_send_value(zabbix_host=zabbix_host,zabbix_port=zabbix_port,local_host=local_host,zabbix_single_key=key_dic[every_key],send_value=cal_dic[every_key])
    conf.set('check_log','last_time',now_time)
    conf.set('check_log','last_line',len(logs_lines))
    with open('/tmp/tomcat_check.log','w') as wr_conf:
        conf.write(wr_conf)
    time.sleep(int(script_wait_time))
