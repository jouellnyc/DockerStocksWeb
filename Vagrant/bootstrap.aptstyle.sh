#!/bin/bash

apt update -y
apt upgrade  -y
apt install zip -y 


#Docker install
which docker || (curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh)

#Docker Compose install
[ -f /usr/local/bin/docker-compose ] || sudo curl -L "https://github.com/docker/compose/releases/download/1.25.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && sudo chmod +x /usr/local/bin/docker-compose

#Pip install
which pip3 ||  sudo apt install python3-pip -y
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-2.0.30.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

#vagrant
echo "alias l='ls -ltr'" >> /home/vagrant/.bashrc
