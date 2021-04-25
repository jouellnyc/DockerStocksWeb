#!/usr/bin/python3

import mongodb
mg = mongodb.MongoCli()

for x in mg.dbh.find({'Stock' : {"$exists": True} }): 
    print(x['Stock'])

"""
for x in mg.dbh.find({'DateCrawled' : {"$exists": False } }): 
    print (x)


for x in mg.dbh.find(): 
    print(x)
    



for x in mg.dbh.find({'Stock' : {"$exists": True} }): 
    if '\n' in x['Stock']:
        #ns = x['Stock'].rstrip()
        #mg.replace_one( {'Stock': x},{'Stock': ns} )
        print(x)
    
for x in mg.dbh.find(): 
    try:
        print (x['Stock'],end='')
    except KeyError:
        print ('oh',x)
"""
