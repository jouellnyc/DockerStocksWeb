#!/bin/bash -x

REPO="https://github.com/jouellnyc/DockerStocksWeb.git"

### Update Software and utils
yum update -y
yum -y install git 
yum -y install python3 
pip3 install boto3
yum -y install awslogs
yum -y install telnet 

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

### Start Build 
service docker start
chkconfig docker on
service awslogsd start
chkconfig awslogsd on

GIT_DIR="/gitrepos/"
mkdir -p $GIT_DIR
cd $GIT_DIR
git clone $REPO
cd DockerStocksWeb

#IMAGE="631686326988.dkr.ecr.us-east-1.amazonaws.com/docker-stocks-web:latest"
#docker pull $IMAGE
#docker image tag $IMAGE dockerstocksweb_web:latest

#IMAGE="631686326988.dkr.ecr.us-east-1.amazonaws.com/dockerstocksweb_app:latest"
#docker pull $IMAGE
#docker image tag $IMAGE dockerstocksweb_app:latest

source data/AWS.vars.txt
DOCKER_COMPOSE_FILE="docker-compose.AWS.hosted.MongoDb.yaml"
docker-compose -f $DOCKER_COMPOSE_FILE up -d

### End
