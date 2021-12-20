#!/usr/bin/env python3
file = '/home/john/.aws/credentials'
with open(file,'r') as fh:
    for line in fh.readlines():
         if line.startswith('aws_'):
            if 'secret' in line:
                 KEY=line.split('=')[1].replace(" ", "")
            if 'key_id' in line:
                 ID=line.split('=')[1].replace(" ", "")

with open('../aws_env','w') as fh:
    fh.write(f"AWS_ACCESS_KEY_ID={ID}")
    fh.write(f"AWS_SECRET_ACCESS_KEY={KEY}")
    fh.write(f"AWS_DEFAULT_REGION=us-east-1")
