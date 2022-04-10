#!/bin/bash

#
# REF - https://www.mongodb.com/docs/atlas/reference/api/ip-access-list/get-all-access-list-entries/
# REF- https://www.mongodb.com/docs/atlas/reference/api/ip-access-list/add-entries-to-access-list/
#


PROD_API="v1.0"
REGION="us-east-1"
SECRET_ID="Prod-Stocks"

export PRIVATE_KEY=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.monogo_api_private_key')
export  PUBLIC_KEY=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.monogo_api_public_key')
export      ORG_ID=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.mongo_org_id')
export    GROUP_ID=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.mongo_stocks_project_id')
export API_ALLOWS_LIST_KEY=$(aws secretsmanager get-secret-value --secret-id $SECRET_ID --query SecretString --region $REGION  --output text | jq  --raw-output '.mongo_allow_list_api_key_id')
export MY_IP=$(curl http://169.254.169.254/latest/meta-data/public-ipv4)
export POST_DATA=post_data.txt

echo "[{\"ipAddress\":\"${MY_IP}\"}]" > $POST_DATA


### Group / Project updating the DB ACCESS Network list
curl -v --user "${PUBLIC_KEY}:${PRIVATE_KEY}" --digest \
     --header "Accept: application/json" \
     --header "Content-Type: application/json" \
     --request POST "https://cloud.mongodb.com/api/atlas/$PROD_API/groups/${GROUP_ID}/accessList?pretty=true" \
     --data @"${POST_DATA}"

exit

### Group / Project listing  the DB ACCESS Network list
curl --user "${PUBLIC_KEY}:${PRIVATE_KEY}" --digest \
     --header "Accept: application/json" \
     --request GET "https://cloud.mongodb.com/api/atlas/$PROD_API/groups/${GROUP_ID}/accessList?pretty=true"


### ORG Level list of  API Keys
curl --user "${PUBLIC_KEY}:${PRIVATE_KEY}" --digest \
 --header "Accept: application/json" \
 --header "Content-Type: application/json" \
 --include \
 --request GET "https://cloud.mongodb.com/api/atlas/$PROD_API/orgs/${ORG_ID}/apiKeys?pretty=true"


### ORG Level ACCESS for the API Keys themseleves
curl --user "${PUBLIC_KEY}:${PRIVATE_KEY}" --digest \
     --header 'Accept: application/json' \
     --header 'Content-Type: application/json' \
     --include \
     --request POST "https://cloud.mongodb.com/api/public/$PROD_API/orgs/${ORG_ID}/apiKeys/{$ALLOW_LIST_API_KEY_ID}/accessList?pretty=true" \
     --data '
       [{
          "ipAddress" : "77.54.32.11"
       }]'

