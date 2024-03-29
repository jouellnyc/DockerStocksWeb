#!/usr/bin/env python3

import argparse
import sys
import random, string
import traceback
from pprint import pprint
import datetime
import time


from alpha_vantage.fundamentaldata import FundamentalData
from pymongo.errors import PyMongoError
from millify import millify
import pandas as pd

from mongodb import MongoCli, StockDoesNotExist
from requestwrap import err_web
from requests.exceptions import HTTPError

""" All Assignment of df Slices """
pd.options.mode.chained_assignment = None


class NotOldEnough(Exception):
    pass

class PassOnErrorStock(Exception):
    pass

class GoodCrawl(Exception):
    pass

class ZeroRevenue(Exception):
    pass

class ZeroNetIncome(Exception):
    pass

class BadRevenueData(Exception):
    pass

class BadIncomeData(Exception):
    pass

class FlywheelError(Exception):
    pass


def mk_pretty(num):
    """ Pretty print Growth Rate """
    return "%.2f" % (num * 100)


def gen_crawlid():
    """ Generate a short id string for each crawler """
    return "".join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
        for _ in range(10)
    )


def cut(x):
    """ Cut off part of the string """
    return x.rpartition("-")[0].rpartition("-")[0]


def add_str(string):
    """ Add Years """
    return string + "Years"


def get_stock_data(stock):
    """ Simple query for stock data """
    try:
        data = mg.lookup_stock(stock)
    except ValueError:
        return False, False
    else:
        return True, data


def sleepit(pause):
    """ sleep for x seconds """
    print(f"Sleeping for {pause} seconds")
    time.sleep(pause)


def stock_is_crawled_recently(stock_data, old_enough=None):
    """ See if we crawled stock recently """
    old_enough = 7
    date_crawled = stock_data["DateCrawled"]
    difference = datetime.datetime.utcnow() - date_crawled
    # duration_in_s = difference.total_seconds()
    # hours = divmod(duration_in_s, 3600)[0]
    return difference.days <= old_enough


def GetNextStockBatch(count=0, max=5, pause=60):
    """ Pull down a batch of Stock to Crawl         """
    """ Try 'max' times to get it w/a 'pause' delay """
    """ before raising a FlywheelError              """

    try:
        #TBD: Can we please stop this hard code and put it in a yaml?
        stock_json = err_web("http://flywheel.justgrowthrates.com:9001/stocks/").json()
        stocks = stock_json["NextBatch"]

    except HTTPError:
        if count == max:
            raise FlywheelError
        print(f"Retrying Flywheel in {pause} s")
        time.sleep(pause)
        count += 1
        GetNextStockBatch(count, max=max, pause=pause)
    return stocks


def DecidetoCrawl(stock, force_new_all=None, force_retry_errors=None):

    """ if force_new_all is True, crawl the doc """
    """ otherwise check it's crawl date         """

    debug = True

    print("Deciding to Crawl or Not...")

    try:
        _, stock_data = get_stock_data(stock)

    except StockDoesNotExist:
        print("Stock DNE - crawling")
        CrawlStock(stock)

    if debug:
        print("data:\n", stock_data)


    if force_new_all:
        print(f"Crawling and Indexing {stock} - due to force_new_all ")
        CrawlStock(stock)

    if force_retry_errors:
        print(f"Crawling and Indexing {stock} due to force_retry_errors")
        CrawlStock(stock)
    else:
        try:
            print("Force_retry_errors is False...")
            print("Checking for Errors...")
            if stock_data["Error"] is None:
                print("Passing: force_retry_errors is False and stock has errors")
                raise PassOnErrorStock
        except KeyError:
            print("No Errors, now checking Crawl Date...")
            if stock_is_crawled_recently(stock_data):
                print("...Passing: Not old enough and force_retry_errors is False")
                raise NotOldEnough
            else:
                print("...Crawling: Old Enough and has no error")
                CrawlStock(stock)


