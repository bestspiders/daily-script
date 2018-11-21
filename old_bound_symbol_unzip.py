#-*- coding:utf-8 -*-
import os,tarfile,re,time,datetime,shutil
import optparse
parser=optparse.OptionParser()
parser.add_option("-t","--tar",dest="tar",help="gzip time")
parser.add_option("-d","--delete",dest="delete",help="raw logs delete time")
parser.add_option("-p","--path",dest="path",help="logs path")
parser.add_option("-l","--local_tar_del",dest="local_tar_del",help="tar package delete")
options,args=parser.parse_args()
log_path=options.path
all_file=os.listdir(log_path)
#today_time=time.strftime("%Y-%m-%d")
today=datetime.date.today()
time_delete=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(int(options.delete),720)]
time_tar=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(1,int(options.tar)+1)]
time_tar_delete=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(int(options.local_tar_del),720)]
for every_day in time_tar_delete:
    for every_file in all_file:
        if re.search(every_day,every_file):#如果文件路径含时间
            if re.search('\.tar\.gz',every_file):#如果文件路径包含.tar.gz
                os.remove(os.path.join(log_path,every_file))
for tar_day in time_tar:
    for every_file in all_file:
        if re.search(tar_day,every_file):
#           if  not os.path.exists(os.path.join(log_path,every_file+'.tar.gz')):
            if not re.search('\.tar\.gz',every_file):
                if not os.path.exists(os.path.join(log_path,every_file+'.tar.gz')):
                    print(os.path.join(log_path,every_file)+'.tar.gz')
                    t=tarfile.open(os.path.join(log_path,every_file)+'.tar.gz','w:gz')
                    t.add(os.path.join(log_path,every_file))
                    t.close()
for every_day in time_delete:
    for every_file in all_file:
        if re.search(every_day,every_file):#如果文件路径含时间
            if not re.search('\.tar\.gz',every_file):#如果文件路径不包含.tar.gz
                os.remove(os.path.join(log_path,every_file))
