#-*- coding:utf-8 -*-
import os,re,shutil,socket,subprocess,time,tarfile,stat,platform
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve
zabbix_path='/usr/local/zabbix'
save_path='/usr/local/zabbix-4.0.1.tar.gz'
bak_path=zabbix_path+str(time.time())
def kill_zabbix_pid():
    all_pid=os.listdir('/proc')
    process_list=[]
    for every_proc_file in all_pid:
        if re.findall('^\d+$',every_proc_file):
            process_list.append(every_proc_file)
    for every_pid in process_list:
        cmd_line_path='/proc/'+every_pid+'/cmdline'
        if os.path.exists(cmd_line_path):
            cmd_line_options=open(cmd_line_path,'r')
            cmd_line_content=cmd_line_options.read()
            cmd_line_options.close()
            if re.findall('zabbix_agentd',cmd_line_content):
                os.kill(int(every_pid),9)
def get_host_ip():
    try:
        sock_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_conn.connect(('8.8.8.8', 80))
        ip = sock_conn.getsockname()[0]
    finally:
        sock_conn.close()
    return ip
def second_get_host_ip():
    host_hostname = socket.gethostname()
    return socket.gethostbyname(host_hostname)
def get_server_ip(host_ip):
    if re.findall('^10\.150\.',host_ip) or re.findall('^10\.151\.',host_ip):
        return '10.150.35.8'
    elif re.findall('^10\.200\.',host_ip):
        return '10.200.31.80'
    elif re.findall('^172\.16',host_ip):
        return '172.16.70.194'
    else:
        return '10.150.35.8'
