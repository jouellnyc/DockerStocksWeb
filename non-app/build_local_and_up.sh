#!/bin/bash

cp init.dev.yaml init.yaml
if grep MODE init.yaml | grep AWS; then

    echo "Oops you are set to AWS"

else

    docker-compose  -f docker-compose.Local.web.app.db.yaml build && docker-compose  -f docker-compose.Local.web.app.db.yaml up -d && docker ps

fi
