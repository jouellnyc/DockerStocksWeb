
# Historical Stock Data (With Growth Rates) 
![Stocks](stock_peek.gif)

## Why Do this?
Once you Crawl and Index all the stocks you like, you can issue a  query like "Tell me all the Companies with a Market Cap of more than 2 Billion, 4 year CAGR for Revenue of 20% and at least 20 Million dollar of Revenue TTM or whatever metric you've crawled and indexed.\

```
In [39]:
for x in mg.dbh.find( {'Market_Cap' : {"$gte" : 2}, "Market_Cap_Denom" : 'B', 'Years.4Years.RevenueGrowth' : {"$gte" : 20} }):
    print(x['Stock'])
KNSL
CDXC
CERS
EBIX
GNMK

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



