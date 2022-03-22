#!/bin/bash -x

source user_data.core

DOCKER_COMPOSE_FILE="docker-compose.AWS.flywheel.yaml"
docker-compose -f $DOCKER_COMPOSE_FILE up -d


