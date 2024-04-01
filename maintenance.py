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
import configparser
import re


config_ini_path = '/workdir/mount/config.ini'
if os.path.exists(config_ini_path):
    config_ini = configparser.ConfigParser()
    config_ini.read(config_ini_path, encoding='utf-8')
    config_default = config_ini['default']

    if config_default.get('include_contract') is not None and config_default.get('include_contract') != '':
        in_contract = re.compile(config_default.get('include_contract'))
    else:
        in_contract = None
    if config_default.get('exclude_contract') is not None and config_default.get('exclude_contract') != '':
        ex_contract = re.compile(config_default.get('exclude_contract'))
    else:
        ex_contract = None
    if config_default.get('include_gid') is not None and config_default.get('include_gid') != '':
        in_gid = re.compile(config_default.get('include_gid'))
    else:
        in_gid = None
    if config_default.get('exclude_gid') is not None and config_default.get('exclude_gid') != '':
        ex_gid = re.compile(config_default.get('exclude_gid'))
    else:
        ex_gid = None
    if config_default.get('include_property') is not None and config_default.get('include_property') != '':
        in_property = re.compile(config_default.get('include_property'))
    else:
        in_property = None
    if config_default.get('exclude_property') is not None and config_default.get('exclude_property') != '':
        ex_property = re.compile(config_default.get('exclude_property'))
    else:
        ex_property = None
else:
    in_contract = None
    ex_contract = None
    in_gid = None
    ex_gid = None
    in_property = None
    ex_property = None

opts,args = getopt.getopt(sys.argv[1:],"xf")
exec=False
force=False
for opt in opts:
    if opt[0]=='-x':
        exec=True
    if opt[0]=='-f':
        force=True


# get existing prop ver
pwd = os.path.dirname(os.path.abspath(__file__))


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
        if in_contract is not None and in_contract.match(spl[4]) is None:
            #print('A:SKIP: %s' % v)
            continue
        if ex_contract is not None and ex_contract.match(spl[4]) is not None:
            #print('B:SKIP: %s' % v)
            continue
        if in_gid is not None and in_gid.match(spl[4]) is None:
            #print('C:SKIP: %s' % v)
            continue
        if ex_gid is not None and ex_gid.match(spl[4]) is not None:
            #print('D:SKIP: %s' % v)
            continue
        if in_property is not None and in_property.match(spl[6]) is None:
            #print('E:SKIP: %s' % v)
            continue
        if ex_property is not None and ex_property.match(spl[6]) is not None:
            #print('F:SKIP: %s' % v)
            continue
        if(exec):
            os.system('rm -rf '+v)
            print('DELETE: %s' % v)
        else:
            print(v)
        
lgret = subprocess.check_output( [pwd + '/_scr/existPropVer.sh'] ).decode('ascii').splitlines()
current={}
for v in lgret:
    v=v.strip().split(':',2)
    spl=v[0].replace(pwd+'/','').split('/',3)
    if in_contract is not None and in_contract.match(spl[1]) is None:
        #print('A:SKIP: %s' % v)
        continue
    if ex_contract is not None and ex_contract.match(spl[1]) is not None:
        #print('B:SKIP: %s' % v)
        continue
    if in_gid is not None and in_gid.match(spl[3]) is None:
        #print('C:SKIP: %s' % v)
        continue
    if ex_gid is not None and ex_gid.match(spl[3]) is not None:
        #print('D:SKIP: %s' % v)
        continue
    if in_property is not None and in_property.match(spl[4]) is None:
        #print('E:SKIP: %s' % v)
        continue
    if ex_property is not None and ex_property.match(spl[4]) is not None:
        #print('F:SKIP: %s' % v)
        continue
    current[spl[1]+'/'+spl[2]+'/'+spl[3]] = int(v[2].strip(', \''))
    
lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lg', '-f' ,'json','-s', 'default'] ))
none_exported   = [] #未エクスポート
need_update     = [] #要アップデート
need_delete     = [] #既にAkamaiにない（削除対象）
remote={}

# プロパティ関連のdiff
for v in lgret:
    cid = v['contractIds'][0]
    if in_contract is not None and in_contract.match(cid) is None:
        #print('A:SKIP: %s' % v)
        continue
    if ex_contract is not None and ex_contract.match(cid) is not None:
        #print('B:SKIP: %s' % v)
        continue
    gid = v['groupId']
    lgret = json.loads(subprocess.check_output( ['akamai', 'pm', 'lpr', '-c', cid, '-g', gid, '-f' ,'json','-s', 'default'] ))
    for vv in lgret:
        if in_property is not None and in_property.match(vv['propertyName']) is None:
            #print('C:SKIP: %s' % vv)
            continue
        if ex_property is not None and ex_property.match(vv['propertyName']) is not None:
            #print('D:SKIP: %s' % vv)
            continue
        if in_gid is not None and in_gid.match(vv['groupId']) is None:
            #print('E:SKIP: %s' % vv)
            continue
        if ex_gid is not None and ex_gid.match(vv['groupId']) is not None:
            #print('F:SKIP: %s' % vv)
            continue
        ver = 0
        if vv['productionVersion'] is not None and ver < vv['productionVersion']:
            ver = vv['productionVersion']
        if vv['stagingVersion'] is not None and ver < vv['stagingVersion']:
            ver = vv['stagingVersion']
        if ver == 0:
            ver = vv['latestVersion']

        path=vv['contractId'] + '/' + vv['groupId'] +'/' + vv['propertyName']
        remote[path]=ver

        if path not in current:
            none_exported.append(path)
        elif current[path] < ver:
            need_update.append([path, current[path], ver])

for k in current.keys():
    if k not in remote:
        need_delete.append(k)

print('### NOT EXPORTED ( ./get_property.sh [property] )')
for v in none_exported:
    if(exec):
        os.system(pwd + '/get_property.sh %s' % (v.split('/',1)[1]))
        print('EXPORT: %s' % v)
    else:
        print(v)
print('\n### NEEDS UPDATE ( rm -rf [property]; ./get_property.sh [property])')
for v in need_update:
    if(exec):
        os.system('rm -rf props/'+v[0])
        #print(pwd + '/get_property.sh %s' % (v[0].split('/',1)[1]))
        #exit()
        os.system(pwd + '/get_property.sh %s' % (v[0].split('/',1)[1]))
        print('UPDATE: %s' % v[0])
    else:
        print(v[0])
print('\n### DELETED PROPERTY ( rm -rf props/[property] )')
for v in need_delete:
    if(exec):
        os.system('rm -rf props/'+v)
        print('DELETE: %s' % v)
    else:
        print(v)


print('\n\ndone.')