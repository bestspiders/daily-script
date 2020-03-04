#-*- coding:utf-8 -*-
from multiprocessing import Pool
import os,time,re
import optparse
def deal_mam(src_path,dest_path,record_path):
    now_time=str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    with open(record_path,'w') as record_start:
        record_start.write(now_time+'\n')
#    dest_path=re.sub("/nas/mam","/nas/new_mam",src_path)
    print("cp -ur "+src_path+" "+dest_path)
    os.system("cp -ur "+src_path+" "+dest_path)
    end_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(record_path,'a') as record_end:
        record_end.write(end_time+'\n')
if __name__ == '__main__':
    parser=optparse.OptionParser()
    #复制根目录
    parser.add_option("-p","--path",dest="path",help="copy root path")
    #粘贴根目录
    parser.add_option("-d","--dest",dest="dest_path",help="dest root path")
    #日志记录根目录
    parser.add_option("-l","--log",dest="log_path",help="log root path")
    #范围
    parser.add_option("-n","--number",dest="number",help="number interval")
    #进程数
    parser.add_option("-c","--create_process",dest="create_process",help="create process number")
    options,args=parser.parse_args()
    now_number=0
    #判断目标拷贝目录是否存在
    if not os.path.exists(options.dest_path):
        os.makedirs(options.dest_path)
    #判断日志目录是否存在
    if options.log_path:
        if not os.path.exists(options.log_path):
            os.makedirs(options.log_path)
    else:
        print(u"请输入保存日志地址")
        os._exit()
    if not os.path.exists(os.path.join(options.log_path,os.path.basename(options.path))):
        os.mkdir(os.path.join(options.log_path,os.path.basename(options.path)))
    #获取拷贝的目录
    copy_list=[]
    if options.number:
        interval_list=options.number.split(',')
        for every_dir in os.listdir(options.path):
            if now_number>=int(interval_list[0]) and now_number<int(interval_list[1]):
                copy_list.append(every_dir)
            now_number+=1
    else:
        for every_dir in os.listdir(options.path):
            copy_list.append(every_dir)
    if options.create_process:
        po=Pool(int(options.create_process))
    else:
        po=Pool(8)
    for every_dir in copy_list:
        #创建次级日志目录
        if not os.path.exists(os.path.join(options.log_path,os.path.basename(options.path))):
            os.mkdir(os.path.join(options.log_path,os.path.basename(options.path)))
        po.apply_async(deal_mam,(os.path.join(options.path,every_dir),options.dest_path,os.path.join(os.path.join(options.log_path,os.path.basename(options.path),every_dir)),))
        #deal_mam(os.path.join(options.path,every_dir),options.dest_path,os.path.join(os.path.join(options.log_path,os.path.basename(options.path),every_dir)))
    po.close()
    po.join()    