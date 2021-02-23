#!/bin/bash

SLEEP=62
COUNTER=0
MAX=400

STOCKS=nasdaq.txt

while read stk; do echo == $stk ==;


	date
	OUT=$(../lib/crawler.py $stk | tee -a "${0}"_main_crawl.log)

	let COUNTER=COUNTER+1
	echo = $COUNTER =

	if [ $COUNTER -eq $MAX ]; then
       	    echo "hit $MAX"
	    exit
	fi

	sleep $SLEEP

done < $STOCKS
