#!/usr/bin/python3

import re
import os
import sys
import argparse
import requests

import numpy as np
import pandas as pd
import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from bs4 import BeautifulSoup as bsoup

import mongodb


parser = argparse.ArgumentParser()
parser.description = "Get Stock Data and Return Growth Rates"
parser.epilog = "Example: " + sys.argv[0] + " -s AAPL -m local"
parser.add_argument("-s", "--stock")
parser.add_argument("-m", "--mode", help="(web or local)", choices=["local", "web"])
parser.add_argument("-k", "--keep", help="Keep data locally", action="store_true")
parser.add_argument("-p", "--plot", help="Save Plot Data", action="store_true")
namespace = parser.parse_args(sys.argv[1:])

if namespace.stock:
    stock = namespace.stock
else:
    stock = "GOOG"
ustock = stock.upper()

if namespace.keep:
    save_data_locally = True
else:
    save_data_locally = False

if namespace.plot:
    plot = True
else:
    plot = False

if namespace.mode:
    if namespace.mode == "local":
        web_mode = False
    elif namespace.mode == "web":
        web_mode = True
else:
    web_mode = True


mynan = np.nan
plot_dir = "data"
prefillna = "-9999"

""" URLS """
url_sales_ninc_eps = (
    "http://www.marketwatch.com/investing/stock/" + stock + "/financials/"
)
url_roic = "http://www.marketwatch.com/investing/stock/" + stock + "/company-profile"
url_fcf = (
    "http://www.marketwatch.com/investing/stock/" + stock + "/financials/cash-flow/"
)
url_bvps = (
    "https://www.gurufocus.com/term/Book+Value+Per+Share/"
    + stock
    + "/Book-Value-per-Share"
)
url_ni_ttm = "https://ycharts.com/companies/" + ustock + "/net_income_ttm"
url_pe_ttm = "https://www.gurufocus.com/stock/" + ustock
url_rev_ttm = "https://ycharts.com/companies/" + ustock + "/revenues_ttm"


""" Functions """


def err_web(url):
    """ Catch the Errors from the Web Connections             """
    """ All or nothing here: If not 200 OK - exit the program """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 "
            "Safari/537.36"
        }
        r = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        # raise_for_status() never execs if request.get above has connect error/timeouts
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Fatal Error Connecting:", errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
        sys.exit(1)
    else:
        return r


def get_web_data():
    """ Get Web Data """
    print("Retrieving HTML for ", stock)
    r_sales_ninc_eps = err_web(url_sales_ninc_eps)
    r_roic = err_web(url_roic)
    r_url_fcf = err_web(url_fcf)
    r_bvps = err_web(url_bvps)
    r_ni_ttm = err_web(url_ni_ttm)
    r_pe_ttm = err_web(url_pe_ttm)
    r_rev_ttm = err_web(url_rev_ttm)

    content_dict = {
        "sales": r_sales_ninc_eps,
        "fcf": r_url_fcf,
        "bvps": r_bvps,
        "roic": r_roic,
        "ninc": r_ni_ttm,
        "pe": r_pe_ttm,
        "revttm": r_rev_ttm,
    }
    return (
        r_sales_ninc_eps,
        r_roic,
        r_url_fcf,
        r_bvps,
        r_ni_ttm,
        r_pe_ttm,
        r_rev_ttm,
        content_dict,
    )


def make_soup(
    r_sales_ninc_eps, r_url_fcf, r_bvps, r_roic, r_ni_ttm, r_pe_ttm, r_rev_ttm
):
    """ Soup Setup """
    print("Parsing HTML")
    # Note: if you make it here, soup objects will be assigned ok
    soup_sales_ninc_eps = bsoup(r_sales_ninc_eps.content, "lxml")
    soup_fcf = bsoup(r_url_fcf.content, "lxml")
    soup_bvps = bsoup(r_bvps.content, "lxml")
    soup_roic = bsoup(r_roic.content, "lxml")
    soup_ni_ttm = bsoup(r_ni_ttm.content, "lxml")
    soup_pe_ttm = bsoup(r_pe_ttm.content, "lxml")
    soup_rev_ttm = bsoup(r_rev_ttm.content, "lxml")
    print("Pulling Data out of HTML")
    print("")
    return (
        soup_sales_ninc_eps,
        soup_fcf,
        soup_bvps,
        soup_roic,
        soup_ni_ttm,
        soup_pe_ttm,
        soup_rev_ttm,
    )


