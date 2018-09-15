#!/usr/bin/python
#-*- coding:utf-8 -*-
import commands,os,re,argparse,base64
import ConfigParser,subprocess 
import socket
import struct
import time
import sys

# If you're using an old version of python that don't have json available,
# you can use simplejson instead: https://simplejson.readthedocs.org/en/latest/
#import simplejson as json
import json


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

def get_route():#获取路由信息
    result=commands.getstatusoutput('/sbin/route -n')
    result_list=result[1].split('\n')
    return result_list[2:]

def get_mount():
    result=commands.getstatusoutput('/bin/mount -l -t nfs,none,nfs4')
    result_list=result[1].split('\n')
    return result_list

def get_crontab():
    result=commands.getstatusoutput('/bin/crontab -l')
    result_list=result[1].split('\n')
    return result_list

def get_network():
    route_list=[]
    for line in open('/proc/net/dev', 'r'):
        if re.match('.*:', line):
            data = re.findall('(.*):',line)
            match_route=re.sub(' ','',data[0])
            route_list.append(match_route)
    return route_list

def get_route_file(network_card_list):
    network_list=os.listdir('/etc/sysconfig/network-scripts') 
    exist_network_dic={}
    for every_network_card_name in network_card_list:
        if 'route-'+every_network_card_name in network_list:
            with open('/etc/sysconfig/network-scripts/route-'+every_network_card_name,'r') as fr_network:
                network_content=fr_network.read()
            exist_network_dic[every_network_card_name]=network_content
    return exist_network_dic

def judge_nas_way(judge_arg,now_content,raw_content):
    if judge_arg:
        for every_line in now_content:
            if not every_line in raw_content:
                return 1
        for every_line in raw_content:
            if not every_line in now_content:
                return 1
    return 0

def socket_send(judge_value):
    if judge_value==1:
        zabbix = pyZabbixSender(server=args.server_host, port=int(args.port))
        zabbix.addData(host=args.host_name, key='route_status', value="1")
        zabbix.printData()
        results = zabbix.sendData()
        for res in results:
            print "Result: %s -> %s" % (str(res[0]), res[1])
        zabbix.clearData()

def reset_single(cmd_arg,section_name,column_name,reset_value):
    if cmd_arg:
        conf = ConfigParser.ConfigParser()
        conf.read('/tmp/snapshot.log')
        conf.set(section_name,column_name,reset_value)
        with open('/tmp/snapshot.log','w') as log_write:
            conf.write(log_write)
class TimeoutError(Exception):
    pass

