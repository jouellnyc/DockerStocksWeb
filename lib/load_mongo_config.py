#!/usr/bin/env python3

import yaml

def get_mongodb_config():
    try:
        with open('/stocks/mongo_infra_prod_config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        with open('../mongo_infra_prod_config.yaml', 'r') as file:
            return yaml.safe_load(file)

def using_aws():
    if get_mongodb_config()['Mode'] == 'AWS':
        return True
    return False

def get_local_mongodb_config():
    return get_mongodb_config()['LocalInfra']

def get_aws_mongodb_config():
    return get_mongodb_config()['AWS']

if __name__ == "__main__":
    print(get_mongodb_config())
    print(using_aws())
    print(get_local_mongodb_config())
    print(get_local_mongodb_config()[0]['port'])
    print(get_local_mongodb_config()[1]['mongohost'])
    print(get_local_mongodb_config()[2]['database'])
    print(get_local_mongodb_config()[3]['collection'])
    print(get_local_mongodb_config()[3]['collection'])
    print(get_aws_mongodb_config()[0]['secret'])
    print(get_aws_mongodb_config()[1]['region'])
