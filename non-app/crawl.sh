#!/bin/bash

COUNTER=0
SLEEP=62

STOCKS=nasdaq.txt

while read stk; do echo == $stk ==;


if [ -e /tmp/$stk ]; then

        ls -l /tmp/$stk
	echo "Already crawled $stk"

else

	OUT=$(../lib/crawler.py $stk)
	if echo $OUT | grep already; then
	    touch /tmp/$stk
	elif echo $OUT | grep -i 'no data'; then
	    echo sleep $SLEEP
	    sleep $SLEEP
	    touch /tmp/$stk
	    echo $stk >> remove.txt
	elif echo $OUT | grep -i 'likely a data issue'; then
	    touch /tmp/$stk
	    echo $stk >> remove.txt
	elif echo $OUT | grep -i 'limit'; then
	    echo 'hit api limit'
	    exit
	else

	    let COUNTER=COUNTER+1
	    echo = $COUNTER =

	    if [ $COUNTER -eq 400 ]; then
		exit
	    fi

	    echo sleep $SLEEP
	    sleep $SLEEP
	fi


fi


done < $STOCKS 
