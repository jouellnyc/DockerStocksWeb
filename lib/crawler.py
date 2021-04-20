#!/usr/bin/python3

import sys
import traceback
from pprint import pprint
import datetime
import time

from alpha_vantage.fundamentaldata import FundamentalData
from pymongo.errors import ServerSelectionTimeoutError
from millify import millify
import pandas as pd

""" All Assignment of df Slices """
pd.options.mode.chained_assignment = None

from mongodb import MongoCli

api_key = "E2W484948FV3YIWS"

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

def stock_exists(stock, mg):
    try:
        data = mg.lookup_stock(stock)
    except ValueError:
        return False, False
    else:
        return True, data


def main(stock, force, force_new):

    """

        force = False will not crawl if stock is in the DB at all
        force = True  will try the date:

            force_new  = True  will crawl no matter how old the data is
            force_new  = False check's if it's X days old

        We pass on stock w/o crawl dates

    """

    debug = False

    _, data = stock_exists(stock, mg)


    if debug:
        print("data:\n", data)
        print("force force_new:", force, force_new)

    if data:

        print(f"{stock} is already in Mongo")
        if force is False:
            print("...Passing due to force option")
            return True
        else:
            print("...Trying due to force option")

            try:

                old_enough = 3
                date_crawled = data['DateCrawled']
                difference = datetime.datetime.utcnow() - date_crawled

                if force_new is False:
                    print("...Checking Crawl Date")
                    if difference.days >  old_enough:
                        print(f"Crawling and Indexing {stock} - Crawl date more than {old_enough} days")
                        pass
                    else:
                        print(f"Passing on {stock} - crawled within {old_enough} days")
                        return True
                else:
                    print(f"Crawling and Indexing {stock} - due to force_new")
                    pass


            except KeyError:

                print(f"{stock} does not have crawl date")
                print("passing")
                return True

            except TypeError:
                print(f"{stock} does not have data or has incorrect data")
                print("passing")
                return True

    else:
        print(f"{stock} was not already in Mongo -- continuing")
        pass

    try:

        print(f"Connecting to Alpha Vantage for {stock}")
        """ Pull Down Income Data from Alpha Vantage """
        income_data, stock_name = alpha.get_income_statement_annual(stock)
        income_data.replace("None", 0, inplace=True)
        currency = income_data["reportedCurrency"].values[0]

        """ Setup our panda dataframe """
        df = income_data[["fiscalDateEnding", "totalRevenue", "netIncome"]]

        try:
            if ((df["totalRevenue"].iloc[0] == "0") or (df["totalRevenue"].iloc[0] == 0) or (df["totalRevenue"].iloc[-1] == "0") or (df["totalRevenue"].iloc[-1] == 0)):
                print("0 Revenue -- Sending blank to Mongo")
                mg.dbh.insert_one({'Stock': stock})
                return False
        except IndexError as e:
            print(e)
            pass

        """
        else:
            print(df["totalRevenue"].iloc[0])
            print(type(df["totalRevenue"].iloc[0]))
            print(len(df["totalRevenue"].iloc[0]))
        """

        """
        df looks like this now:
                  fiscalDateEnding  totalRevenue    netIncome
        index
        0           2019-12-31  161857000000  34343000000
        1           2018-12-31  136819000000  30736000000
        2           2017-12-31  110855000000  12662000000
        3           2016-12-31   90272000000  19478000000
        4           2015-12-31   74989000000  16348000000
        """

        if debug:
            print("df:\n", df, "\n")

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

        df["Years_From"] = df['Years']  - last_year_value
        df["Years_From"] = df["Years_From"].apply(str)
        df["Years_From"] = df["Years_From"].apply(add_str)
        df = df.fillna(0)

        if debug:
            print("df:\n", df, "\n")

        """
        df looks like this now:
               fiscalDateEnding  totalRevenue    netIncome  Years  Revenue_Growth  NetInc_Growth Years_From
        index
        0           2019-12-31  161857000000  34343000000   2019        0.212086       0.203908     4Years
        1           2018-12-31  136819000000  30736000000   2018        0.221939       0.234225     3Years
        2           2017-12-31  110855000000  12662000000   2017        0.215847      -0.119927     2Years
        3           2016-12-31   90272000000  19478000000   2016        0.203803       0.191461     1Years
        4           2015-12-31   74989000000  16348000000   2015        0.000000       0.000000     0Years

        df.to_dict\('records'\) looks like this now:

        [{'NetInc_Growth': 0.20390827677878742,
          'Revenue_Growth': 0.21208612858558862,
          'Years': 2019,
          'Years_From': '4Years',
          'fiscalDateEnding': '2019-12-31',
          'netIncome': 34343000000,
          'totalRevenue': 161857000000},
         {'NetInc_Growth': 0.23422471699892022,
          'Revenue_Growth': 0.22193925428985017,
          'Years': 2018,
          'Years_From': '3Years',
          'fiscalDateEnding': '2018-12-31',
          'netIncome': 30736000000,
          'totalRevenue': 136819000000},
         {'NetInc_Growth': -0.11992671079483375,
          'Revenue_Growth': 0.21584681665796124,
          'Years': 2017,
          'Years_From': '2Years',
          'fiscalDateEnding': '2017-12-31',
          'netIncome': 12662000000,
          'totalRevenue': 110855000000},
         {'NetInc_Growth': 0.19146072914117918,
          'Revenue_Growth': 0.20380322447292265,
          'Years': 2016,
          'Years_From': '1Years',
          'fiscalDateEnding': '2016-12-31',
          'netIncome': 19478000000,
          'totalRevenue': 90272000000},
         {'NetInc_Growth': 0.0,
          'Revenue_Growth': 0.0,
          'Years': 2015,
          'Years_From': '0Years',
          'fiscalDateEnding': '2015-12-31',
          'netIncome': 16348000000,
          'totalRevenue': 74989000000}]
        """

        if debug:
            print("df.to_dict\('records'\):\n")
            pprint(df.to_dict('records'))
            print("\n")


        """ Setup our mongo doc as a hash to prepare to send to Mongo """
        mongo_doc = {}
        mongo_doc["Years"] = {}

        """ millify() and mk_pretty() the data and re-arrange df """
        for year in df.to_dict("records"):

            mongo_doc["Years"][ year["Years_From"] ] =  {

                "Date"          : year["fiscalDateEnding"],
                "Revenue"       : float(millify(year["totalRevenue"], precision=2)[:-1]),
                "RevDenom"      : millify(year["totalRevenue"], precision=2)[-1],
                "NetIncome"     : float(millify(year["netIncome"], precision=2)[:-1]),
                "NetIncDenom"   : millify(year["netIncome"], precision=2)[-1],
                "NetIncGrowth"  : float(mk_pretty(year["NetInc_Growth"])),
                "RevenueGrowth" : float(mk_pretty(year["Revenue_Growth"])),
            }

        """
        mongo_doc looks like this now:
        {'Years': {'0Years': {'Date': '2015-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 0.0,
                              'NetIncome': '16.35',
                              'RevDenom': 'B',
                              'Revenue': '74.99',
                              'RevenueGrowth': 0.0},
                   '1Years': {'Date': '2016-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 19.15,
                              'NetIncome': '19.48',
                              'RevDenom': 'B',
                              'Revenue': '90.27',
                              'RevenueGrowth': 20.38},
                   '2Years': {'Date': '2017-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': -11.99,
                              'NetIncome': '12.66',
                              'RevDenom': 'B',
                              'Revenue': '110.86',
                              'RevenueGrowth': 21.58},
                   '3Years': {'Date': '2018-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 23.42,
                              'NetIncome': '30.74',
                              'RevDenom': 'B',
                              'Revenue': '136.82',
                              'RevenueGrowth': 22.19},
                   '4Years': {'Date': '2019-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 20.39,
                              'NetIncome': '34.34',
                              'RevDenom': 'B',
                              'Revenue': '161.86',
                              'RevenueGrowth': 21.21}}}


        """
        if debug:
            print("mongo_doc: \n")
            pprint(mongo_doc)
            print("\n")



        """ Pull Down Overview Data from Alpha Vantage """
        overview_data, stock_name = alpha.get_company_overview(stock)
        if debug:
            print("overview_data: \n", overview_data, "\n")

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
        mongo_doc["DateCrawled"] = datetime.datetime.utcnow()

        """
        mongo_doc now looks like this:

        {'BookValue': 314.169,
         'Currency': 'USD',
         'Market_Cap': 1.28,
         'Market_Cap_Denom': 'T',
         'PriceToBookRatio': 6.02,
         'PriceToSalesTTM': 7.61,
         'RevTTM': 171.7,
         'RevTTM_Denom': 'B',
         'TrailingPE': 36.0,
         'Years': {'0Years': {'Date': '2015-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 0.0,
                              'NetIncome': '16.35',
                              'RevDenom': 'B',
                              'Revenue': '74.99',
                              'RevenueGrowth': 0.0},
                   '1Years': {'Date': '2016-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 19.15,
                              'NetIncome': '19.48',
                              'RevDenom': 'B',
                              'Revenue': '90.27',
                              'RevenueGrowth': 20.38},
                   '2Years': {'Date': '2017-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': -11.99,
                              'NetIncome': '12.66',
                              'RevDenom': 'B',
                              'Revenue': '110.86',
                              'RevenueGrowth': 21.58},
                   '3Years': {'Date': '2018-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 23.42,
                              'NetIncome': '30.74',
                              'RevDenom': 'B',
                              'Revenue': '136.82',
                              'RevenueGrowth': 22.19},
                   '4Years': {'Date': '2019-12-31',
                              'NetIncDenom': 'B',
                              'NetIncGrowth': 20.39,
                              'NetIncome': '34.34',
                              'RevDenom': 'B',
                              'Revenue': '161.86',
                              'RevenueGrowth': 21.21}}}
        """

        if debug:
            print("mongo_doc:\n")
            pprint(mongo_doc)
            print("\n")

    except Exception:
        raise
    else:
        """ And now we are ready to send the Data to Mongo """
        print(f"OK, Sending data to Mongo for {stock}\n")
        print(mg.dbh.update_one({'Stock': stock}, {'$set' : mongo_doc }, upsert=True))
        print(f"OK, Updating {stock} as the lastest stock\n")
        print(mg.update_latest_stock(stock))
        print(f"OK, sleeping for {pause} seconds")
        time.sleep(pause)

