#!/usr/bin/env python3

import json
import pprint
import subprocess
import os
import time
from _scr import AkamaiTf

atf = AkamaiTf.AkamaiTf()
props = atf.list_properties()

task=[]
for v in props:
    cid = v['contractId']
    gid = v['groupId']
    pname=v['propertyName']
    ver = atf.selectPropertyVer(v['latestVersion'], v['stagingVersion'], v['productionVersion'])
    print(">>>contract: %s group: %s property: %s version( stg: %s prod: %s latest: %s get: %s )"%(cid,gid,pname,v['stagingVersion'],v['productionVersion'],v['latestVersion'],ver))
    if os.path.isdir('/workdir/mount/props/%s/%s/%s' %(cid,gid,pname)) is False:
        print(">>>queued")
        task.append([pname,ver])
        #subprocess.call(['/workdir/mount/get_property.sh', pname, str(ver)])
    else:
        print(">>>skip(exsits)")
if len(task) > 0:
    atf.get_properties(task)
#lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lg', '-f' ,'json','-s', 'default'] ))#
#for v in lgret:
#    cid = v['contractIds'][0]
#    gid = v['groupId']
#    if atf.filterProps(cid,gid)==False:
#        continue
#    lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lpr', '-c', cid, '-g', gid, '-f' ,'json','-s', 'default'] ))
#    for vv in lgret:
#        ver = atf.selectPropertyVer(vv['latestVersion'], vv['stagingVersion'], vv['productionVersion'])
#        pname = vv['propertyName']
#        if atf.filterProps(props=pname)==False:
#            continue
#
#        print(">>>contract: %s group: %s property: %s version( stg: %s prod: %s latest: %s get: %s )"%(cid,gid,pname,vv['stagingVersion'],vv['productionVersion'],vv['latestVersion'],ver))
#        if os.path.isdir('/workdir/mount/props/%s/%s/%s' %(cid,gid,pname)) is False:
#            subprocess.call(['/workdir/mount/get_property.sh', pname, str(ver)])
#        else:
#            print(">>>skip(exsits)")
#