def CrawlStock(stock):

    print(f"Connecting to Alpha Vantage for {stock}")
    """ Pull Down Income Data from Alpha Vantage """
    income_data, stock_name = alpha.get_income_statement_annual(stock)
    if len(income_data) < 1:
        raise BadIncomeData
    else:
        income_data.replace("None", 0, inplace=True)

    try:
        currency = income_data["reportedCurrency"].values[0]
    except KeyError:
        currency = NA

    """ Setup our panda dataframe """
    df = income_data[["fiscalDateEnding", "totalRevenue", "netIncome"]]

    print("df:\n", df, "\n") if debug else None


    if (
        (df["totalRevenue"].iloc[0] == "0")
        or (df["totalRevenue"].iloc[0] == 0)
        or (df["totalRevenue"].iloc[-1] == "0")
        or (df["totalRevenue"].iloc[-1] == 0)
    ):
        raise ZeroRevenue

    if (
        (df["netIncome"].iloc[0] == "0")
        or (df["netIncome"].iloc[0] == 0)
        or (df["netIncome"].iloc[-1] == "0")
        or (df["netIncome"].iloc[-1] == 0)
    ):
        raise ZeroNetIncome


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

    df["Years_From"] = df["Years"] - last_year_value
    df["Years_From"] = df["Years_From"].apply(str)
    df["Years_From"] = df["Years_From"].apply(add_str)
    df = df.fillna(0)

    if debug:
        print("df:\n", df, "\n")

    if debug:
        print("df.to_dict\('records'\):\n")
        pprint(df.to_dict("records"))
        print("\n")

    """ Setup our mongo doc as a hash to prepare to send to Mongo """
    mongo_doc = {'Stock': stock, 'Error': None, 'Years': {}}

    """ millify() and mk_pretty() the data and re-arrange df """
    for year in df.to_dict("records"):

        if year["totalRevenue"] < 1:
            raise BadRevenueData

        mongo_doc["Years"][year["Years_From"]] = {
            "Date": year["fiscalDateEnding"],
            "Revenue": float(millify(year["totalRevenue"], precision=2)[:-1]),
            "RevDenom": millify(year["totalRevenue"], precision=2)[-1],
            "NetIncome": float(millify(year["netIncome"], precision=2)[:-1]),
            "NetIncDenom": millify(year["netIncome"], precision=2)[-1],
            "NetIncGrowth": float(mk_pretty(year["NetInc_Growth"])),
            "RevenueGrowth": float(mk_pretty(year["Revenue_Growth"])),
        }

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
    #market_cap is a string 'None', not the python None.
    if market_cap.startswith('None'):
        mongo_doc["Market_Cap"] = 'NA'
    else:
        mongo_doc["Market_Cap"] = millify(market_cap, precision=2)
        mongo_doc["Market_Cap_Denom"] = mongo_doc["Market_Cap"][-1]
        mongo_doc["Market_Cap"] = float(mongo_doc["Market_Cap"][:-1])

    #Wow. This is annoying
    try:
        PETTM = int(float(overview_data["TrailingPE"].values[0]))
    except ValueError:
        PETTM = NA

    try:
        price2sales = float(overview_data["PriceToSalesRatioTTM"].values[0])
    except ValueError:
        price2sales = NA

    try:
        price2book = float(overview_data["PriceToBookRatio"].values[0])
    except ValueError:
        price2book = NA

    try:
        book_value = float(overview_data["BookValue"].values[0])
    except ValueError:
        book_value = NA
    mongo_doc["BookValue"] = book_value


    """ Add each as a key:value pair ... """
    if revenue_ttm > 0:
        mongo_doc["RevTTM"] = millify(revenue_ttm, precision=2)
        mongo_doc["RevTTM_Denom"] = mongo_doc["RevTTM"][-1]
        mongo_doc["RevTTM"] = float(mongo_doc["RevTTM"][:-1])
    else:
        mongo_doc["RevTTM_Denom"] = "NA"
        mongo_doc["RevTTM"] = revenue_ttm

    mongo_doc["Currency"] = currency
    mongo_doc["TrailingPE"] = PETTM

    try:
        mongo_doc["PriceToSalesTTM"] = millify(price2sales, precision=2)
    except ValueError:
        mongo_doc["PriceToSalesTTM"] = NA

    try:
        mongo_doc["PriceToBookRatio"] = float(millify(price2book, precision=2))
    except ValueError:
        mongo_doc["PriceToBookRatio"] = NA

    mongo_doc["DateCrawled"] = datetime.datetime.utcnow()
    mongo_doc["Success"] = "Yes"
    mongo_doc["Crawled_By"] = my_crawlid

    if debug:
        print("mongo_doc:\n")
        pprint(mongo_doc)
        print("\n")

    """ And now we are ready to send the Data to Mongo """
    print(f"OK, Sending data to Mongo for {stock}\n")
    print(mg.replace_one_document( {"Stock": stock}, mongo_doc ))
    raise GoodCrawl


