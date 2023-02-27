#!/usr/bin/env python3

import yaml  

try:
    from lib.aws_secrets import get_aws_secrets 
except ModuleNotFoundError:
    from     aws_secrets import get_aws_secrets 

class Credentials:

    def __init__(self, init_file="/stocks/init.yaml", env_file="/stocks/.my.env"):
        self.init_file = init_file
        self.env_file  = env_file
        self.init_config_all = self.get_init_config()
            
    def get_init_config(self):
        with open(self.init_file,'r') as file:
            return yaml.safe_load(file)

    def get_all_credentials(self):
        if self.mode_is_aws():
            return self.get_secrets_from_aws()
        elif self.mode_is_local():
            return self.get_secrets_from_local()

    def get_secrets_from_aws(self):
        import json
        region        = self.init_config_all['AWS']['region']
        secret        = self.init_config_all['AWS']['secret']
        return  json.loads(get_aws_secrets(secret, region))

    def get_secrets_from_local(self):
        secrets={}
        with open(self.env_file) as fh:
            for entry in fh:
                _lst =  entry.strip().split('=')
                secrets[_lst[0]] = _lst[1] 
        return secrets


    def get_local_mongodb_config(self):
        return self.init_config_all['Local']

    def mode_is_aws(self):
        return self.init_config_all['Mode'] == 'AWS'

    def mode_is_local(self):
        return self.init_config_all['Mode'] == 'Local'

if __name__ == "__main__":

    from pprint import  pprint as pp
    creds = Credentials(init_file="../init.yaml", env_file="../.my.env")
    #breakpoint()
    pp(creds.get_all_credentials())
