#!/usr/bin/env python3

""" This script's function is to provide the data quickly to crawlers in a flywheel fashion. """
""" in order to make getting the stock list as efficient as possible.                        """
""" Pulling the list locally and fiddling was ok but a temp measure and not efficient.       """

""" Without this script the Crawlers would have to take a differnet mode                     """
""" - Take a bunch of stocks off the stocklist  in batches                                   """
""" - Set some sort of flag in the database and try to work with  that                       """
""" So far it's 100% efficient and no blocking                                               """

import sys
import logging

from flask import Flask

from lib import mongodb
sys.path.insert(0, 'lib')

app = Flask(__name__)
mg = mongodb.MongoCli()    
all_stocks = mg.dump_all_stocks_sorted_by_date()
batch_size = 50

# Logging A la:
# https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
# https://stackoverflow.com/questions/27687867/is-there-a-way-to-log-python-print-statements-in-gunicorn

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    
@app.route("/stocks/", methods=["POST", "GET"])
def get_data():
        
    global all_stocks
    
    while all_stocks:
        #stock = all_stocks.pop()
        stock = [ all_stocks.pop() for x in range(batch_size ) ]
        return str(stock)
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001)
