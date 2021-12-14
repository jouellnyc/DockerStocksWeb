#!/bin/bash

### VPC Specific helper script
if [[ -z "$1" ]]; then
  echo "$0 name of lc";  exit 55 
fi

LC_NAME="$1"
aws autoscaling create-launch-configuration --launch-configuration-name $LC_NAME --instance-type t2.micro --key-name vpc-06d6f12a90d3b24e3-stocks.pem --security-groups sg-059a16a168f1a1595 sg-0d5aa2183d13bc046 sg-0f39b668f6146939e  --user-data file://./data/user_data.http.AWS.sh   --image-id  ami-0fc61db8544a617ed --iam-instance-profile  AWS_EC2_INSTANCE_PROFILE_ROLE

