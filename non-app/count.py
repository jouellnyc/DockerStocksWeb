#!/usr/bin/python3

import sys

sys.path.append("../lib/")

import mongodb

mg = mongodb.MongoCli()

def sa(how_to_sort):

    return sorted(
        [
            (x["Stock"], x["DateCrawled"], x["Crawled_By"])
                for x in mg.dbh.find({ "Crawled_By": {"$exists": True}})
        ], key=how_to_sort,
    )

def by_date(stock):
    return stock[1]


"""
for x in mg.dbh.find({ "Crawled_By": {"$exists": True}}):
    try:
        print(x["Stock"],x['Error'],x['Crawled_By'],x['DateCrawled'],x['Success'])
    except KeyError:
        print(x)



for x in sa(how_to_sort=by_date):
    try:
        print(x)
    except KeyError:
        pass

"""

for x in mg.dbh.find(): 
    try:
        print(x["Stock"],x['Error'],x['Success'])
    except KeyError:
        print(x)
