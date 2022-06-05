#!/bin/bash


#docker-compose -f docker-compose.local.yaml build

for svc in app web; do 

    docker tag docker_stocks_${svc}:latest 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_${svc}:latest
    PUSH="docker push 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_${svc}:latest"
    if  ! $PUSH ; then
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 631686326988.dkr.ecr.us-east-1.amazonaws.com 
        $PUSH
    fi

done

