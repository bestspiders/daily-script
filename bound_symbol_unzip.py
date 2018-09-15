#-*- coding:utf-8 -*-
import os,tarfile,re,time,datetime,shutil
import argparse
parser=argparse.ArgumentParser()
parser.add_argument("-t","--tar",help="gzip time")
parser.add_argument("-d","--delete",help="raw logs delete time")
parser.add_argument("-p","--path",help="logs path")
parser.add_argument("-l","--local_tar_del",help="tar package delete")
args=parser.parse_args()
log_path=args.path
all_file=os.listdir(log_path)
#today_time=time.strftime("%Y-%m-%d")
today=datetime.date.today()
time_delete=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(int(args.delete),365)]
time_tar=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(1,int(args.tar)+1)]
time_tar_delete=[(today-datetime.timedelta(days=add_time)).strftime('%y-%m-%d') for add_time in range(int(args.local_tar_del),365)]
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
