#!/bin/bash

[ -z $2 ] &&  { echo "$0 local|AWS up|down|ps|build"; exit 55;  }

WHAT=$2
if [ x$WHAT = 'xup' ] ; then
    WHAT='up -d'
fi

case $1 in
local)
    docker-compose -f docker-compose.local.yaml $WHAT
    ;;
AWS)
    docker-compose -f docker-compose.AWS.hosted.MongoDb.yaml $WHAT
    ;;
esac