if __name__ == "__main__":

    format = "pandas"
    api_key ="None"
    my_crawlid = gen_crawlid()
    api_key = api_key or  my_crawlid.upper()
    alpha = FundamentalData(key=api_key, output_format=format, indexing_type="integer")
    NA ='NA'

    # Multiple crawlers will step on each other if set
    pause = 35
    debug = True
    force_new_all = False
    force_retry_errors = True


    parser = argparse.ArgumentParser()
    parser.description = "Get Stock Data and Return Growth Rates"
    parser.epilog = "Example: " + sys.argv[0] + " -m all"
    parser.add_argument("-s", "--stock")
    parser.add_argument("-m", "--mode", choices=["date", "all", "flywheel", "last"])
    namespace = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 2:
        parser.print_usage()
        sys.exit(1)

    try:

        """ Connect to Mongo... or not """
        mg = MongoCli()

        """ mode == all  -- Crawl from the first alphabetically    """
        """ mode == date -- Crawl the oldest stocks first          """
        """ mode == last -- Crawl from Last Known, Alphabetically  """
        """ flywheel -- use a micro service                        """
        """ -s stock - crawl one stock                             """

        if namespace.mode:

            if namespace.mode == "all":
                all_stocks = mg.dump_all_stocks()
            elif namespace.mode == "date":
                all_stocks = mg.dump_all_stocks_sorted_by_date()
            elif namespace.mode == "flywheel":
                all_stocks = GetNextStockBatch()
            elif namespace.mode == "last":
                all_stocks = mg.dump_recent_stocks()

        elif namespace.stock:

            all_stocks = [namespace.stock]
    except PyMongoError as e:
        print("Mongodb issue: ", e)
        sys.exit(1)

    print(f"{all_stocks} Mode: {namespace.mode}") if debug else None

    count = 1
    print(all_stocks)

    date = datetime.datetime.utcnow()
    for stock in all_stocks:
        try:

            print(f"==== Trying {stock} - {count}")
            DecidetoCrawl(
                stock,
                force_new_all=force_new_all,
                force_retry_errors=force_retry_errors,
            )

        except PassOnErrorStock:
            continue

        except NotOldEnough:
            continue

        except FlywheelError:
            continue

        except GoodCrawl:
            print(f"OK - Updating {stock} as the lastest stock\n")
            print(mg.update_latest_stock(stock))
            sleepit(pause)
            continue

        except ZeroRevenue:
            msg = f"Zero Revenue - {date} - "
            mg.update_as_error(stock, msg)
            print(msg) if debug else None
            print(f"Updating {stock} as the lastest stock\n")
            print(mg.update_latest_stock(stock))
            sleepit(pause)
            continue

        except ZeroNetIncome:
            msg = f"Zero NetIncome - {date} - "
            mg.update_as_error(stock, msg)
            print(msg) if debug else None
            print(f"Updating {stock} as the lastest stock\n")
            print(mg.update_latest_stock(stock))
            sleepit(pause)
            continue

        except BadIncomeData:
            msg = f"Bad  NetIncome - {date} - "
            mg.update_as_error(stock, msg)
            print(msg) if debug else None
            print(f"Updating {stock} as the lastest stock\n")
            print(mg.update_latest_stock(stock))
            sleepit(pause)
            continue

        except KeyError as e:
            msg = f"Likely a Data Issue - {date} -"
            mg.update_as_error(stock, f"{msg} -- {e}")
            print(msg)
            print(f"Updating {stock} as the lastest stock\n")
            print(mg.update_latest_stock(stock))
            sleepit(pause)
            continue

        except ValueError as e:

            if "Thank you" in str(e.args):
                print("Error: Hit Api limit")
                time.sleep(7200)
            elif "no return was given" in str(e.args):
                msg = "No Data Returned from Api"
                mg.update_as_error(stock, msg)
                print(f"Updating {stock} as the lastest stock\n")
                mg.update_latest_stock(stock)
                print(msg)
                sleepit(pause)
                continue
            else:
                msg = f"Unhandled Value Error - {date} -"
                mg.update_as_error(stock, f"{msg} -- {e}")
                print(f"Updating {stock} as the lastest stock\n")
                mg.update_latest_stock(stock)
                print("Full TB: ", traceback.format_exc())
                sleepit(pause)
                continue

        except PyMongoError as e:
            print("Mongodb issue: - Quitting Crawl", e)
            sys.exit(1)

        except Exception as e:
            print("UnExpected Error")
            print(type(e), e)
            print(traceback.format_exc())
            sleepit(pause)
            continue

        finally:
            count += 1




