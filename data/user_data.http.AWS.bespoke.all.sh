#!/bin/bash -x

### Update Software and utils
yum update -y
yum -y install git
yum -y install python3
pip3 install boto3
pip3 install pyyaml
yum -y install awslogs
yum -y install telnet
yum -y install jq

amazon-linux-extras install docker


### Install aws
cd /tmp
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

### Install Docker
curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

### Start Docker and AWSlogsd
service docker start
chkconfig docker on

service awslogsd start
chkconfig awslogsd on

### Setup to Pull Images 
GITHUB_REPO="https://github.com/jouellnyc/DockerStocksWeb.git"
GIT_DIR="/gitrepos/"
mkdir -p $GIT_DIR
cd $GIT_DIR

git clone $GITHUB_REPO
cd DockerStocksWeb
source data/AWS.vars.txt
/usr/local/bin/aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ECR_REPO

# Pull and Tag Images
docker pull       $AWS_ECR_REPO/$SHORT_WEB_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_WEB_IMAGE $SHORT_WEB_IMAGE

# Pull and Tag Images
docker pull       $AWS_ECR_REPO/$SHORT_APP_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_APP_IMAGE $SHORT_APP_IMAGE

# Start in all up if we can update the Mongo IP ACL
DOCKER_COMPOSE_FILE="docker-compose.AWS.web.app.Hosted.mongo.yaml"
./update_mongo_ip_allow_list.sh && docker-compose -f $DOCKER_COMPOSE_FILE up -d

### End