def calc_growth(last, first, period):
    """ Simple cagr calculation """
    return (last / first) ** (1 / period) - 1


def calc_cagr(years, data):
    """ Calcuate CAGR and make data frame """
    df = pd.DataFrame(
        {"years_strings": years, "years": [int(x) for x in years], "data": data}
    )
    # Use variables to help from going cross eyed
    last_data_value = df["data"][len(df["data"]) - 1]
    last_year_value = df["years"].max()
    growth = (last_data_value / df["data"]) ** (1 / (last_year_value - df["years"])) - 1
    return growth.apply(prettify_num)


def check_data(data):
    """ Return a Number and a Denomination Value (typically M or B) """

    """ Ensure each list is filled by returning NaN if no match     """

    if data is None:
        return None, None
    else:
        data_pat = re.compile("([-(]?[-(]?[0-9,]+\.?[0-9]{,3})([mMbB]?)")
        data_is_valid = data_pat.search(data)
        if data_is_valid:
            num = data_is_valid.group(1)
            denom = data_is_valid.group(2)
            brc_pat = re.compile("\(")
            braces = brc_pat.search(num)
            num = num.replace("(", "")
            num = num.replace(")", "")
            num = num.replace(",", "")

            if denom:
                denom_val = denom
            else:
                denom_val = mynan

            if braces:
                neg_pat = re.compile("-")
                is_neg_already = neg_pat.search(num)
                if is_neg_already:
                    return float(num), denom_val
                else:
                    return -float(num), denom_val
            else:
                return float(num), denom_val
        else:
            return mynan, mynan


def check_growth_rate(data_name, data_master, denom_master, years):
    """ Given the data name,list,denomination and years, return a data """
    """ frame with growth rates                                        """

    data = True
    df = pd.DataFrame({data_name: data_master, "Denoms": denom_master, "Years": years})
    # Note: NA and NaN get promoted to float64 which don't print well
    # Year is the key, if it DNE drop the whole row.
    df.drop(df.index[df.Years == -9999], inplace=True)
    # EPS and BVPS are per share and not needing a denomination
    if data_name not in ["EPS", "BVPS"]:
        df.loc[df["Denoms"].isnull(), "Millions"] = df[data_name] / 1000000
    else:
        df.loc[df["Denoms"].isnull(), "Millions"] = df[data_name]
    df["Denoms"].fillna("d", inplace=True)
    df["Denoms"] = df["Denoms"].str.upper()
    df.loc[df["Denoms"] == "B", "Millions"] = df[data_name] * 1000
    df.loc[df["Denoms"] == "M", "Millions"] = df[data_name]
    last_data_value = df.Millions.iloc[-1]
    last_year_value = df.Years.iloc[-1]
    df["Years_delta"] = last_year_value - df["Years"]
    df["Growth"] = (last_data_value / df["Millions"]) ** (
        1 / (last_year_value - df["Years"])
    ) - 1
    df["Growth"] = df["Growth"].apply(prettify_num)
    df.loc[df["Growth"] == "inf%", "Growth"] = "NA"
    df.loc[df["Growth"] == "nan%", "Growth"] = "NA"
    return data, df, df["Growth"].head(1).values[0]


def summarize(data_name, df):
    """ Print out the Big 5 Numbers Cleanly """
    zipped = zip(df["Millions"], df["Years"], df["Years_delta"], df["Growth"])
    for data, year, delta, grwth in zipped:
        if data_name in ("EPS", "BVPS"):
            print(
                stock,
                "had",
                "{:,}".format(data),
                data_name,
                "in",
                year,
                delta,
                "GR Rate = ",
                grwth,
            )
        else:
            print(
                stock,
                "had",
                "{:,}".format(data),
                "M",
                data_name,
                "in",
                year,
                delta,
                "GR Rate = ",
                grwth,
            )
    print("")


