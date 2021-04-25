#!/usr/bin/python3

import mongodb
mg = mongodb.MongoCli()

def sa(how_to_sort):
    return sorted([ (x['Stock'],x['DateCrawled'])  
            for x in mg.dbh.find({'DateCrawled' : {"$exists": True} }) 
           ], key=how_to_sort)
           
def by_date(stock):
    return stock[1]   

for x in sa(how_to_sort=by_date):
    print(x)
