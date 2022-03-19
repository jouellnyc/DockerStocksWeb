#!/usr/bin/env python3

import yaml

def get_local_mongodb_config():
    with open('/stocks/mongo_infra_prod_config.yaml', 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    print(get_local_mongodb_config())