def prettify_num(num):
    """ Pretty print Growth Rate """
    return "%.2f" % (num * 100) + "%"


def get_years_rev_ninc_eps(soup_sales_ninc_eps):
    """ Years (Revenue,Net Inc and EPS) - including USD and EUR """
    years_rev_ninc_eps = []
    rev_text_pattern = re.compile("Fiscal year is \w+-\w+. All values \w+ millions")
    years_main_th_tag = soup_sales_ninc_eps.find("th", text=rev_text_pattern)
    try:
        years_links = years_main_th_tag.find_next_siblings()
    except AttributeError as e:
        print("No Rev-EPS-NINC web data patterns found - exiting")
        sys.exit(0)
    else:
        max = 5
        for tag in years_links:
            year_raw_data = tag.string
            if year_raw_data is not None:
                match = re.search("20[0-9][0-9]", year_raw_data)
                if match:
                    year_data = match.group()
                    years_rev_ninc_eps.append(int(year_data))
            else:
                years_rev_ninc_eps.append(int(prefillna))
        if len(years_rev_ninc_eps) == max:
            return years_rev_ninc_eps


def get_rev(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ Revenue """
    rev_rn1 = "0"
    revenue = True
    revenue_master = []
    revenue_denom_master = []

    a_href_sales = soup_sales_ninc_eps.find(
        "a", attrs={"data-ref": "ratio_SalesNet1YrGrowth"}
    )
    """ If we got here the http call succeeded so we will have a valid
    soup object. But if no content found in a soup obj it returns a
    NoneType. Worst case a_href_sales becomes NoneType, but we don't
    kick up an AttributeError here.
    """
    try:
        """ If the soup object is null we will kick up the AttributeError
        here so we try and group together.
        """
        sales_td_parent = a_href_sales.find_parent()
        sales_data_links = sales_td_parent.find_next_siblings(
            "td", attrs={"class": "valueCell"}
        )
    except AttributeError as e:
        print("No Revenue data found - quitting")
        sys.exit(0)
    else:
        if sales_data_links is not None:
            for link in sales_data_links:
                rev_val = link.string
                rev, denom_val = check_data(rev_val)
                revenue_master.append(rev)
                revenue_denom_master.append(denom_val)

        revenue, revdf, rev_rn1 = check_growth_rate(
            "revenue", revenue_master, revenue_denom_master, years_rev_ninc_eps
        )
        summarize("Revenue", revdf)
        #print(revdf)
        mg_rev, mg_rev_gr = mongoize_df(revdf,"revenue", denoms='yes') 
        return revenue, revdf["Millions"], rev_rn1, mg_rev, mg_rev_gr


def get_ninc(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ Net Income """
    net_inc_rn1 = "0"
    net_inc = True
    net_inc_master = []
    net_inc_denom_master = []

    net_inc_link = soup_sales_ninc_eps.find(
        "td", attrs={"class": "rowTitle"}, text="Net Income Available to Common"
    )
    try:
        net_inc_values = net_inc_link.fetchNextSiblings("td", class_="valueCell")
    except AttributeError as e:
        print("No Net Income data found")
        print("")
        net_inc = False
        return net_inc, net_inc_master, net_inc_rn1
    else:
        for link in net_inc_values:
            net_income_val = link.string
            safe, denom_val = check_data(net_income_val)
            net_inc_master.append(safe)
            net_inc_denom_master.append(denom_val)

        net_inc, net_inc_df, net_inc_rn1 = check_growth_rate(
            "Net Income", net_inc_master, net_inc_denom_master, years_rev_ninc_eps
        )
        summarize("Net Income", net_inc_df)
        mg_inc, mg_inc_line = mongoize_df(net_inc_df,"Net Income",denoms='yes') 
        return net_inc, net_inc_df["Millions"], net_inc_rn1, mg_inc, mg_inc_line


def get_eps(soup_sales_ninc_eps, years_rev_ninc_eps):
    """ EPS """
    eps_rn1 = "0"
    eps_master = []
    eps_denom_master = []

    main_eps_a_tag = soup_sales_ninc_eps.find(
        "a", attrs={"data-ref": "ratio_Eps1YrAnnualGrowth"}
    )
    try:
        main_eps_td_tag_parent = main_eps_a_tag.find_parent()
        eps_data = main_eps_td_tag_parent.find_next_siblings(
            "td", attrs={"class": "valueCell"}
        )
    except AttributeError as e:
        print("No EPS data found")
        print("")
        eps = False
        return eps, eps_master, eps_rn1
    else:
        if eps_data is None:
            print("No EPS data found at all")
            print("")
            eps = False
            return eps, eps_master, eps_rn1
        else:
            for tag in eps_data:
                eps_val = tag.string
                safe, denom_val = check_data(eps_val)
                eps_master.append(safe)
                # Expected to be 'None's
                eps_denom_master.append(denom_val)

            eps, eps_df, esp_rn1 = check_growth_rate(
                "EPS", eps_master, eps_denom_master, years_rev_ninc_eps
            )

            summarize("EPS", eps_df)
            mgeps_line, mgeps_gr_line = mongoize_df(eps_df,"EPS") 
            return eps, eps_df["Millions"], esp_rn1, mgeps_line, mgeps_gr_line 


def mongoize_df(df,name,denoms='no'):

            mongo_data  = []
            #Data
            if denoms == 'no':
                data  = zip(df["Years"], df[name]) 
                for year, value in data:
                    mongo_data.append(f"'{year}':'{value}'")
            else:
                data  = zip(df["Years"], df[name], df["Denoms"]) 
                for year, value, denom in data:
                    #print("Y ", year, "V ", value, type(value),  "D ", denom)
                    try:
                        int(value)
                    except ValueError as e:
                        mongo_data.append(f"'{year}': {{'Val': 'NA','Den': '{denom}' }}")
                    else:
                        mongo_data.append(f"'{year}': {{'Val': {value},'Den': '{denom}' }}")
                    '''
                    if value == 'NA':
                        mongo_data.append(f"'{year}': {{'Val': 'NA','Den': '{denom}' }}")
                    elif value is np.nan:
                        mongo_data.append(f"'{year}': {{'Val': 'NA','Den': '{denom}' }}")
                    elif value == 'NaN':
                        mongo_data.append(f"'{year}': {{'Val': 'NA','Den': '{denom}' }}")
                    else:
                    '''

            mg_data_line = ','.join(mongo_data)
            mg_data_line = f"'{name}': {{ {mg_data_line} }}"

            #Growth
            data_growth     = zip(df["Years_delta"], df["Growth"]) 
            mongo_data_gr   = []
            for year_delta, growth in data_growth:
                growth = growth.replace('%','')
                if growth == 'NA':
                    mongo_data_gr.append(f"'{year_delta}':'{growth}'")
                else:
                    mongo_data_gr.append(f"'{year_delta}':{growth}")
            mg_data_line_gr = ','.join(mongo_data_gr)
            mg_data_line_gr = f"'{name}_Growth': {{ {mg_data_line_gr} }}"


            return (mg_data_line, mg_data_line_gr)


'''
EPS df looks like this:

   EPS    Denoms  Years  Millions  Years_delta  Growth
0  23.12      D   2015     23.12            4  21.02%
1  28.32      D   2016     28.32            3  20.53%
2  18.27      D   2017     18.27            2  64.75%
3  44.22      D   2018     44.22            1  12.14%
4  49.59      D   2019     49.59            0   0.00%

Without Denoms, we want this:

'EPS': {'2015':23.12},{'2016':28.32},{'2017':18.27},{'2018':44.22},{'2019':49.59}

and

'EPS_Growth': {'3':42.02} {'2':45.44} {'1':1618.75} {'0':0.00}



With Denoms:

FCF:
     FCF Denoms  Years  Millions  Years_delta  Growth
0  16.62      B   2015   16620.0            4  16.84%
1  25.82      B   2016   25820.0            3   6.25%
2  23.91      B   2017   23910.0            2  13.81%
3  22.83      B   2018   22830.0            1  35.65%
4  30.97      B   2019   30970.0            0   0.00%

We want this:

'FCF' : {'2020': {'Val':110,'Den':'M'}, '2019': {'Val':109,'Den':'M'}}
'FCFGrowth' : {'1yr':9,'2yr':8 }    



Revenue:
   revenue Denoms  Years  Millions  Years_delta  Growth
0    73.59      B   2015   73590.0            4  21.69%
1    89.73      B   2016   89730.0            3  21.62%
2   111.02      B   2017  111020.0            2  20.57%
3   136.96      B   2018  136960.0            1  17.84%
4   161.40      B   2019  161400.0            0   0.00%
'''


def get_fcf(soup_fcf):
    """ Free Cash Flow """
    fcf = True
    fcf_rn1 = "0"
    years_fcf = []
    fcf_master = []
    fcf_denom_master = []

    pattern = re.compile("\s+Free Cash Flow")
    fcf_text = soup_fcf.find(text=pattern)
    try:
        fcf_link_parent = fcf_text.find_parent()
        fcf_data = fcf_link_parent.find_next_siblings(attrs={"class": "valueCell"})
    except AttributeError as e:
        print("No FCF data found")
        print("")
        fcf = False
        return fcf, fcf_master, years_fcf, fcf_rn1
    else:
        for tag in fcf_data:
            fcf_val = tag.string
            safe, denom_val = check_data(fcf_val)
            fcf_master.append(safe)
            fcf_denom_master.append(denom_val)

        """Fcf Years"""
        fcf_years_text_h2 = soup_fcf.find("h2", text="Financing Activities")
        try:
            fcf_years_data_th = fcf_years_text_h2.find_next(
                "th", attrs={"class": "rowTitle"}
            )
            fcf_years_data = fcf_years_data_th.find_next_siblings()

        except AttributeError as e:
            print("No FCF years found")
            print("")
            fcf = False
            return fcf, fcf_master, years_fcf, fcf_rn1
        else:
            max = 5
            for tag in fcf_years_data:
                """ HTML here is 6 of the same th/td elements """
                """ 5 housing the target years                """
                fcf_raw_years = tag.string
                if fcf_raw_years is None:
                    years_fcf.append(int(prefillna))
                else:
                    match = re.search("20[0-9][0-9]", fcf_raw_years)
                    if match:
                        fcf_year_data = match.group()
                        years_fcf.append(int(fcf_year_data))
        if len(years_fcf) == max:
            pass


        fcf, fcf_df, fcf_rn1 = check_growth_rate(
            "FCF", fcf_master, fcf_denom_master, years_fcf
        )
        summarize("FCF", fcf_df)
        mg_fcf, mg_fcf_gr = mongoize_df(fcf_df,"FCF",denoms='yes') 
        return fcf, fcf_df["Millions"], years_fcf, fcf_rn1, mg_fcf, mg_fcf_gr


def get_bvps(soup_bvps):
    """ BVPS """
    bvps = True
    bvps_rn1 = "0"
    years_bvps = []
    bvps_master = []
    bvps_denom_master = []

    main_bvps_td_tag = soup_bvps.find("td", text="Book Value per Share")
    main_bvps_years = soup_bvps.find("div", attrs={"id": "target_def_historical_data"})
    try:
        bvps_data_in_links = main_bvps_td_tag.find_next_siblings()
        bvps_years_data = main_bvps_years.find_next("td").find_next_siblings()
    except AttributeError as e:
        print("No BVPS data found")
        print("")
        bvps = False
        return bvps, bvps_master, years_bvps, bvps_rn1
    else:
        bvps_data_pat = re.compile("-?[0-9]{1,9}.[0-9]{1,2}")
        for tag in bvps_data_in_links:
            bvps_val = tag.string
            if bvps_val is not None:
                matched_bvps_data = bvps_data_pat.search(bvps_val)
                bvps_data = matched_bvps_data.group()
                safe, denom_val = check_data(bvps_data)
                bvps_master.append(safe)
                # Expected to be 'None's
                bvps_denom_master.append(denom_val)

    """Bvps Years"""
    bvps_years_pat = re.compile("[0-9]{2}")
    if bvps_years_data is not None and len(bvps_years_data) > 0:
        for year in bvps_years_data[-5:]:
            # year will break w/html \'s, use year.string
            # just get the last 5 values
            matched_bvps_year = bvps_years_pat.search(year.string)
            if matched_bvps_year:
                bvps_year = "20" + matched_bvps_year.group()
                years_bvps.append(int(bvps_year))
    else:
        bvps = False
        print("No BVPS years data found")
        print("")
        return bvps, bvps_master, years_bvps, bvps_rn1

    bvps, bvps_df, bvps_rn1 = check_growth_rate(
        "BVPS", bvps_master, bvps_denom_master, years_bvps
    )
    summarize("BVPS", bvps_df)
    return bvps, bvps_df["BVPS"], years_bvps, bvps_rn1


def get_roic(soup_roic):
    """ ROIC """
    pattern = re.compile("Return on Invested Capital")
    roic_p_tag = soup_roic.find("td", text=pattern)
    try:
        roic_data = roic_p_tag.find_next_sibling(
            "td"
        )
        # ROIC is just one value. Leave as NavString
    except AttributeError as e:
        print("No Roic data found")
        roic = False
        return roic
    else:
        roic = roic_data.string
        print(stock, "had", roic, "ROIC")
        mg_roic = f"'ROIC':'{roic}'"
        return mg_roic


def get_ni_ttm(soup_ni_ttm):
    """ Net Income TTM """
    net_inc_ttm = soup_ni_ttm.find("span", attrs={"id": "pgNameVal"})
    try:
        net_inc_ttm_data = net_inc_ttm.string
    except AttributeError as e:
        print("No NetInc TTM found")
        mg_ni_ttm = f"'NetIncTTM' : {{ 'Val' : 'NA', 'Den' : 'NA' }}"
        return 'NA', mg_ni_ttm
    else:
        ni_ttm, ni_ttm_denom = check_data(net_inc_ttm_data)
        print(stock, "had", ni_ttm, ni_ttm_denom, "NetInc TTM")
        mg_ni_ttm = f"'NetIncTTM' : {{ 'Val' : {ni_ttm}, 'Den' : '{ni_ttm_denom}' }}"
        return ni_ttm, mg_ni_ttm


def get_pe_ttm(soup_pe_ttm):
    wanted_text  = 'P/E'
    hook_text = 'stock-summary-table fc-regular'
    pe_ttm = list(soup_pe_ttm.find('div',attrs={"class" : hook_text }).children)
    if pe_ttm:
        for index, div_tag in enumerate(pe_ttm):
            if wanted_text in str(pe_ttm[index]):
                pe_ttm_num  = pe_ttm[index+2].text.lstrip()
                print(f"{stock} PE: {pe_ttm_num}")
                return(f"{stock} PE: {pe_ttm_num}")
    else:
        print("No PE TTM data found for " + stock)
        return(f"{stock} PE: 'NA'")

def get_mcap(soup_pe_ttm):
    """ Get Total Market Cap
    Create a list of child div tags of the 'hook text'.
    Note the 'next' item (+2 index b/c of tags vs strings) is market cap.

    <div class="stock-summary-table fc-regular" data-v-fa982d3a>
    SNIP...
        <div data-v-fa982d3a> Avg Vol (1m): </div>
        <div data-v-fa982d3a> 1,980,804 </div>
        <div data-v-fa982d3a> Market Cap $: </div>
        <div data-v-fa982d3a> 969.35 Bil </div>
    SNIP...
    """
    wanted_text  = 'Market Cap'
    hook_text = 'stock-summary-table fc-regular'
    market_cap = list(soup_pe_ttm.find('div',attrs={"class" : hook_text }).children)
    for index, div_tag in enumerate(market_cap):
        if wanted_text in str(market_cap[index]):
            market_cap_text = market_cap[index+2].text.lstrip()
            print(f"{stock} Market Cap: {market_cap_text}")
            mc_val, mc_den = market_cap_text.strip().split(' ') 
            mg_mcap = f"'MC' : {{'Val' : {mc_val} , 'Den' : '{mc_den}' }}"
            return mg_mcap

def get_rev_ttm(soup_rev_ttm):
    """ Get Trailing TTM for Revenue """
    rev_ttm_tag = soup_rev_ttm.find("span", attrs={"id": "pgNameVal"})
    try:
        #print('hello')
        rev_ttm_data = rev_ttm_tag.string
        #print('rev_ttm_data', rev_ttm_data)
    except AttributeError as e:
        #print(e, "!Error Text!")
        print('No Rev TTM Found!')
        return f"'RevTTM' : {{'Val' : 'NA', 'Den' : 'NA' }}"
    else:
        rev_ttm, rev_ttm_denom = check_data(rev_ttm_data)
        try:
            int(rev_ttm)
        except ValueError:
            rev_ttm = 'NA'
            mg_rev_ttm = f"'RevTTM' : {{'Val' : 'NA', 'Den' : '{rev_ttm_denom}' }}"
            #print ('a',mg_rev_ttm)
        else:
            mg_rev_ttm = f"'RevTTM' : {{'Val' : {rev_ttm} , 'Den' : '{rev_ttm_denom}' }}"
            #print ('N',mg_rev_ttm)
        print(
            stock + " had " + str(rev_ttm) + " " + str(rev_ttm_denom) + " Revenue TTM"
        )
    return mg_rev_ttm


def main():
    """" Start Here """
    if web_mode:
        (
            r_sales_ninc_eps,
            r_roic,
            r_url_fcf,
            r_bvps,
            r_ni_ttm,
            r_pe_ttm,
            r_rev_ttm,
            content_dict,
        ) = get_web_data()

        (
            soup_sales_ninc_eps,
            soup_fcf,
            soup_bvps,
            soup_roic,
            soup_ni_ttm,
            soup_pe_ttm,
            soup_rev_ttm,
        ) = make_soup(
            r_sales_ninc_eps, r_url_fcf, r_bvps, r_roic, r_ni_ttm, r_pe_ttm, r_rev_ttm
        )

    years_rev_ninc_eps = get_years_rev_ninc_eps(soup_sales_ninc_eps)
    revenue, revenue_master, rev_rn1, mg_rev, mg_rev_gr = get_rev(soup_sales_ninc_eps, years_rev_ninc_eps)

    net_inc, net_inc_master, net_inc_rn1, mg_inc, mg_inc_line = get_ninc(
        soup_sales_ninc_eps, years_rev_ninc_eps
    )

    eps, eps_master, eps_rn1, mgeps_line, mgeps_gr_line  = get_eps(soup_sales_ninc_eps, years_rev_ninc_eps)
    fcf, fcf_master, years_fcf, fcf_rn1, mg_fcf, mg_fcf_gr = get_fcf(soup_fcf)
    bvps, bvps_master, years_bvps, bvp_rn1 = get_bvps(soup_bvps)
    mg_roic = get_roic(soup_roic)
    ni_ttm, mg_ni_ttm = get_ni_ttm(soup_ni_ttm)
    pe_ttm = get_pe_ttm(soup_pe_ttm)
    mg_rev_ttm = get_rev_ttm(soup_rev_ttm)
    mg_mcap   = get_mcap(soup_pe_ttm)

    mg = []
    for x in [mg_roic, mg_ni_ttm, mg_mcap, mg_rev_ttm, mg_rev, mg_rev_gr, mg_inc, mg_inc_line, mgeps_line,mgeps_gr_line,mg_fcf,mg_fcf_gr]:
        mg.append(x)
    mongo_doc = ','.join(mg)
    mongo_doc = f"{{ 'Stock':'{stock}', {mongo_doc} }}"
    print(mongocli.insert_one(eval(mongo_doc)))

if __name__ == "__main__":

    try:
        #receive a mondb collection handle here
        mongocli = mongodb.MongoCli().ConnectToMongo()
        main()
    except ServerSelectionTimeoutError as e:
        print("Can't connect to Mongodb - Quitting Crawl")
        sys.exit(1)
