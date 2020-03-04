#-*- coding:utf-8 -*-
import os,re,commands,shutil,subprocess,time
from xml.dom.minidom import parse
import xml.dom.minidom
#匹配的文件名字
deal_file=['jdbc.properties']
#匹配要替换的数据
raw_data=['\@172\.16\.74\.6\:1521\:ivideo','\@172\.16\.3\.107\:1521\:MV2']
#转门替换密码
pass_data=['VOMS\_2o1o','PORTAL\_SEARCH\_2o1o','PORTAL\_INTERACTION\_2o1o','oms\_movietv']
#替换的数据
sub_data=['@//10.125.161.34:1521/ivideo','@//10.125.161.34:1521/mv']
sub_pass=['Voms_Pwd_0828','Portal_Search_Pwd_0828','Portal_Interaction_Pwd_0828','Oms_Movietv_Pwd_0828']
all_process=os.listdir('/proc')
process_list=[]
#获取进程id
def get_WEB_INF(main_path_list):
    all_path=[]
    for every_path in main_path_list:
        now_listdir=os.listdir(every_path)
        for every_file in now_listdir:
            if os.path.isdir(os.path.join(every_path,every_file)):
                if every_file=='WEB-INF':
                    return os.path.join(every_path,every_file)
                all_path.append(os.path.join(every_path,every_file))
    return get_WEB_INF(all_path)
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
        jdbc_file_path=get_WEB_INF([os.path.join(every_tomcat_conf_path,'webapps')])
        for root,dirs,files in os.walk(jdbc_file_path):
            for file_name in files:
                if file_name in deal_file:
                    java_list.append(os.path.join(root,file_name))
for every_file_path in java_list:
    bak_path=every_file_path+str(time.time())
    print('src: '+every_file_path)
    print('dest:'+bak_path)
    shutil.copyfile(every_file_path,bak_path)
    file_options=open(every_file_path,'r') 
    file_line=[]
    for every_line in  file_options:
        line_status,pass_status,normal_status=-1,-1,-1
        for match_number in range(0,len(raw_data)):
            if re.findall(raw_data[match_number],every_line):
                line_status=match_number
                break
        for every_pass_number in range(0,len(pass_data)):
            if re.findall('pass',every_line) and re.findall(pass_data[every_pass_number],every_line):
                pass_status=every_pass_number
                break
        if line_status!=-1:
            line_data=re.sub(raw_data[line_status],sub_data[line_status],every_line)
            normal_status=0
            file_line.append(line_data)
        if pass_status!=-1:
            raw_pass_list=every_line.split('=')
            #line_data=re.sub(pass_data[pass_status],sub_pass[pass_status],every_line,-1)
            normal_status=0
            file_line.append(raw_pass_list[0]+'='+sub_pass[pass_status])
        if normal_status==-1:
            file_line.append(every_line)
    file_options.close()
    file_write_options=open(every_file_path,'w') 
    file_write_options.write(''.join(file_line))
    file_write_options.close()