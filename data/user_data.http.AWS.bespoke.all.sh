#!/bin/bash -x


### Update Software and utils
yum update -y
yum -y install git 
yum -y install python3 
pip3 install boto3
yum -y install awslogs
yum -y install telnet 
yum -y install jq 

amazon-linux-extras install docker

### Install aws
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
/usr/local/bin/aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 631686326988.dkr.ecr.us-east-1.amazonaws.com

### Install Docker
curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

### Start Docker and AWSlogsd
service docker start
chkconfig docker on

service awslogsd start
chkconfig awslogsd on

### Start Build 
GITHUB_REPO="https://github.com/jouellnyc/DockerStocksWeb.git"
GIT_DIR="/gitrepos/"
mkdir -p $GIT_DIR
cd $GIT_DIR

#*Vars
git clone $GITHUB_REPO
cd DockerStocksWeb
source data/AWS.vars.txt

#*Vars
docker pull       $AWS_ECR_REPO/$SHORT_WEB_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_WEB_IMAGE $SHORT_WEB_IMAGE

#*Vars
docker pull       $AWS_ECR_REPO/$SHORT_APP_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_APP_IMAGE $SHORT_APP_IMAGE

DOCKER_COMPOSE_FILE="docker-compose.AWS.hosted.MongoDb.bespoke.yaml"
docker-compose -f $DOCKER_COMPOSE_FILE up -d

./update_mongo_ip_allow_list.sh

### End
