#!/bin/bash

cd non-app
./set_aws_env.py
cd ..
source aws_env
set | grep AWS
