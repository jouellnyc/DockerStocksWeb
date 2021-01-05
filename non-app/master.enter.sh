#!/bin/bash


DP="docker ps"
DE="docker exec"

function flask {
CONT=$( $DP | grep flask | awk '{ print $1; }')
$DE -it $CONT bash
}


function nginx {
CONT=$( $DP | grep nginx | awk '{ print $1; }')
$DE -it $CONT bash
}

function mongodb {
CONT=$( $DP | grep mongod | awk '{ print $1; }')
$DE -it $CONT bash
}

case $1 in
    "flask") flask ;;
    "nginx") nginx ;;
    "mongodb") mongodb ;;
    "") echo "Tell me a name"; exit;;
esac
