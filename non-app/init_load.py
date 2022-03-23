#!/usr/bin/env python3

import sys
sys.path.append('../lib/')

import time
import datetime

from mongodb import MongoCli
mg = MongoCli()

if __name__ == "__main__" :

    for file in [ 'nyse.txt', 'nasdaq.txt' ]:
        mg = MongoCli()
        for stock in open(f"../non-app/{file}",'r'):
            stock=stock.strip()
            if '^' in stock:
                continue
            date = datetime.datetime.utcnow()
            if mg.insert_one_document({'Stock': stock, 'DateCrawled':date, 'Error':'init'}):
                print(f"{stock} loaded ok")

