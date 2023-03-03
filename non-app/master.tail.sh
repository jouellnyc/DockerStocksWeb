#!/bin/bash


DP="docker ps"
DE="docker exec"
DL="docker logs"

CONT=$( $DP | grep $1 | awk '{ print $1; }')
$DL $CONT

case $1 in
    "") echo "Tell me a name"; exit;;
esac
