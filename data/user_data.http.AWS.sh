#!/bin/bash -x

source user_data.core 

#*Vars
docker pull       $AWS_ECR_REPO/$SHORT_WEB_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_WEB_IMAGE $SHORT_WEB_IMAGE

#*Vars
docker pull       $AWS_ECR_REPO/$SHORT_APP_IMAGE
docker image tag  $AWS_ECR_REPO/$SHORT_APP_IMAGE $SHORT_APP_IMAGE

DOCKER_COMPOSE_FILE="docker-compose.AWS.hosted.MongoDb.yaml"
docker-compose -f $DOCKER_COMPOSE_FILE up -d

### End