if os.path.exists(os.path.join(zabbix_path,'sbin/zabbix_agentd')):
    zabbix_agentd_content=subprocess.Popen(os.path.join(zabbix_path,'sbin/zabbix_agentd')+' --version',stdout=subprocess.PIPE,shell=True).stdout.read()
    zabbix_cmd_list=zabbix_agentd_content.split('\n')
    zabbix_cmd_daemon=zabbix_cmd_list[0].split()
    zabbix_version=re.sub('v','',zabbix_cmd_daemon[3])
    if int(zabbix_version[0])<=3:
        try:
            os_version=platform.linux_distribution(supported_dists="redhat")
        except:
            os_version=['1','5']
        print(os_version)
        if os_version[0]:
            if int(os_version[1][0])==6:
                urlretrieve('http://10.200.53.43:81/pcre-7.8-7.el6.x86_64.rpm','/usr/local/pcre-7.8-7.el6.x86_64.rpm')
                urlretrieve('http://10.200.53.43:81/pcre-devel-7.8-7.el6.x86_64.rpm','/usr/local/pcre-devel-7.8-7.el6.x86_64.rpm')
                subprocess.Popen('rpm -ivh /usr/local/pcre-7.8-7.el6.x86_64.rpm',stdout=subprocess.PIPE,shell=True).stdout.read()
                subprocess.Popen('rpm -ivh /usr/local/pcre-devel-7.8-7.el6.x86_64.rpm',stdout=subprocess.PIPE,shell=True).stdout.read()
            elif int(os_version[1][0])==7:
                urlretrieve('http://10.200.53.43:81/pcre-devel-8.32-17.el7.x86_64.rpm','/usr/local/pcre-devel-8.32-17.el7.x86_64.rpm')
                urlretrieve('http://10.200.53.43:81/pcre-8.32-17.el7.x86_64.rpm','/usr/local/pcre-8.32-17.el7.x86_64.rpm')
                subprocess.Popen('rpm -ivh /usr/local/pcre-devel-8.32-17.el7.x86_64.rpm',stdout=subprocess.PIPE,shell=True).stdout.read()
                subprocess.Popen('rpm -ivh /usr/local/pcre-8.32-17.el7.x86_64.rpm',stdout=subprocess.PIPE,shell=True).stdout.read()
            else:
                import yum
                yb=yum.YumBase()
                yb.install(name='pcre')
                yb.resolveDeps()
                yb.buildTransaction()
                yb.processTransaction()
            judge_pcre=subprocess.Popen('rpm -qa|grep pcre-devel',stdout=subprocess.PIPE,shell=True).stdout.read()
            if not re.findall('pcre\-devel',judge_pcre):
                import yum
                yb=yum.YumBase()
                yb.install(name='pcre-devel')
                yb.resolveDeps()
                yb.buildTransaction()
                yb.processTransaction()
            urlretrieve('http://10.200.53.43:81/zabbix-4.0.1.tar.gz','/usr/local/zabbix-4.0.1.tar.gz')
            tar_options = tarfile.open(save_path,'r:gz')
            for every_tar_file in tar_options:
                tar_options.extract(every_tar_file,os.path.dirname(save_path))
            tar_dir=re.sub('\.tar\.gz','',os.path.basename(save_path))
            os.rename(zabbix_path,bak_path)
            kill_zabbix_pid()
            os.chdir(os.path.join(os.path.dirname(save_path),tar_dir))
            subprocess.Popen('./configure --prefix=/usr/local/zabbix  --enable-agent',stdout=subprocess.PIPE,shell=True).stdout.read()
            subprocess.Popen('make',stdout=subprocess.PIPE,shell=True).stdout.read()
            subprocess.Popen('make install',stdout=subprocess.PIPE,shell=True).stdout.read()
            read_agentd=open('/usr/local/'+tar_dir+'/misc/init.d/tru64/zabbix_agentd','rb') 
            agentd_info=read_agentd.read()
            read_agentd.close()
            init_agent_options=open('/etc/init.d/zabbix_agentd','wb')
            init_agent_options.write(agentd_info)
            init_agent_options.close()
            os.chmod('/etc/init.d/zabbix_agentd',stat.S_IRWXO+stat.S_IRWXG+stat.S_IRWXU)
            try:
                os.symlink(zabbix_path+'/sbin/zabbix_agentd', '/usr/local/sbin/zabbix_agentd') 
            except:
                pass
            raw_options=open(bak_path+'/etc/zabbix_agentd.conf','r') 
            raw_content=raw_options.read()
            raw_options.close()
            try:
                host_ip=get_host_ip()
            except:
                host_ip=second_get_host_ip()
            sub_ip=get_server_ip(host_ip)
            agentd_conf=[]
            for every_line in raw_content.split('\n'):
                every_line=every_line.strip()
                if re.findall('^Server\=',every_line):
                    agentd_conf.append('Server='+sub_ip+'\n')
                elif re.findall('^ServerActive\=',every_line):
                    agentd_conf.append('Server='+sub_ip+'\n')
                else:
                    agentd_conf.append(every_line+'\n')
            new_options=open(zabbix_path+'/etc/zabbix_agentd.conf','w')
            new_options.write(''.join(agentd_conf))
            new_options.close()
            subprocess.Popen('/etc/init.d/zabbix_agentd start',stdout=subprocess.PIPE,shell=True)
        else:
            urlretrieve('http://10.200.53.43:81/zabbix-agent-4.0.1-1.el11.suse.x86_64.rpm','/usr/local/zabbix-agent-4.0.1-1.el11.suse.x86_64.rpm')
            os.rename(zabbix_path,bak_path)
            subprocess.Popen('rpm -e zabbix-agent-4.0.1-1.suse11',stdout=subprocess.PIPE,shell=True).stdout.read()
            install_info=subprocess.Popen('rpm -ivh /usr/local/zabbix-agent-4.0.1-1.el11.suse.x86_64.rpm',stdout=subprocess.PIPE,shell=True).stdout.read()
            print(install_info)
            kill_zabbix_pid()
            try:
                os.remove('/etc/init.d/zabbix_agentd')
            except:
                pass
            try:
                
                os.symlink(zabbix_path+'/sbin/zabbix_agentd', '/etc/init.d/zabbix_agentd') 
            except:
                pass
            os.chmod('/etc/init.d/zabbix_agentd',stat.S_IRWXO+stat.S_IRWXG+stat.S_IRWXU)
            raw_options=open(bak_path+'/etc/zabbix_agentd.conf','r') 
            raw_content=raw_options.read()
            raw_options.close()
            host_ip=get_host_ip()
            sub_ip=get_server_ip(host_ip)
            agentd_conf=[]
            for every_line in raw_content.split('\n'):
                every_line=every_line.strip()
                if re.findall('^Server\=',every_line):
                    agentd_conf.append('Server='+sub_ip+'\n')
                elif re.findall('^ServerActive\=',every_line):
                    agentd_conf.append('Server='+sub_ip+'\n')
                elif re.findall('^Hostname\=',every_line):
                    agentd_conf.append('Hostname\='+host_ip+'\n')
                else:
                    agentd_conf.append(every_line+'\n')
            new_options=open(zabbix_path+'/etc/zabbix_agentd.conf','w')
            new_options.write(''.join(agentd_conf))
            new_options.close()
            shutil.rmtree('/usr/local/zabbix/etc/zabbix_agentd.conf.d')
            shutil.copytree(bak_path+'/etc/zabbix_agentd.conf.d','/usr/local/zabbix/etc/zabbix_agentd.conf.d')
            subprocess.Popen('/etc/init.d/zabbix_agentd',stdout=subprocess.PIPE,shell=True).stdout.read()