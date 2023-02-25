#!/usr/bin/env python3

import yaml
from aws_secrets import get_aws_secrets 

class Credentials:

    def __init__(self,init_file=None):
        self.init_config_all = self.get_init_config()

    def get_init_config(self, init_file="init.yaml"):
        with open(init_file,'r') as file:
            return yaml.safe_load(file)

    def get_all_credentials(self):
        if self.mode_is_aws():
            return self.get_secrets_from_aws()
        elif self.mode_is_local():
            return self.get_secrets_from_local()

    def get_secrets_from_aws(self):
        region        = init_config_all['AWS']['region']
        secret        = init_config_all['AWS']['secret']
        return json.loads(get_aws_secrets(secret, region))

    def get_secrets_from_local(self):
        from os import environ as env
        from dotenv import find_dotenv, load_dotenv
        ENV_FILE = find_dotenv('../.my.env')
        if ENV_FILE:
            load_dotenv(ENV_FILE)
            mysecret = {}
            for x in ['AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 'AUTH0_DOMAIN', 'APP_SECRET_KEY','COMPOSE_PROJECT_NAME']:
                mysecret[x] = env.get(x)
        return mysecret

    def mode_is_aws(self):
        return self.init_config_all['Mode'] == 'AWS'

    def mode_is_local(self):
        return self.init_config_all['Mode'] == 'Local'

if __name__ == "__main__":

    from  pprint import pprint as pp
    creds = Credentials()
    print("== All Config  ==")
    pp(creds.init_config_all)
    print("== Mode is Local  ==")
    pp(creds.mode_is_local())
    print("== get_all_credentials ==")
    pp(creds.get_all_credentials())
