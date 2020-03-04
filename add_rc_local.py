#-*- coding:utf-8 -*-
import os,re,shutil,socket,subprocess,time,tarfile,stat,platform
try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve
rc_read=open('/etc/rc.d/rc.local','r')
rc_content=rc_read.read()
rc_read.close()
route_status=0
for every_line in rc_content.split('\n'):
    if re.findall('route add \-host 10\.150\.35\.8 gw 10\.150\.51\.1',every_line):
        route_status=1
if route_status==0:
    rc_content=rc_content+'\nroute add -host 10.150.35.8 gw 10.150.51.1'
rc_options=open('/etc/rc.d/rc.local','w')
rc_options.write(rc_content)
rc_options.close()
subprocess.Popen('chmod +x /etc/rc.d/rc.local',stdout=subprocess.PIPE,shell=True).stdout.read()