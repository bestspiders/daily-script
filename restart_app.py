#-*- coding:utf-8 -*-
import os,re,commands,subprocess
all_process=os.listdir('/proc')
process_list=[]
#获取进程id
for every_proc_file in all_process:
    if re.findall('^\d+$',every_proc_file):
        process_list.append(every_proc_file)
start_list,kill_list,mid_app_list=[],[],[]
#遍历每个进程
for every_proc_number in process_list:
    cmd_line_path='/proc/'+every_proc_number+'/cmdline'
    if os.path.exists(cmd_line_path):
        cmd_line_options=open(cmd_line_path,'r')
        cmd_line_content=cmd_line_options.read()
        cmd_line_options.close()
        #判读是否为java
        if re.findall('bootstrap\.jar',cmd_line_content) and re.findall('catalina',cmd_line_content): 
            cmd_list=cmd_line_content.split('\0')
            deal_cmd_list=[]
            for every_cmd in cmd_list:
                if every_cmd:
                    deal_cmd_list.append(every_cmd)
            start_line=' '.join(cmd_list)
            start_list.append(deal_cmd_list)
            kill_list.append(every_proc_number)
        #判断是否为nginx
        elif re.findall('nginx',cmd_line_content):
            read_link=os.readlink('/proc/'+every_proc_number+'/exe')
            if not read_link in mid_app_list:
                mid_app_list.append(read_link)
            kill_list.append(every_proc_number)
        #判断是否为httpd
        elif re.findall('httpd',cmd_line_content):
            read_link=os.readlink('/proc/'+every_proc_number+'/exe')
            if not read_link+' -k start' in mid_app_list:
                mid_app_list.append(read_link+' -k start')
            kill_list.append(every_proc_number)
#stop httpd\nginx
for every_kill_number in kill_list:
    commands.getstatusoutput('kill -9 '+every_kill_number)
#start java
for every_start_cmd in start_list:
    print every_start_cmd
    subprocess.Popen(every_start_cmd,stdout=subprocess.PIPE,shell=False)#.communicate()
#start nginx\httpd
for every_mid_cmd in mid_app_list:
    print every_mid_cmd
    subprocess.Popen(every_mid_cmd,stdout=subprocess.PIPE,shell=True)