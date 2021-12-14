#!/bin/bash

source data/AWS.vars.txt
docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml build
docker images
docker tag docker_stocks_app:latest 631686326988.dkr.ecr.us-east-1.amazonaws.com/docker_stocks_app:latest
