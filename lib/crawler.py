#!/usr/bin/python3

import sys
import traceback

from alpha_vantage.fundamentaldata import FundamentalData
from pymongo.errors import ServerSelectionTimeoutError
from millify import millify
import pandas as pd
""" All Assignment of df Slices """
pd.options.mode.chained_assignment = None

from mongodb import MongoCli

api_key = "ZZZZZZZZZZZ"
format = "pandas"

alpha = FundamentalData(key=api_key, output_format=format, indexing_type="integer")

def mk_pretty(num):
    """ Pretty print Growth Rate """
    # return "%.2f" % (num * 100) + "%"
    return "%.2f" % (num * 100)

def cut(x):
    return x.rpartition("-")[0].rpartition("-")[0]

def add_str(string):
    return string + "Years"

def main(stock):

    try:
        """ Pull Down Income Data from Alpha Vantage """
        income_data, stock_name = alpha.get_income_statement_annual(stock)
        income_data.replace("None", 0, inplace=True)
        currency = income_data["reportedCurrency"].values[0]

        """ Setup our panda dataframe """
        df = income_data[["fiscalDateEnding", "totalRevenue", "netIncome"]]

        """
        df looks like this now:
                  fiscalDateEnding totalRevenue   netIncome
        index
        0           2019-12-31     57300000       -808500000
        1           2018-12-31     42500000       -72900000
        2           2017-12-31     32500000       -62900000
        3           2016-12-31     22500000       -52900000
        4           2015-12-31     12500000       -42900000
        """

        """  Set data to numbers from strings """
        df[["totalRevenue", "netIncome"]] = df[["totalRevenue", "netIncome"]].apply(
            pd.to_numeric
        )

        """ Calculate the x-Year Growth Rate for Revenue and Net Income """
        """ The growth values are relative to the last year of data     """

        # Trim the year value to get just the year
        df["Years"] = df["fiscalDateEnding"].apply(cut).apply(pd.to_numeric)
        last_year_value = df["Years"].iloc[-1]
        last_rev_value = int(df.totalRevenue.iloc[-1])
        last_ninc_value = int(df.netIncome.iloc[-1])

        df["Revenue_Growth"] = (last_rev_value / df["totalRevenue"]) ** (
            1 / (last_year_value - df["Years"])
        ) - 1

        df["NetInc_Growth"] = (last_ninc_value / df["netIncome"]) ** (
            1 / (last_year_value - df["Years"])
        ) - 1

        #df["Years_From"] = str(df['Years'] - last_year_value) + 'year'
        df["Years_From"] = df['Years']  - last_year_value
        df["Years_From"] = df["Years_From"].apply(str)
        df["Years_From"] = df["Years_From"].apply(add_str)

        """
        df looks like this now:
                    fiscalDateEnding  totalRevenue    netIncome  Years  Revenue_Growth  NetInc_Growth
        index
        0           2019-12-31      161857000000  34343000000     2019     0.212086       0.203908
        1           2018-12-31      136819000000  30736000000     2018     0.221939       0.234225
        2           2017-12-31      110855000000  12662000000     2017     0.215847      -0.119927
        3           2016-12-31      90272000000  19478000000      2016     0.203803       0.191461
        4           2015-12-31       74989000000  16348000000     2015     0.000000       0.000000


        df.to_dict('records') looks like:

        [{'fiscalDateEnding': '2020-01-31', 'totalRevenue': 10918000000, 'netIncome': 2796000000, 'Revenue_Growth': 0.1685870595963277, 'NetInc_Growth': 0.35417178008219086},
        {'fiscalDateEnding': '2019-01-31', 'totalRevenue': 11716000000, 'netIncome': 4141000000, 'Revenue_Growth': 0.23661756024638625, 'NetInc_Growth': 0.6115144899902718},
        {'fiscalDateEnding': '2018-01-31', 'totalRevenue': 9714000000, 'netIncome': 3047000000, 'Revenue_Growth': 0.24696268563501333, 'NetInc_Growth': 0.7056949396757586},
        {'fiscalDateEnding': '2017-01-31', 'totalRevenue': 6910000000, 'netIncome': 1666000000, 'Revenue_Growth': 0.17441113625768545, 'NetInc_Growth': 0.6472264716364702},
        {'fiscalDateEnding': '2016-01-31', 'totalRevenue': 5010000000, 'netIncome': 614000000, 'Revenue_Growth': 0.0, 'NetInc_Growth': 0.0}]
        """

        print(df)

        print(df.to_dict('records'))

        """ Setup our mongo doc as a hash to prepare to send to Mongo """
        mongo_doc = {}
        mongo_doc["Stock"] = stock
        mongo_doc["Years"] = {}

        """ millify() and mk_pretty() the data and re-arrange df """
        for year in df.to_dict("records"):
            #mongo_doc["Years"][year["fiscalDateEnding"]] = {
            mongo_doc["Years"][ year["Years_From"] ] =  {

                "Date"          : year["fiscalDateEnding"],
                "Revenue"       : millify(float(year["totalRevenue"]), precision=2)[:-1],
                "RevDenom"      : millify(year["totalRevenue"], precision=2)[-1],
                "NetIncome"     : millify(float(year["netIncome"]), precision=2)[:-1],
                "NetIncDenom"   : millify(year["netIncome"], precision=2)[-1],
                "NetIncGrowth"  : float(mk_pretty(year["NetInc_Growth"])),
                "RevenueGrowth" : float(mk_pretty(year["Revenue_Growth"])),
            }

        """
        mongo_doc looks like this now:
        { 'Stock': 'NVDA',

        'Years':
        {'2020-01-31': {'Revenue': '10.92B', 'NetIncome': '2.8B', 'NetIncGrowth': '35.42%', 'RevenueGrowth': '16.86%'},
         '2019-01-31': {'Revenue': '11.72B', 'NetIncome': '4.14B', 'NetIncGrowth': '61.15%', 'RevenueGrowth': '23.66%'},
         '2018-01-31': {'Revenue': '9.71B', 'NetIncome': '3.05B', 'NetIncGrowth': '70.57%', 'RevenueGrowth': '24.70%'},
         '2017-01-31': {'Revenue': '6.91B', 'NetIncome': '1.67B', 'NetIncGrowth': '64.72%', 'RevenueGrowth': '17.44%'},
         '2016-01-31': {'Revenue': '5.01B', 'NetIncome': '614M', 'NetIncGrowth': '0.00%', 'RevenueGrowth': '0.00%'}}
        }

        """

        print(mongo_doc)

        """ Pull Down Overview Data from Alpha Vantage """
        overview_data, stock_name = alpha.get_company_overview(stock)
        ##print(overview_data)

        """ Pull out Each value and millify() """
        revenue_ttm = float(overview_data["RevenueTTM"].values[0])
        market_cap = overview_data["MarketCapitalization"].values[0]
        PETTM = int(float(overview_data["TrailingPE"].values[0]))
        price2sales = float(overview_data["PriceToSalesRatioTTM"].values[0])
        price2book = float(overview_data["PriceToBookRatio"].values[0])
        book_value = overview_data["BookValue"].values[0]
        if book_value.startswith('None'):
            mongo_doc["BookValue"] = 0.0
        else:
            mongo_doc["BookValue"] = float(book_value)

        """ Add each as a key:value pair ... """
        if revenue_ttm > 0:
            mongo_doc["RevTTM"] = millify(revenue_ttm, precision=2)
            mongo_doc["RevTTM_Denom"] = mongo_doc["RevTTM"][-1]
            mongo_doc["RevTTM"] = float(mongo_doc["RevTTM"][:-1])
        else:
            mongo_doc["RevTTM_Denom"] = "NA"
            mongo_doc["RevTTM"] = revenue_ttm


        mongo_doc["Market_Cap"] = millify(market_cap, precision=2)
        mongo_doc["Market_Cap_Denom"] = mongo_doc["Market_Cap"][-1]
        mongo_doc["Market_Cap"] = float(mongo_doc["Market_Cap"][:-1])

        mongo_doc["Currency"] = currency
        mongo_doc["TrailingPE"] = float(PETTM)
        mongo_doc["PriceToSalesTTM"] = float(millify(price2sales, precision=2))
        mongo_doc["PriceToBookRatio"] = float(millify(price2book, precision=2))

        """
        mongo_doc now looks like this:
        {'Stock': 'NVDA',
        'Years':
        {'2020-01-31': {'Revenue': '10.92B', 'NetIncome': '2.8B', 'NetIncGrowth': '35.42%', 'RevenueGrowth': '16.86%'},
         '2019-01-31': {'Revenue': '11.72B', 'NetIncome': '4.14B', 'NetIncGrowth': '61.15%', 'RevenueGrowth': '23.66%'},
         '2018-01-31': {'Revenue': '9.71B',  'NetIncome': '3.05B', 'NetIncGrowth': '70.57%', 'RevenueGrowth': '24.70%'},
         '2017-01-31': {'Revenue': '6.91B', 'NetIncome': '1.67B', 'NetIncGrowth': '64.72%', 'RevenueGrowth': '17.44%'},
         '2016-01-31': {'Revenue': '5.01B', 'NetIncome': '614M', 'NetIncGrowth': '0.00%', 'RevenueGrowth': '0.00%'}},
        'RevTTM': '14.78B',
        'BookValue': 24.772,
        'Market Cap': '339.52B',
        'Currency': 'USD',
        'TrailingPE': 89,
        'PriceToSalesTTM': '21.75',
        'PriceToBookRatio': '20.76'}


        >>> pprint.pprint( mg.lookup_stock('AACG') )
        {'BookValue': 'None',
         'Market Cap': '42.32M',
         'PriceToBookRatio': '1.02',
         'PriceToSalesTTM': '1.58',
         'RevTTM': '0',
         'Stock': 'AACG',
         'TrailingPE': 0,
         'Years': {'2015-12-31': {'NetIncGrowth': '0.00%',
                                  'NetIncome': '26.05M',
                                  'Revenue': '417.14M',
                                  'RevenueGrowth': '0.00%'},
                   '2016-12-31': {'NetIncGrowth': 'nan%',
                                  'NetIncome': '-9.72M',
                                  'Revenue': '472.39M',
                                  'RevenueGrowth': '6.42%'},
                   '2017-12-31': {'NetIncGrowth': '4.39%',
                                  'NetIncome': '29.63M',
                                  'Revenue': '490.06M',
                                  'RevenueGrowth': '5.52%'},
                   '2018-12-31': {'NetIncGrowth': '139.35%',
                                  'NetIncome': '854.93M',
                                  'Revenue': '1.34M',
                                  'RevenueGrowth': '-76.20%'},
                   '2019-12-31': {'NetIncGrowth': 'nan%',
                                  'NetIncome': '-122.25M',
                                  'Revenue': '97.77M',
                                  'RevenueGrowth': '-25.19%'}}}

        """

    except Exception:
        raise
    else:
        """ And now we are ready to send the Data to Mongo """
        print("OK, Sending to Mongo")
        #print(mongo_doc)
        mg = MongoCli()
        mg.dbh.insert_one(mongo_doc)


if __name__ == "__main__":

    # print('main')
    try:
        stock = sys.argv[1]
        #stock = 'amzn'
        main(stock)
    except ServerSelectionTimeoutError as e:
        print("Can't connect to Mongodb - Quitting Crawl", e)
        sys.exit(1)
    except KeyError as e:
        print("Likely a Data Issue")
        print("Not Sending to Mongo")
        # logging.warning
        print(type(e), e)
    except Exception as e:
        print("Uncaught handled Error")
        #print(type(e), e)
        print(traceback.format_exc())
        # logging.error
