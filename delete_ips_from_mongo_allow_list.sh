#!/bin/bash

PROD_API="v1.0"
REGION="us-east-1"
SECRET_ID="Prod-Stocks"

export PRIVATE_KEY=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.monogo_api_private_key')
export  PUBLIC_KEY=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.monogo_api_public_key')
export    GROUP_ID=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.mongo_stocks_project_id')

while read MY_IP; do

        echo  == $MY_IP ==
        curl --user "${PUBLIC_KEY}:${PRIVATE_KEY}" --digest --include \
             --header 'Accept: application/json' \
             --header 'Content-Type: application/json' \
             --request DELETE  'https://cloud.mongodb.com/api/atlas/v1.0/groups/${GROUP_ID}/accessList/${MY_IP}%2F32'
done


