#!/bin/bash

#test http on the edges - CAPS are for AWS instances 

[ -z $1 ] &&  { echo "$0 local|DEV|BETA"; exit 55;  }


case $1 in
local)
    URL=http://192.168.0.206
    ;;
DEV)
    URL=X
    ;;
esac

echo "== Checking $1 =="

SLEEP=1

echo "Default"
curl -s -I -X GET "${URL}"/search/?stock=AAPL | grep 200
sleep $SLEEP

echo "2 params"
curl -s -I -X GET "${URL}"/search/?stock=11212\&hello=i | grep 200

sleep $SLEEP
echo "short"
curl -s -I -X GET "${URL}"/search/?stock=A | grep 200

echo "text vs int"
sleep $SLEEP
curl -s -I -X GET "${URL}"/search/?stock=mickeymouse | grep 200

sleep $SLEEP
echo "zap no stock"
curl -s -I -X GET "${URL}"/search/?zap=hello | grep 200


<< 'MULTILINE-COMMENT'
Flask App will log before gunicorn:

INFO:should_flask:querystring: ImmutableMultiDict([('zip', '11218')])
172.18.0.4 - - [17/Apr/2020:02:04:11 +0000] "GET /search/?zip=11218 HTTP/1.0" 200 7392 "-" "curl/7.67.0" "-"
INFO:should_flask:querystring: ImmutableMultiDict([('zip', '11212'), ('hello', 'i')])
172.18.0.4 - - [17/Apr/2020:02:04:13 +0000] "GET /search/?zip=11212&hello=i HTTP/1.0" 200 7392 "-" "curl/7.67.0" "-"
ERROR:root:Invalid data: ImmutableMultiDict([('zip', '1121')]) : nota5digitzip
172.18.0.4 - - [17/Apr/2020:02:04:15 +0000] "GET /search/?zip=1121 HTTP/1.0" 200 1374 "-" "curl/7.67.0" "-"
ERROR:root:Invalid data: ImmutableMultiDict([('zip', 'mickeymouse')]) : nota5digitzip
172.18.0.4 - - [17/Apr/2020:02:04:17 +0000] "GET /search/?zip=mickeymouse HTTP/1.0" 200 1374 "-" "curl/7.67.0" "-"

Expected output:
./test_cases.sh
Default
HTTP/1.1 200 OK
2 params
HTTP/1.1 200 OK
short zip
HTTP/1.1 200 OK
text vs int
HTTP/1.1 200 OK

MULTILINE-COMMENT
