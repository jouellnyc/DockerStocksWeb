#!/usr/bin/python3


import sys
sys.path.append('../lib/')

import mongodb
mg = mongodb.MongoCli()

for x in mg.dbh.find( {'Stock' : {"$exists": True}} , {'_id' : 0} ): 
    if '\n' in x['Stock']:
        stock = x['Stock']
        ns    = stock.strip()
        print(ns,stock)
        print({'Stock': stock},{'Stock': ns})
        print(mg.dbh.replace_one( {'Stock': stock},{'Stock': ns} ))
