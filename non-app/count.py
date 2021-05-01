#!/usr/bin/python3

import sys
sys.path.append('../lib/')

import mongodb
mg = mongodb.MongoCli()

for x in mg.dbh.find({'Success' : {"$exists": True } }): 
    print(x['Stock'], x['DateCrawled'])

"""
for x in mg.dbh.find({'Error' : {"$exists": True } }): 
    print(x)


for x in mg.dbh.find({'Stock' : {"$exists": True} }): 
    print(x['Stock'])


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

############

def sa(how_to_sort):
    return sorted([ (x['Stock'],x['DateCrawled'])  
            for x in mg.dbh.find({'DateCrawled' : {"$exists": True} }) 
           ], key=how_to_sort)
           
def by_date(stock):
    return stock[1]   

for x in sa(how_to_sort=by_date):
    print(x)

"""