def command(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    return p.stdout.read()

def mount_nfs(mount_line):
    single_mount_list=mount_line.split(' ')
    single_mount_list.remove('type') 
    single_mount_list.remove('on')
    if 'bind' in single_mount_list[3]:
        all_args_str=re.findall('\((.*)\)',single_mount_list[3])
        all_args_str=re.sub('bind','',all_args_str[0])
        all_args_str=re.sub('\,port=\d+\,','',all_args_str)
        mount_cmd='mount --bind '+single_mount_list[0]+' '+single_mount_list[1]+' -o '+all_args_str
    elif single_mount_list[2]=='nfs' or 'nfs4':
        all_args_str=re.findall('\((.*)\)',single_mount_list[3])
        all_args_str=re.sub('port=\d+\,','',all_args_str[0])
        mount_cmd='mount '+single_mount_list[0]+' '+single_mount_list[1]+' -o '+all_args_str
    print mount_cmd
    command(cmd=mount_cmd,timeout=30)
def umount_nfs(mount_line):
    single_mount_list=mount_line.split(' ')
    single_mount_list.remove('type')
    single_mount_list.remove('on')
    mount_cmd='umount -v '+single_mount_list[1]
    command(cmd=mount_cmd,timeout=30)
'''
z = pyZabbixSender(server="103.210.236.8", port=10051)
z.addData(host="39.106.182.145", key="test_trap_1", value="12")
z.printData()
results = z.sendData()
for r in results:
    print "Result: %s -> %s" % (str(r[0]), r[1])
z.clearData()
'''

parser=argparse.ArgumentParser()
parser.add_argument("-r","--reset",action="store_true",help="reset snapshot")
parser.add_argument("-m","--mount",action="store_true",help="check mount")
parser.add_argument("-c","--crontab",action="store_true",help="check crontab")
parser.add_argument("-n","--route",action="store_true",help="check route")
parser.add_argument("-p","--port",help="server port")
parser.add_argument("-s","--server_host",help="server host ip")
parser.add_argument("-l","--host_name",help="local host name")
parser.add_argument("-a","--alter_item",action="store_true",help="repair item")
#parser.add_argument("-k","--key",action="store_true",help="key_name")
#parser.add_argument("-v","--key_value",action="store_true",help="key value")
args=parser.parse_args()
if args.reset:#如果有-r或--reset则重置
    route_info=base64.b64encode('\n'.join(get_route()))
    mount_info=base64.b64encode('\n'.join(get_mount()))
    crontab_info=base64.b64encode('\n'.join(get_crontab()))
    if not os.path.exists('/tmp/snapshot.log'):
        conf = ConfigParser.ConfigParser()
        conf.add_section("route")
        conf.add_section('mount')
        conf.add_section('crontab')
        conf.set('route', 'route_value',route_info)
        conf.set('mount','mount_value',mount_info)
        conf.set('crontab','crontab_value',crontab_info)
        network_list=get_network()
        route_dic=get_route_file(network_card_list=network_list)
        print route_dic
        for every_network,network_file_content in route_dic.items():
            conf.set('route',every_network,base64.b64encode(network_file_content))
        with open('/tmp/snapshot.log','w+') as write_log:
            conf.write(write_log)
        sys.exit()
    if args.route:
        reset_single(cmd_arg=args.route,section_name='route',column_name='route_value',reset_value=route_info)
        network_list=get_network()
        route_dic=get_route_file(network_card_list=network_list)
        for every_network,network_file_content in route_dic.items():
            reset_single(cmd_arg=args.route,section_name='route',column_name=every_network,reset_value=base64.b64encode(network_file_content))
    reset_single(cmd_arg=args.mount,section_name='mount',column_name='mount_value',reset_value=mount_info)
    reset_single(cmd_arg=args.crontab,section_name='crontab',column_name='crontab_value',reset_value=crontab_info)
    sys.exit()
elif args.alter_item:
    if args.mount:
        conf = ConfigParser.ConfigParser()
        conf.read('/tmp/snapshot.log')
        mount_value=conf.get('mount','mount_value')
        mount_content=base64.b64decode(mount_value)
        mount_list=mount_content.split('\n')
        now_mount_list=get_mount()
        for every_raw_mount_point in mount_list:
            if not every_raw_mount_point in now_mount_list:
                try:
                    mount_nfs(mount_line=every_raw_mount_point)
                except:
                    print every_raw_mount_point+' mount failed'
        for every_umount_point in now_mount_list:
            if not every_umount_point in mount_list:
                try:
                    umount_nfs(mount_line=every_umount_point)
                except:
                    print every_umount_point+' umount failed'
    elif args.route:
        route_conf=ConfigParser.ConfigParser()
        route_conf.read('/tmp/snapshot.log') 
        '''
        先恢复静态路由文件内容,再和临时路由做对比,添加路由
        '''
       
        for every_raw_network in route_conf.options('route'):
            if not every_raw_network=='route_value':
                #判断路由文件是否存在
                if os.path.exists('/etc/sysconfig/network-scripts/route-'+every_raw_network):
                    over_write_content=route_conf.get('route',every_raw_network)
                    print 'alter route file '+over_write_content
                    #覆盖路由文件
                    with open('/etc/sysconfig/network-scripts/route-'+every_raw_network,'w') as now_network_wr:
                        now_network_wr.write(base64.b64decode(over_write_content))
        #重启网卡
        command(cmd='service network restart', timeout=60)
        #获取临时路由
        '''
        now_route_content=command(cmd='route -n',timeout=60)
        route_value=base64.b64decode(conf.get('route','route_value'))
        if now_route_content!=route_value:
            now_route_list=now_route_content.split('\n')
            raw_route_list=route_value.split('\n')
        '''    
    elif args.crontab:
        crontab_conf=ConfigParser.ConfigParser()
        crontab_conf.read('/tmp/snapshot.log')
        crontab_root=crontab_conf.get('crontab','crontab_value')
        with open('/var/spool/cron/root','w') as crontab_option:
            crontab_content=crontab_option.write(base64.b64decode(crontab_root))
        

    sys.exit()

conf=ConfigParser.ConfigParser()
conf.read('/tmp/snapshot.log')
route_content=conf.get('route','route_value')
mount_content=conf.get('mount','mount_value')
crontab_content=conf.get('crontab','crontab_value')
route_content_list=base64.b64decode(route_content)
mount_content_list=base64.b64decode(mount_content)
crontab_content_list=base64.b64decode(crontab_content)
now_route_content,now_mount_content,now_crontab_content=get_route(),get_mount(),get_crontab()
route_judge_value=judge_nas_way(judge_arg=args.route,now_content=now_route_content,raw_content=route_content_list)
mount_judge_value=judge_nas_way(judge_arg=args.mount,now_content=now_mount_content,raw_content=mount_content_list)
crontab_judge_value=judge_nas_way(judge_arg=args.crontab,now_content=now_crontab_content,raw_content=crontab_content_list)
[socket_send(judge_value=judge_value) for judge_value in [route_judge_value,mount_judge_value,crontab_judge_value]]
