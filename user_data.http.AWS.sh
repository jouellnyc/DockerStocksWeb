#!/bin/bash -x

yum update -y
yum -y install git 
yum -y install python3 
pip3 install boto3
yum -y install awslogs

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
git clone https://github.com/jouellnyc/AWS.git
cd AWS/boto3/
read -r  MONGOUSERNAME MONGOPASSWORD MONGOHOST <  <(/usr/bin/python3 ./getSecret.py)

cd $GIT_DIR
git clone https://github.com/jouellnyc/shouldipickitup.git
cd shouldipickitup
sleep 2
sed -i -r  's#MONGOCLIENTLINE#client = MongoClient("mongodb+srv://MONGOUSERNAME:MONGOPASSWORD@MONGOHOST/test?retryWrites=true\&w=majority", serverSelectionTimeoutMS=2000)#' lib/mongodb.py

sleep 2
sed -i s"/MONGOUSERNAME/${MONGOUSERNAME}/" lib/mongodb.py
sed -i s"/MONGOPASSWORD/${MONGOPASSWORD}/" lib/mongodb.py
sed -i         s"/MONGOHOST/${MONGOHOST}/" lib/mongodb.py

source $GIT_DIR/AWS/shared_vars.txt
docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml up -d
