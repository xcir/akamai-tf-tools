#!/usr/bin/env python3

import json
import pprint
import subprocess
import os
import glob
import getopt
import sys
from _scr import AkamaiTf
import time

atf = AkamaiTf.AkamaiTf()

props={}
akprop = atf.list_properties()

for v in akprop:
    key = '%s-%s'%(v['contractId'],v['groupId'])
    if key not in props.keys():
        props[key]={}
    props[key][v['propertyName']] = {
        'pname':v['propertyName'],
        'cid':v['contractId'],
        'gid':v['groupId'],
        'gname':v['groupName'],
        'latest':v['latestVersion'],
        'prod':v['productionVersion'],
        'stg':v['stagingVersion'],
        'local': None
    }

if len(glob.glob(atf.pwd + '/props/*')) > 0:
    localprop = subprocess.check_output( [atf.pwd + '/_scr/existPropVer.sh'] ).decode('ascii').splitlines()
    for v in localprop:
        v=v.strip().split(':',2)
        spl=v[0].replace(atf.pwd+'/','').split('/',4)
        if atf.filterProps(spl[1],spl[2],spl[3])==False:
            continue
        cid = spl[1]
        gid = spl[2]
        pname = spl[3]
        ver = int(v[2].strip(', \''))

        key = '%s-%s'%(cid, gid)
        if key not in props.keys():
            props[key]={}

        if pname in props[key].keys():
            props[key][pname]['local'] = ver
        else:
            props[key][pname] = {
                'pname':pname,
                'cid':cid,
                'gid':gid,
                'gname':'',
                'latest': None,
                'prod': None,
                'stg': None,
                'local': ver
            }


print('%16s %16s %32s %60s %9s %9s %9s %9s' % ('contractId','groupId','groupName','propertyName','latestVer','prodVer','stgVer','localVer'))
print('-'*167)
for v in props.values():
    for vv in v.values():
        print('%16s %16s %32s %60s %9s %9s %9s %9s' % (vv['cid'],vv['gid'],vv['gname'],vv['pname'],vv['latest'],vv['prod'],vv['stg'],vv['local']))

