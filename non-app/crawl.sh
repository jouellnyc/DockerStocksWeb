#!/bin/bash

SLEEP=62
COUNTER=0
MAX=400

STOCKS=nasdaq.txt

while read stk; do echo == $stk ==;


if [ -e /tmp/$stk ]; then

        ls -l /tmp/$stk
	echo "Already crawled $stk"

else

	date
	OUT=$(../lib/crawler.py $stk | tee -a "${0}"_main_crawl.log)
	if echo $OUT | grep -i 'limit'; then
	    echo 'hit api limit'
	    sleep $SLEEP
	elif echo $OUT | grep -i 'is already in Mongo'; then
	    touch /tmp/$stk
	elif echo $OUT | grep -i 'unhandled Value Error'; then
	    touch /tmp/$stk
	    sleep $SLEEP
	elif echo $OUT | grep -i 'no data'; then
	    touch /tmp/$stk
	    sleep $SLEEP
	elif echo $OUT | grep -i 'likely a data issue'; then
	    touch /tmp/$stk
	    sleep $SLEEP
	elif echo $OUT | grep -i 'sending'; then

	    touch /tmp/$stk

	    let COUNTER=COUNTER+1
	    echo = $COUNTER =

	    if [ $COUNTER -eq $MAX ]; then
       		echo "hit $MAX"
		      exit
	    fi

	    sleep $SLEEP

	fi


fi

done < <(tac $STOCKS
