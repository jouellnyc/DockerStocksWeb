#!/usr/bin/env python3


from init import Credentials
creds = Credentials()
print(creds.init_config_all)
print(creds.mode_is_local())
print(creds.get_all_credentials())

"""
import init 
print(init.get_secrets_from_local())
print(init.get_local_mongodb_config())
print(init.get_all_credentials())
"""
