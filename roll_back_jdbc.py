#-*- coding:utf-8 -*-
import os,re,commands,subprocess,datetime,shutil
from xml.dom.minidom import parse
import xml.dom.minidom
#匹配的文件名字
deal_file=['jdbc.properties']
all_process=os.listdir('/proc')
process_list=[]
#获取进程id
for every_proc_file in all_process:
    if re.findall('^\d+$',every_proc_file):
        process_list.append(every_proc_file)
java_list,tomcat_path=[],[]
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
            tomcat_conf_path=re.findall('config\.file\=(.*/)logging\.properties',start_line)[0]
            if os.path.exists(os.path.join(tomcat_conf_path,'Catalina/localhost')):
                all_conf_list=[]
                for every_file in os.listdir(os.path.join(tomcat_conf_path,'Catalina/localhost')):
                    DOMTree = xml.dom.minidom.parse(os.path.join(tomcat_conf_path,'Catalina/localhost',every_file))
                    collection = DOMTree.documentElement
                    context_elt=collection.getAttributeNode("docBase")
                    if context_elt:
                        for node_root,node_dirs,node_files in os.walk(os.path.join(context_elt.nodeValue,'WEB-INF')):
                            for node_name in node_files:
                                if node_name in deal_file:
                                    java_list.append(os.path.join(node_root,node_name))
                tomcat_path.append(re.findall('config\.file\=(.*/)conf/logging\.properties',start_line)[0])
if not java_list:
    for every_tomcat_conf_path in tomcat_path:
        for root,dirs,files in os.walk(os.path.join(every_tomcat_conf_path,'webapps')):
            for file_name in files:
                if file_name in deal_file:
                    java_list.append(os.path.join(root,file_name))
for every_file_path in java_list:
    today_time=datetime.date.today()
    os.remove(every_file_path)
    shutil.copyfile(every_file_path+str(today_time),every_file_path)
    