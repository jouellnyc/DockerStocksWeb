#!/usr/bin/python3


if __name__ == "__main__":

    import json
    from aws_secrets import get_aws_secrets
    from load_mongo_config import get_aws_mongodb_config
    from pprint import pprint
    from flask import jsonify

    region        = get_aws_mongodb_config()[1]['region']
    secret        = get_aws_mongodb_config()[0]['secret']
    mysecret      = json.loads(get_aws_secrets(secret, region))
    """
    for k,v in mysecret.items():
        if 'GOOGLE' in k:
            print(k.lower().split('_',2)[2],v)
    """

    myoidc_config         =  {}
    myoidc_data           =  dict( sorted([ (x.lower().split('_',2)[2],y) for x,y in mysecret.items() if 'GOOGLE' in x ])  )
    #myoidc_data           =  myoidc_data.replace("'", '"')
    myoidc_config['web']  =  myoidc_data
    myoidc_config['web']['redirect_uris'] = [ myoidc_config['web']['redirect_uris'] ]


with open('client_secrets.json','w') as fh:
    fh.write(str(myoidc_config).replace("'", '"'))
