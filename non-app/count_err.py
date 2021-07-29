#!/usr/bin/python3

import sys
sys.path.append("../lib/")

import mongodb
mg = mongodb.MongoCli()

#for x in mg.dbh.find({'Error' : {"$exists": True } }): 
for x in mg.dbh.find( {'Error' : {"$ne": None }}): 
    print(x)
