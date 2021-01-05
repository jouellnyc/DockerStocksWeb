#!/usr/bin/env python3

""" requestwrap.py -  wrap repetitive web requests

- This script module:
    - uses requests to screen scrape and serves as a wrapper for requests
    - takes in a url and crawls it

-This script requires the requests module.

-This file is meant to be imported as a module.

- It contains the following functions:
    * err_web- the main function of the script wrapping requests

"""

import sys
import requests
import random


def err_web(url):
    """
    Catch the Errors from the Web Requests
    All or nothing here: If not 200 OK - exit the program

    Parameters
    ----------
    url : str
        The URL to crawl

    Returns
    -------
    httprequest :  A  Beautiful Soup object

    Rotate the UserAgent to attempt to blend the requests in.
    see  https://deviceatlas.com/blog/list-of-user-agent-strings#desktop

    """

    user_agents = [
        {
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
        },
        {
            "User-Agent": f"Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9"
            "(KHTML, like Gecko) Version/9.0.2 Safari/601.3.9"
        },
        {
            "User-Agent": f"Mozilla/5.0 (Linux; Android 8.0.0; "
            "SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/62.0.3202.84 Mobile Safari/537.36"
        },
        {
            "User-Agent": f"Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/47.0.2526.111 Safari/537.36"
        },
        {
            "User-Agent": f"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; "
            "rv:15.0 Gecko/20100101 Firefox/15.0.1"
        },
    ]

    try:
        httprequest = requests.get(
            url, timeout=10, allow_redirects=True, headers=random.choice(user_agents)
        )
        # raise_for_status() never execs if requests.get above has connect error/timeouts
        httprequest.raise_for_status()
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
        return httprequest


err_web("http://www.google.com")
