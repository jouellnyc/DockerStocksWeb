#!/bin/bash -x

source user_data.core

DOCKER_COMPOSE_FILE="docker-compose.AWS.crawler.yaml"
docker-compose -f $DOCKER_COMPOSE_FILE up -d
