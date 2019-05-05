#-*- coding:utf-8 -*-
import sys,os,re,subprocess,tarfile
try:
    import urllib2,urllib
except:
    import urllib
    import urllib.request as urllib2
#保存的位置
save_path='/usr/local/redis-4.0.14.tar.gz'
#redis压缩下载地址
redis_down_path='http://39.104.119.163/upload_special/redis-4.0.14.tar.gz'
#redis的安装脚本
redis_install_server='http://39.104.119.163/upload_special/install_server.sh'
#如果需要挂代理，填写代理地址
proxy_ip='http://10.200.58.39:3128'
if proxy_ip:
    proxy_support = urllib2.ProxyHandler({"http":proxy_ip,'https':proxy_ip})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)
res_redis=urllib2.urlopen(redis_down_path).read()
res_redis_options=open(save_path,'wb')
res_redis_options.write(res_redis)
res_redis_options.close()
tar_options = tarfile.open(save_path,'r:gz')
for every_tar_file in tar_options:
    tar_options.extract(every_tar_file,os.path.dirname(save_path))
#tar_options.extractall(path=os.path.dirname(save_path))
tar_dir=re.sub('\.tar\.gz','',os.path.basename(save_path))
os.chdir(os.path.join(os.path.dirname(save_path),tar_dir))
res_script=urllib2.urlopen(redis_install_server).read()
res_script_options=open(os.path.join(os.path.dirname(save_path),tar_dir)+'/utils/install_server.sh','wb')
res_script_options.write(res_script)
res_script_options.close()
subprocess.Popen('make MALLOC=libc',stdout=subprocess.PIPE,shell=True).stdout.read()
subprocess.Popen('make install PREFIX=/usr/local/redis',stdout=subprocess.PIPE,shell=True).stdout.read()
subprocess.Popen('./utils/install_server.sh',stdout=subprocess.PIPE,shell=True).stdout.read()