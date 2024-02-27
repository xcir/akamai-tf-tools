#!/usr/bin/env python3

import json
import pprint
import subprocess

lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lg', '-f' ,'json','-s', 'default'] ))
for v in lgret:
    cid = v['contractIds'][0]
    gid = v['groupId']
    lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lpr', '-c', cid, '-g', gid, '-f' ,'json','-s', 'default'] ))
    for vv in lgret:
        ver = 0
        if vv['productionVersion'] is not None and ver < vv['productionVersion']:
            ver = vv['productionVersion']
        if vv['stagingVersion'] is not None and ver < vv['stagingVersion']:
            ver = vv['stagingVersion']
        if ver == 0:
            ver = vv['latestVersion']
        pname = vv['propertyName']
        print(">>>contract: %s group: %s property: %s version( stg: %s prod: %s latest: %s get: %s )"%(cid,gid,pname,vv['stagingVersion'],vv['productionVersion'],vv['latestVersion'],ver))
        subprocess.call(['./get_property.sh', pname, str(ver)])
    #pprint.pprint (lgret)
    #break