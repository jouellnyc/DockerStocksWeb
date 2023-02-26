#!/usr/bin/env python3

import json
import yaml

class Credentials:

    def __init__(self, init_file="init.yaml", env_file="../.my.env"):
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
        from . aws_secrets import get_aws_secrets 
        region        = self.init_config_all['AWS']['region']
        secret        = self.init_config_all['AWS']['secret']
        return json.loads(get_aws_secrets(secret, region))

    def get_secrets_from_local(self):
        from os import environ as env
        from dotenv import find_dotenv, load_dotenv
        ENV_FILE = find_dotenv(self.env_file)
        if ENV_FILE:
            load_dotenv(ENV_FILE)
            mysecret = {}
            for x in [ 'AUTH0_CLIENT_ID'    , 'AUTH0_CLIENT_SECRET', 'AUTH0_DOMAIN', 'APP_SECRET_KEY',
                      'COMPOSE_PROJECT_NAME', 'collection'         , 'mongohost'   , 'mongopassword',
                      'mongousername'       , 'port'               , 'database' ]:
                mysecret[x] = env.get(x)
        return mysecret

    def get_local_mongodb_config(self):
        return self.init_config_all['LocalInfra']

    def mode_is_aws(self):
        return self.init_config_all['Mode'] == 'AWS'

    def mode_is_local(self):
        return self.init_config_all['Mode'] == 'Local'

if __name__ == "__main__":

    from  pprint import pprint as pp
    creds = Credentials(init_file="../init.yaml")
    print("== All Config  ==")
    pp(creds.init_config_all)
    print("== Mode is Local  ==")
    pp(creds.mode_is_local())
    print("== get_all_credentials ==")
    pp(creds.get_all_credentials())
