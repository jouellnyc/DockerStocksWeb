# Historical Stock Data (With Growth Rates) 
![Stocks](non-app/stock_peek.gif)

## Why Do this?
Once you Crawl and Index all the stocks you like, you can issue a  query like "Tell me all the Companies with a Market Cap of more than 2 Billion, 4 year CAGR for Revenue of 20% and at least 200 Million dollar of Revenue TTM or whatever metric you've crawled and indexed. Or simply query to see the details of the stock you are researching.

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
git clone https://github.com/jouellnyc/DockerStocksWeb
cd DockerStocksWeb
docker-compose -f docker-compose.local.yaml  up -d
```

### Setup 

Enter the flask container:

```
./non-app/master.enter.sh flask
```

Set your  api_key from Alpha Vantage
```
cd /stocks/lib
vi ./crawler.py
```

Start testing a crawling -- (Example with debug=True):
```

nobody@85e2ddd5a534:/stocks/lib$ ./crawler.py -s  OKTA
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
mongodb@6fd40bdb8b08:/$ mongo
MongoDB shell version v3.6.8
connecting to: mongodb://127.0.0.1:27017
Implicit session: session { "id" : UUID("755643dd-801e-4d72-bfd0-30c7728f6fd9") }
MongoDB server version: 3.6.8
Server has startup warnings: 
2021-09-26T15:14:41.888+0000 I CONTROL  [initandlisten] 
2021-09-26T15:14:41.888+0000 I CONTROL  [initandlisten] ** WARNING: Access control is not enabled for the database.
2021-09-26T15:14:41.888+0000 I CONTROL  [initandlisten] **          Read and write access to data and configuration is unrestricted.
2021-09-26T15:14:41.888+0000 I CONTROL  [initandlisten] 
> show dbs
admin   0.000GB
config  0.000GB
local   0.000GB

```
Point your browser to http://$YOUR_IP and search for OKTA or 

http://$YOUR_IP/search/?stock=OKTA


## Architecture
Nginx will listen on your local host's port 80.

Flask and Mongodb will be on the same bridged docker network reachable by docker names.

## Requirements
- Git/Docker/Docker-compose/MongoDB(Optionally at Mongo)
- https://www.alphavantage.co/ -- Free Api key


This project defaults to a local MongoDB -- up and running after 'git clone'.

To use AWS:
- Change Mode to 'AWS' in mongo_infra_prod_config.yaml
- You'd need a custom Mongo Atlas entry specific to your account  -- (See https://www.mongodb.com/python) 
- If using https://github.com/jouellnyc/AWS/tree/master/boto3/blue_green_deploy, modify the variable 'user_data_file' in 'prod_vpc_lb_builder.py' to point to  user_data.http.AWS.sh

To fully deploy automatically:
- You'll need to setup AWS Secret Manager entries as well. See user_data.http.AWS.sh and getSecret.py.

## Warnings
- This project is mean to be a part of a DevOps/Python learning project and is unsecured by default.
- Images built from this report are likely to be large and cumbersome with Container Orchestration.
- For a while, alphavantage free api keys were not, working, I have not spent much time on this project recently, your mileage may vary.

