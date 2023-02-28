#!/bin/bash

source .env
source data/AWS.vars.txt

docker-compose  -f  docker-compose.AWS.web.app.Hosted.mongo.yaml build 

for svc in app web; do 

    docker tag "${COMPOSE_PROJECT_NAME}_${svc}:latest" "${AWS_ECR_REP}/${COMPOSE_PROJECT_NAME}_${svc}:latest"
    PUSH="docker push ${AWS_ECR_REPO}/${COMPOSE_PROJECT_NAME}_${svc}:latest"
    if  ! $PUSH ; then
        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin  "${AWS_ECR_REPO}"
        $PUSH
    fi

done
