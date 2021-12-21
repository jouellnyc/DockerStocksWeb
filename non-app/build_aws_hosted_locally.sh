#!/bin/bash

docker-compose  -f docker-compose.AWS.hosted.MongoDb.no.cloudwatch.yaml build
echo == Docker Images
docker images
REPO="631686326988.dkr.ecr.us-east-1.amazonaws.com"
SHORT_IMAGE="docker_stocks_app:latest"
docker image tag $SHORT_IMAGE $REPO/$SHORT_IMAGE && echo docker push $SHORT_IMAGE $REPO/$SHORT_IMAGE 
