import configparser
import re
import os
import subprocess
import json
import time
import pprint
import asyncio

class AkamaiTf:
    config_ini_path = '/workdir/mount/config.ini'
    def __init__(self):
        self.in_contract = None
        self.ex_contract = None
        self.in_group = None
        self.ex_group = None
        self.in_property = None
        self.ex_property = None
        self.get_property_ver = 'activate'
        self.api_concurrency = 5
        self.prop_concurrency = 3
        self.pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        if os.path.exists(AkamaiTf.config_ini_path):
            config_ini = configparser.ConfigParser()
            config_ini.read(AkamaiTf.config_ini_path, encoding='utf-8')
            config_default = config_ini['default']

            if config_default.get('include_contract') is not None and config_default.get('include_contract') != '':
                self.in_contract = re.compile(config_default.get('include_contract'))
            if config_default.get('exclude_contract') is not None and config_default.get('exclude_contract') != '':
                self.ex_contract = re.compile(config_default.get('exclude_contract'))

            if config_default.get('include_group') is not None and config_default.get('include_group') != '':
                self.in_group = re.compile(config_default.get('include_group'))
            if config_default.get('exclude_group') is not None and config_default.get('exclude_group') != '':
                self.ex_group = re.compile(config_default.get('exclude_group'))

            if config_default.get('include_property') is not None and config_default.get('include_property') != '':
                self.in_property = re.compile(config_default.get('include_property'))
            if config_default.get('exclude_property') is not None and config_default.get('exclude_property') != '':
                self.ex_property = re.compile(config_default.get('exclude_property'))
            if config_default.get('get_property_ver') is not None and config_default.get('get_property_ver') != '':
                self.get_property_ver = config_default.get('get_property_ver')
            if config_default.getint('api_concurrency') is not None:
                self.api_concurrency = config_default.getint('api_concurrency')
            if config_default.getint('prop_concurrency') is not None:
                self.prop_concurrency = config_default.getint('prop_concurrency')

    def filterProps(self, cid=None, gid=None, props=None):
        if cid is not None:
            if self.in_contract is not None and self.in_contract.match(cid) is None:
                return False
            if self.ex_contract is not None and self.ex_contract.match(cid) is not None:
                return False
        if gid is not None:
            if self.in_group is not None and self.in_group.match(gid) is None:
                return False
            if self.ex_group is not None and self.ex_group.match(gid) is not None:
                return False
        if props is not None:
            if self.in_property is not None and self.in_property.match(props) is None:
                return False
            if self.ex_property is not None and self.ex_property.match(props) is not None:
                return False
        return True

    def selectPropertyVer(self, latest, staging, production):
        #print ("l:%s s:%s p:%s" %(latest, staging, production))
        if latest is None:
            latest = 0
        if staging is None:
            staging = 0
        if production is None:
            production = 0
        ver = 0
        if self.get_property_ver == 'latest':
            # 最新のものを取得
            ver = latest
        elif self.get_property_ver == 'production':
            # prod->stg->latestで取得
            if production > ver:
                ver = production
            elif staging > ver:
                ver = staging
            else:
                ver = latest
        else:
            # アクティベートされている最新のバージョンを取得
            if staging > ver:
                ver = staging
            if production > ver:
                ver = production
            if ver == 0:
                ver = latest
        return ver

    async def call_akamai(self, opts:list, retry=3):
        #print(time.time())
        for i in range(0, retry):
            try:
                p= await asyncio.create_subprocess_exec(
                    *[*['akamai'], *opts, *['-f' ,'json','-s', 'default']]
                    , stdout=asyncio.subprocess.PIPE
                )
                j=await p.communicate()
                
                return json.loads(j[0])
            except Exception as e:
                if i == retry - 1:
                    raise e
                await asyncio.sleep(1)
                continue
    async def sem_call_akamai(self, opts:list, retry=2):
        async with self.ak_sem:
            return await self.call_akamai(opts, retry)

    async def __list_properties(self):
        lgret = await self.call_akamai(['pm','lg'])
        tasks=[]
        for v in lgret:
            cid = v['contractIds'][0]
            gid = v['groupId']
            if self.filterProps(cid,gid)==False:
                continue
            tasks.append(self.sem_call_akamai(['pm','lpr', '-c', cid, '-g', gid]))
        res = await asyncio.gather(*tasks)
        ret=[]
        for props in res:
            for prop in props:
                if self.filterProps(props=prop['propertyName'])==False:
                    continue
                ret.append(prop)
        return ret

    def list_properties(self):
        self.ak_sem = asyncio.Semaphore(self.api_concurrency)
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(self.__list_properties())
        return ret

    async def get_property(self, props, ver=None):
        param = [self.pwd + '/get_property.sh', props]
        if ver is not None:
            param.append(str(ver))
        p= await asyncio.create_subprocess_exec(
            *param
            #, stdout=asyncio.subprocess.PIPE
        )
        await p.communicate()
        
    async def sem_get_property(self, props, ver=None):
        async with self.prop_sem:
            await self.get_property(props, ver)

    async def __get_properties(self, opts):
        tasks=[]
        for v in opts:
            prop = v[0]
            ver = None
            if v[1] is not None:
                ver = v[1]
            tasks.append(self.sem_get_property(prop,ver))
        await asyncio.gather(*tasks)

    def get_properties(self, opts:list):
        self.prop_sem = asyncio.Semaphore(self.prop_concurrency)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__get_properties(opts))
