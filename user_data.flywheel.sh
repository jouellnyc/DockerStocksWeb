#!/bin/bash -x

GIT_AWS="https://github.com/jouellnyc/AWS.git"
GIT_STOCKS="https://github.com/jouellnyc/DockerStocksWeb.git"

yum update -y
yum -y install git 
yum -y install python3 
pip3 install boto3
yum -y install awslogs
yum -y install telnet 

amazon-linux-extras install docker

curl -L https://github.com/docker/compose/releases/download/1.21.0/docker-compose-`uname -s`-`uname -m` | sudo tee /usr/local/bin/docker-compose > /dev/null
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

service docker start
chkconfig docker on
service awslogsd start
chkconfig awslogsd on

GIT_DIR="/gitrepos/"
mkdir -p $GIT_DIR
cd $GIT_DIR/
git clone  $GIT_AWS 
cd AWS/boto3/
read -r  MONGOUSERNAME MONGOPASSWORD MONGOHOST <  <(/usr/bin/python3 ./getSecret.py)

cd $GIT_DIR
git clone $GIT_STOCKS 
cd DockerStocksWeb
sleep 2

MONGOFILE="lib/mongodb.py"
sed -i -r  's#MONGOCLIENTLINE#client = MongoClient("mongodb+srv://MONGOUSERNAME:MONGOPASSWORD@MONGOHOST/test?retryWrites=true\&w=majority", serverSelectionTimeoutMS=2000)#' $MONGOFILE
sed -i s"/MONGOUSERNAME/${MONGOUSERNAME}/" $MONGOFILE
sed -i s"/MONGOPASSWORD/${MONGOPASSWORD}/" $MONGOFILE 
sed -i         s"/MONGOHOST/${MONGOHOST}/" $MONGOFILE 
unset MONGOPASSWORD 
unset MONGOHOST
unset MONGOUSERNAME

DOCKER_COMPOSE_FILE="docker-compose.AWS.flywheel.yaml"
source $GIT_DIR/AWS/aws-cli/shared_vars.txt
docker-compose -f $DOCKER_COMPOSE_FILE up -d
