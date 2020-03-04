#-*- coding:utf-8 -*-
import paramiko,os,random,sys
from multiprocessing import Pool
import multiprocessing,time


def start_ftp(s,ip,host_port,user,pwd,src,dest,k):
	s.acquire()
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
	    client.connect(hostname=ip, port=host_port, username=user, password=pwd)
	except paramiko.ssh_exception.SSHException as alert_info:
	    print str(alert_info)
	sftp=client.open_sftp()
	global will_ip
	global line_k
	will_ip=ip
	line_k = k
	sftp.put(localpath=src,remotepath=dest,callback=progress_bar,confirm=True)
	sftp.close()
	file_open=open('temporary.txt','a+')
	file_open.write(ip+'   successful')
	file_open.close()
	s.release()
def progress_bar(transferred, toBeTransferred, suffix=''):
    # print "Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred)
    bar_len = 60
    filled_len = int(round(bar_len * transferred/float(toBeTransferred)))
    percents = round(100.0 * transferred/float(toBeTransferred), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    new_data='%s[%s] %s%s ...%s\n' % (will_ip,bar, percents, '%', suffix)
    f = open('temporary.txt','a+')
    f.write(new_data)
    f.close()
    # sys.stdout.write('%s[%s] %s%s ...%s\r' % (will_ip,bar, percents, '%', suffix))
    # sys.stdout.flush()
if __name__ == '__main__':
    s = multiprocessing.Semaphore(16)
    host_list=['']#主机列表
    host_port=22#端口
    user='root'#用户名
    pwd=''#密码
    src='G:\\zxczxc\\android-ndk-r14b-linux-x86_64.zip'#服务器文件存储位置
    dest='/root/android-ndk-r14b-linux-x86_64.zip'#目标机存储位置
    will_write=open('temporary.txt','wb')
    will_write.close()
    for k in range(0,len(host_list)):
        ip=host_list[k]
        result = multiprocessing.Process(target = start_ftp, args = (s,ip,host_port,user,pwd,src,dest,k))
        result.start()
    while True:
    	os.system('cls')
    	will_list=host_list
        new_file = open('temporary.txt','r')
        all_content= new_file.read()
        new_file.close()
        new_list=all_content.split('\n')
        success_list=[]
        for match_ip in host_list:
            ip_list=[]
            for every_line in new_list:
                if match_ip+'   successful' in every_line:
                    print match_ip+'   successful'
                    success_list.append(match_ip)
                    break
                elif match_ip in every_line:
                    ip_list.append(every_line)
            if ip_list:
                print ip_list[-1]
        if len(success_list)==len(host_list):
        	os.remove('temporary.txt')
        	sys.exit()
        time.sleep(3)