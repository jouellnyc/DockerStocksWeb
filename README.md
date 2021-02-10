
# Historical Stock Data (With Growth Rates) 
![Stocks](stock_peek.gif)

## Why Do this?
Once you Crawl and Index all the stocks you like, you can issue a  query like "Tell me all the Companies with a Market Cap of more than 2 Billion, 4 year CAGR for Revenue of 20% and at least 200 Million dollar of Revenue TTM or whatever metric you've crawled and indexed.

```
>>> for x in mg.dbh.find( {'Market_Cap' : {"$gte" : 2}, "Market_Cap_Denom" : 'B', 'Years.4Years.RevenueGrowth' : {"$gte" : 20 }, 'RevTTM': {"$gte" : 200 } , 'RevTTM_Denom': 'M' }):
...     print(x['Stock'])
...
KNSL
ADC
ZEN
YEXT
AVLR
WHD
AYX

and so on.....

```


## Installing Locally
```
git clone https://github.com/jouellnyc/stocks_web
cd stocks_web 
docker-compose -f docker-compose.local.yaml  up -d
```

### Setup 

Enter the flask container:
```

 ./non-app/master.enter.sh flask

```


Start crawling -- (Example with debug=True):
```

nobody@85e2ddd5a534:/stocks/lib$ ./crawler.py OKTA
Connecting to Alpha Vantage for OKTA
df:
       fiscalDateEnding totalRevenue   netIncome
index
0           2020-01-31    586067000  -208913000
1           2019-01-31    399254000  -125497000
2           2018-01-31    259990000  -114359000
3           2017-01-31    160326000   -83509000
4           2016-01-31     85907000   -76302000

df:
       fiscalDateEnding  totalRevenue  netIncome  Years  Revenue_Growth  NetInc_Growth Years_From
index
0           2020-01-31     586067000 -208913000   2020        0.616143       0.286345     4Years
1           2019-01-31     399254000 -125497000   2019        0.668810       0.180409     3Years
2           2018-01-31     259990000 -114359000   2018        0.739659       0.224242     2Years
3           2017-01-31     160326000  -83509000   2017        0.866274       0.094454     1Years
4           2016-01-31      85907000  -76302000   2016        0.000000       0.000000     0Years

df.to_dict\('records'\):

[{'NetInc_Growth': 0.2863447725994137,
  'Revenue_Growth': 0.6161426026736712,
  'Years': 2020,
  'Years_From': '4Years',
  'fiscalDateEnding': '2020-01-31',
  'netIncome': -208913000,
  'totalRevenue': 586067000},
 {'NetInc_Growth': 0.18040889685668393,
  'Revenue_Growth': 0.6688100541398727,
  'Years': 2019,
  'Years_From': '3Years',
  'fiscalDateEnding': '2019-01-31',
  'netIncome': -125497000,
  'totalRevenue': 399254000},
 {'NetInc_Growth': 0.22424182793353276,
  'Revenue_Growth': 0.7396586685468718,
  'Years': 2018,
  'Years_From': '2Years',
  'fiscalDateEnding': '2018-01-31',
  'netIncome': -114359000,
  'totalRevenue': 259990000},
 {'NetInc_Growth': 0.09445361851589729,
  'Revenue_Growth': 0.8662739939702238,
  'Years': 2017,
  'Years_From': '1Years',
  'fiscalDateEnding': '2017-01-31',
  'netIncome': -83509000,
  'totalRevenue': 160326000},
 {'NetInc_Growth': 0.0,
  'Revenue_Growth': 0.0,
  'Years': 2016,
  'Years_From': '0Years',
  'fiscalDateEnding': '2016-01-31',
  'netIncome': -76302000,
  'totalRevenue': 85907000}]


mongo_doc:

{'Years': {'0Years': {'Date': '2016-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 0.0,
                      'NetIncome': '-76.3',
                      'RevDenom': 'M',
                      'Revenue': '85.91',
                      'RevenueGrowth': 0.0},
           '1Years': {'Date': '2017-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 9.45,
                      'NetIncome': '-83.51',
                      'RevDenom': 'M',
                      'Revenue': '160.33',
                      'RevenueGrowth': 86.63},
           '2Years': {'Date': '2018-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 22.42,
                      'NetIncome': '-114.36',
                      'RevDenom': 'M',
                      'Revenue': '259.99',
                      'RevenueGrowth': 73.97},
           '3Years': {'Date': '2019-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 18.04,
                      'NetIncome': '-125.5',
                      'RevDenom': 'M',
                      'Revenue': '399.25',
                      'RevenueGrowth': 66.88},
           '4Years': {'Date': '2020-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 28.63,
                      'NetIncome': '-208.91',
                      'RevDenom': 'M',
                      'Revenue': '586.07',
                      'RevenueGrowth': 61.61}}}


overview_data:
     Symbol     AssetType       Name   Description  ... DividendDate 
     ExDividendDate LastSplitFactor LastSplitDate
     NaN   OKTA  Common Stock  Okta, Inc  
     Okta, Inc. provides identity management platfo...  ...         
     None           None            None          None

[1 rows x 59 columns]

mongo_doc:

{'BookValue': 5.256,
 'Currency': 'USD',
 'Market_Cap': 36.56,
 'Market_Cap_Denom': 'B',
 'PriceToBookRatio': 53.82,
 'PriceToSalesTTM': '46.12',
 'RevTTM': 768.01,
 'RevTTM_Denom': 'M',
 'TrailingPE': 0.0,
 'Years': {'0Years': {'Date': '2016-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 0.0,
                      'NetIncome': '-76.3',
                      'RevDenom': 'M',
                      'Revenue': '85.91',
                      'RevenueGrowth': 0.0},
           '1Years': {'Date': '2017-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 9.45,
                      'NetIncome': '-83.51',
                      'RevDenom': 'M',
                      'Revenue': '160.33',
                      'RevenueGrowth': 86.63},
           '2Years': {'Date': '2018-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 22.42,
                      'NetIncome': '-114.36',
                      'RevDenom': 'M',
                      'Revenue': '259.99',
                      'RevenueGrowth': 73.97},
           '3Years': {'Date': '2019-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 18.04,
                      'NetIncome': '-125.5',
                      'RevDenom': 'M',
                      'Revenue': '399.25',
                      'RevenueGrowth': 66.88},
           '4Years': {'Date': '2020-01-31',
                      'NetIncDenom': 'M',
                      'NetIncGrowth': 28.63,
                      'NetIncome': '-208.91',
                      'RevDenom': 'M',
                      'Revenue': '586.07',
                      'RevenueGrowth': 61.61}}}


OK, Sending data to Mongo for OKTA

```


The DB 'Stocks' will be auto created in the local Mongo Container
```
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



