#!/usr/bin/python3


import sys
sys.path.append('../lib/')

import mongodb
mg = mongodb.MongoCli()

for x in mg.dbh.find( {'Stock' : {"$exists": True}} , {'_id' : 0} ): 
    if '^' in x['Stock']:
        print(mg.dbh.remove(x))
