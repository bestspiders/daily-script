#-*- coding:utf-8 -*-
#此脚本目的是收集java栈信息jmap -heap pid  、  jmap -histo:live pid 、jstat -gcutil pid
import subprocess,os,re,datetime,time
all_process=os.listdir('/proc')
process_list=[]
#获取进程id
for every_proc_file in all_process:
    if re.findall('^\d+$',every_proc_file):
        process_list.append(every_proc_file)
#存储tomcat启动命令，进程
start_list,kill_list=[],[]
for every_proc_number in process_list:
    cmd_line_path='/proc/'+every_proc_number+'/cmdline'
    if os.path.exists(cmd_line_path):
        cmd_line_options=open(cmd_line_path,'r')
        cmd_line_content=cmd_line_options.read()
        cmd_line_options.close()
        #判读是否为java
        if re.findall('bootstrap\.jar',cmd_line_content) and re.findall('catalina',cmd_line_content): 
            cmd_list=cmd_line_content.split('\0')
            #deal_cmd_list=[]
            for every_cmd in cmd_list:
                if every_cmd:
                    start_list.append(every_cmd)
            #start_line=' '.join(cmd_list)
            #start_list.append(deal_cmd_list)
            kill_list.append(every_proc_number)
jmap_path=re.sub('/jre/bin/java','/bin/jmap',start_list[0])
jstat_path=re.sub('/jre/bin/java','/bin/jstat',start_list[0])
#获取当日时间
today_time=time.localtime()
today=str(time.strftime('%Y%m%d',today_time))
detail_time=str(time.strftime('%Y%m%d%H',today_time))
print(detail_time)
java_live=subprocess.Popen(jmap_path+' -histo:live '+kill_list[0],stdout=subprocess.PIPE,shell=True).stdout.read()
if java_live:
    if not os.path.exists('/tmp/'+today+'live'):
        os.mkdir('/tmp/'+today+'live')
    wr_options=open(os.path.join('/tmp',today+'live',detail_time+'.txt'),'w')
    wr_options.write(java_live)
    wr_options.close()
print(java_live)