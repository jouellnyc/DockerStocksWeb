
# Historical Stock Data (With Growth Rates) 
![Stocks](stock_peek.gif)

## Why Do this?
Once you Crawl and Index all the stocks you like, you can issue a  query like "Tell me all the Companies with a Market Cap of more than 200 Million, 4 year CAGR for Revenue of 15%, and at least 20 Million dollar of Revenue TTM/etc/etc. Most Stock Screeners don't include Growth Rates 

```
In [39]: for x in collh.find( {"MC.Val" : {"$gt" : 200 }, "MC.Den" : 'Mil',  "revenue_Growth.4" : {"$gte" : 15}, "revenue_Growth.3" : {"$gte" : 15
    ...: },"revenue_Growth.2" : {"$gte" : 15}, "revenue_Growth.1" : {"$gte" : 15},  "RevTTM.Val" : {"$gte" : 20}, 'revenue.2015.Val' : {"$gte" : 2
    ...: 0},'revenue.2016.Val' : {"$gte" : 20}, 'revenue.2017.Val' : {"$gte" : 20}, 'revenue.2018.Val' : {"$gte" : 20}}, {"Stock" : 1, "MC.Val" :
    ...: 1, "revenue_Growth.4" : 1 ,   "_id" : 0 } ):
    ...:     print(x)
    ...:
    ...:
{'Stock': 'AKU', 'MC': {'Val': 251.24}, 'revenue_Growth': {'4': 66.18}}
{'Stock': 'ATRS', 'MC': {'Val': 465.06}, 'revenue_Growth': {'4': 28.34}}
{'Stock': 'AXGN', 'MC': {'Val': 510.28}, 'revenue_Growth': {'4': 40.57}}
{'Stock': 'BCOR', 'MC': {'Val': 493.84}, 'revenue_Growth': {'4': 57.15}}
{'Stock': 'BOOM', 'MC': {'Val': 516.64}, 'revenue_Growth': {'4': 24.23}}
{'Stock': 'CDXC', 'MC': {'Val': 277.91}, 'revenue_Growth': {'4': 20.43}}
{'Stock': 'CERS', 'MC': {'Val': 871.62}, 'revenue_Growth': {'4': 28.66}}
{'Stock': 'EBIX', 'MC': {'Val': 558.3}, 'revenue_Growth': {'4': 21.61}}
{'Stock': 'GNMK', 'MC': {'Val': 876.43}, 'revenue_Growth': {'4': 22.25}}

and so on.....

```


## Installing Locally
```
git clone https://github.com/jouellnyc/stocks_web
cd stocks_web 
docker-compose -f docker-compose.local.yaml  up -d
```

### Setup 
```
Enter the flask container and start crawling:

 ./non-app/master.enter.sh flask

nobody@cb9eb7ca0e0b:/$ /stocks/lib/crawler.py -s GOOG
Retrieving HTML for  GOOG
Parsing HTML
Pulling Data out of HTML

GOOG had 73,590.0 M Revenue in 2015 4 GR Rate =  21.69%
<szip>

The DB 'Stocks' will be auto created in the local Mongo Container

./non-app/master.enter.sh mongodb 

> show dbs
Stocks  0.000GB
admin   0.000GB
config  0.000GB
local   0.000GB

Point your browser to http://$YOUR_IP and search for GOOG or 
http://$YOUR_IP/search/?stock=GOOG

```

## Architechure
Nginx will listen on the local hosts port 80

Flask and Mongodb will be on the same bridged docker network reachable by docker names

## Requirements
git/docker/docker-compose/optionally a MongoDB hosted at Mongo



