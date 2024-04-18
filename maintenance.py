#!/usr/bin/env python3

#
# プロパティとかのメンテ
#

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

opts,args = getopt.getopt(sys.argv[1:],"xf")
exec=False
force=False
for opt in opts:
    if opt[0]=='-x':
        exec=True
    if opt[0]=='-f':
        force=True

# get existing prop ver
pwd = atf.pwd


if len(glob.glob(pwd + '/props/*')) == 0:
    print('### NO PROPS. Need to run ./get_all_property.py')
    cmd=pwd + '/get_all_property.py'
    if(exec):
        os.system(cmd)
    else:
        print(cmd)
    exit(0)

if force:
    print('### DELETE Terraform STATE (rm -rf [path])')
    lgret = subprocess.check_output( [pwd + '/_scr/existTfstate.sh'] ).decode('ascii').splitlines()
    for v in lgret:
        spl = v.split('/')
        if atf.filterProps(spl[4],spl[5],spl[6])==False:
            continue

        if(exec):
            os.system('rm -rf '+v)
            print('DELETE: %s' % v)
        else:
            print('rm -rf '+v)
        
lgret = subprocess.check_output( [pwd + '/_scr/existPropVer.sh'] ).decode('ascii').splitlines()
current={}
for v in lgret:
    v=v.strip().split(':',2)
    spl=v[0].replace(pwd+'/','').split('/',4)
    if atf.filterProps(spl[1],spl[2],spl[3])==False:
        continue

    current['/'.join(spl[1:4])] = int(v[2].strip(', \''))


none_exported   = [] #未エクスポート
need_update     = [] #要アップデート
need_delete     = [] #既にAkamaiにない（削除対象）
remote={}

# プロパティ関連のdiff

props = atf.list_properties()
for v in props:
    cid = v['contractId']
    gid = v['groupId']
    pname=v['propertyName']
    ver = atf.selectPropertyVer(v['latestVersion'], v['stagingVersion'], v['productionVersion'])
    path='%s/%s/%s' % (cid, gid, pname)
    remote[path]=ver
    if path not in current:
        none_exported.append([path, ver])
    elif current[path] < ver:
        need_update.append([path, current[path], ver])

#lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lg', '-f' ,'json','-s', 'default'] ))
#for v in lgret:
#    cid = v['contractIds'][0]
#    gid = v['groupId']
#    if atf.filterProps(cid,gid)==False:
#        continue
#
#    lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lpr', '-c', cid, '-g', gid, '-f' ,'json','-s', 'default'] ))
#    for vv in lgret:
#        if atf.filterProps(props=vv['propertyName'])==False:
#            continue
#        ver = atf.selectPropertyVer(vv['latestVersion'], vv['stagingVersion'], vv['productionVersion'])
#
#        path='%s/%s/%s' % (vv['contractId'], vv['groupId'], vv['propertyName'])
#        remote[path]=ver
#
#        if path not in current:
#            none_exported.append([path, ver])
#        elif current[path] < ver:
#            need_update.append([path, current[path], ver])
#
for k in current.keys():
    if k not in remote:
        need_delete.append(k)

proptasks=[]

print('### NOT EXPORTED ( ./get_property.sh [property] [ver])')
for v in none_exported:
    if(exec):
        #os.system(pwd + '/get_property.sh %s %s' % (v[0].split('/',2)[2], v[1]))
        proptasks.append([v[0].split('/',2)[2], v[1]])
        print('EXPORT(QUEUED): %s %s' % (v[0], v[1]))
    else:
        print(pwd + '/get_property.sh %s %s' % (v[0].split('/',2)[2], v[1]))
print('\n### NEEDS UPDATE ( rm -rf [property]; ./get_property.sh [property])')
for v in need_update:
    if(exec):
        os.system('rm -rf props/'+v[0])
        proptasks.append([v[0].split('/',2)[2], v[2]])
        #os.system(pwd + '/get_property.sh %s %s' % (v[0].split('/',2)[2], v[2]))
        print('UPDATE(QUEUED): %s (Version: %d->%d)' % (v[0], v[1], v[2]))
    else:
        print('rm -rf props/'+v[0], end='; ')
        print(pwd + '/get_property.sh %s %s' % (v[0].split('/',2)[2], v[2]))
print('\n### DELETED PROPERTY ( rm -rf props/[property] )')
for v in need_delete:
    if(exec):
        os.system('rm -rf props/'+v)
        print('DELETE: %s' % v)
    else:
        print('rm -rf props/'+v)

if len(proptasks) > 0:
    atf.get_properties(proptasks)

print('\n\ndone.')