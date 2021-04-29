#!/usr/bin/env python3


import sys

import logging

import flask
from flask import Flask
from flask import request
from flask import render_template

from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure

from lib import mongodb


import mongodb

sys.path.insert(0, 'lib')


app = Flask(__name__)

mg = mongodb.MongoCli()    
all_stocks = mg.dump_all_stocks_sorted_by_date()
    
    
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
        stock = all_stocks.pop()
        return str(stock)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)