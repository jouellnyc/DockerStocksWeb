#!/usr/bin/env python3

import yaml

def get_mongodb_config():
    for path in ['/stocks/mongo_infra_prod_config.yaml','../mongo_infra_prod_config.yaml','mongo_infra_prod_config.yaml']:
        try:
            with open(path,'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            continue

def using_aws():
    return get_mongodb_config()['Mode'] == 'AWS'

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
