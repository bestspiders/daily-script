#-*- coding:utf-8 -*-
import os,re,commands,time,shutil,optparse
parser=optparse.OptionParser()
parser.add_option("-p","--path",dest="path",help="alter path")
parser.add_option("-s","--ssh",dest="ssh",action="store_true",help="ssh alter")
options,args=parser.parse_args()
search_path=options.path
file_list=os.listdir(search_path)
if search_path:
    for every_file in file_list:
        if re.findall('nginx',every_file):#判断是否包含nginx字符
            if os.path.exists(os.path.join(search_path,every_file)):
                nginx_path=os.path.join(search_path,every_file,'sbin/nginx')
                result=commands.getstatusoutput(nginx_path+' -v')
                if result[1]:
                    line_list=result[1].split('\n')
                    sub_list=line_list[0].split()#分割输出内容的第一行
                    shutil.copyfile(nginx_path,nginx_path+str(time.time()))
                    nginx_options=open(nginx_path,'r')
                    nginx_content=nginx_options.read()
                    nginx_options.close()
                    os.remove(nginx_path)
                    write_nginx=re.sub(sub_list[2],'6'*len(sub_list[2]),nginx_content)
                    new_nginx=open(nginx_path,'w')
                    new_nginx.write(write_nginx)
                    new_nginx.close()
                    os.system('chmod 755 '+nginx_path)
        if re.findall('apache',every_file):
            if os.path.exists(os.path.join(search_path,every_file)):
                apache_path=os.path.join(search_path,every_file,'bin/httpd')
                apache_result=commands.getstatusoutput(apache_path+' -v')
                if apache_result[1]:
                    line_list=apache_result[1].split('\n')
                    sub_list=line_list[0].split()
                    shutil.copyfile(apache_path,apache_path+str(time.time()))
                    apache_options=open(apache_path,'r')
                    apache_content=apache_options.read()
                    apache_options.close()
                    os.remove(apache_path)
                    write_apache=re.sub(sub_list[2],'6'*len(sub_list[2]),apache_content)
                    new_apache=open(apache_path,'w')
                    new_apache.write(write_apache)
                    new_apache.close()
                    os.system('chmod 755 '+apache_path)

if options.ssh:
    if os.path.exists('/usr/bin/ssh'):
        ssh_result=commands.getstatusoutput('/usr/bin/ssh -V') 
        ssh_list=ssh_result[1].split()
        if re.findall('OpenSSH',ssh_list[0]):
            shutil.copyfile('/usr/bin/ssh','/usr/bin/ssh'+str(time.time()))
            ssh_options=open('/usr/bin/ssh','r')
            ssh_content=ssh_options.read()
            ssh_options.close()
            os.remove('/usr/bin/ssh')
            sub_str=re.sub(',','',ssh_list[0])
            ssh_content=re.sub(sub_str,'6'*len(sub_str),ssh_content)
            ssh_wr=open('/usr/bin/ssh','w')
            ssh_wr.write(ssh_content)
            ssh_wr.close()
            os.system('chmod 755 /usr/bin/ssh')

    if os.path.exists('/usr/sbin/sshd'):
        sshd_result=commands.getstatusoutput('/usr/sbin/sshd -V') 
        sshd_list=sshd_result[1].split()
        for every_sub_sshd in sshd_list:
            if re.findall('OpenSSH',every_sub_sshd):
                shutil.copyfile('/usr/sbin/sshd','/usr/sbin/sshd'+str(time.time()))
                sshd_options=open('/usr/sbin/sshd','r')
                sshd_content=sshd_options.read()
                sshd_options.close()
                os.remove('/usr/sbin/sshd')
                sub_str=re.sub(',','',every_sub_sshd)
                sshd_content=re.sub(sub_str,'6'*len(sub_str),sshd_content)
                sshd_wr=open('/usr/sbin/sshd','w')
                sshd_wr.write(sshd_content)
                sshd_wr.close()
                os.system('chmod 755 /usr/sbin/sshd')
