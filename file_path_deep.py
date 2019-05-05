#-*- coding:utf-8 -*-
import os,re
list_path='/home/ansible/wangxin/zabbix_agent_install/'
floor_number=2
all_path=[]
dir_list=[]
for root,dirs,files in os.walk(list_path):
    now_floor=0
    for file_name in files:
        full_path=os.path.join(root,file_name)
        deal_path=re.sub('^'+list_path,'',root)
        floor_list=deal_path.split('/')
        if len(floor_list)<=floor_number:
            all_path.append(full_path)
        else:
            now_floor=len(floor_list)
            break
    for every_dirs in dirs:
        dir_list.append(os.path.join(root,every_dirs))
    if now_floor>floor_number:
        break
for every_dir in dir_list:
    file_path_status=True
    for every_file_path in all_path:
        if re.findall('^'+every_dir+'/',every_file_path):
            file_path_status=False
            break
    if file_path_status:
        all_path.append(every_dir)
record_path=open('copy_path.log','w')
for every_path in all_path:
    
    record_path.write(every_path+'\n')
record_path.close()