if __name__ == "__main__" :

    def pause_update_last(pause, msg):
        print(msg)
        print(f"Pausing for {pause} seconds")
        time.sleep(pause)
        mg.update_latest_stock(stock)

    force = True
    force_new = False
    pause = 35

    try:

        mg = MongoCli()
        all_stocks_raw  = mg.dump_all_stocks()
        all_stocks_dict  = {}
        for i,stock in enumerate(all_stocks_raw):
            all_stocks_dict[stock]=int(i)
        latest_stock = mg.get_latest_stock()
        latest_stock_index = all_stocks_dict[latest_stock]
        print(f"Latest Stock {latest_stock}")
        all_stocks_left = all_stocks_raw[latest_stock_index:]

    except ServerSelectionTimeoutError as e:
        print("Can't connect to Mongodb - Quitting Crawl", e)
        sys.exit(1)

    for stock in  all_stocks_left:
        try:
            print(f"==== Trying {stock}")
            main(stock,force=force, force_new=force_new)
        except KeyError:
            msg="Likely a Data Issue\nSending blank to Mongo"
            mg.dbh.insert_one({'Stock': stock})
            pause_update_last(pause, msg)
            pass
        except ValueError as e:
            if "Thank you" in str(e.args):
                msg=print("Error: Hit Api limit -- ", end='')
                pause_update_last(pause * 3, msg)
                pass
            elif "no return was given" in str(e.args):
                msg="No Data Returned from Api\nSending blank to Mongo"
                mg.dbh.insert_one({'Stock': stock})
                pause_update_last(pause, msg)
                pass
            else:
                msg="Unhandled Value Error\nSending blank to Mongo"
                mg.dbh.insert_one({'Stock': stock})
                pause_update_last(pause, msg)
                print(traceback.format_exc())
                pass
        except Exception as e:
            print("Unhandled Error")
            print(type(e), e)
            print(traceback.format_exc())
