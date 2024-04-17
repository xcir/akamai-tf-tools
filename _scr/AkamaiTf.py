import configparser
import re
import os

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



    