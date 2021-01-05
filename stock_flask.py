#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
app.py - Main Flask application file

- This script is the WSGI form parser/validator.

- This script requires Flask to be installed.

- It expects to be passed:
    - zip # from nginx html form

- It sends all returnables to return flask's render_template

"""


import sys
import logging

import flask
from flask import Flask
from flask import request
from flask import render_template
import pymongo
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure

from lib import mongodb


app = Flask(__name__)

# Logging A la:
# https://trstringer.com/logging-flask-gunicorn-the-manageable-way/
# https://stackoverflow.com/questions/27687867/is-there-a-way-to-log-python-print-statements-in-gunicorn

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route("/search/", methods=["POST", "GET"])
def get_data():
    """
    Return a view to Flask with relevant details

    zip comes in as a 'str' from the Flash HTML form  and most easily is tested
    by casting to 'int'. zip is then queried @mongodb and returns HTML
    Done this way it catches zip='' and if zip is None with explictly checking.
    """

    try:
        querystring = request.args
        app.logger.debug(f"querystring: {querystring}")
        stock = querystring.get("stock")
        if len(str(stock)) < 1:
            raise ValueError
    except (TypeError, ValueError): 
            app.logger.error(f"Invalid data: querystring: {querystring} : invalid")
            return render_template("notastock.html", stock=stock)
    except Exception as e:
            msg = f"Bug: querystring:{querystring}, Error: {str(e)}"
            app.logger.exception(msg)
            flask.abort(500)
    else:
        stock = str(stock).upper()
        try:
            #Master Dictionary with all the Data
            mongocli   = mongodb.MongoCli()
            stock_data = mongocli.lookup_stock(stock)
        except ValueError as e:
            app.logger.error(str(e))
            return render_template("dne_stock.html", stock=stock)
        except OperationFailure as e:
            msg = "PROD FAILURE! "
            msg += str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        except ConnectionFailure as e:
            msg = "Connect FAILURE! "
            msg += str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        except ServerSelectionTimeoutError as e:
            msg = "Server FAILURE! "
            msg += str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        else:
            #Each Financial Group will be broken down by the template
            return render_template(
                "stock_data.html", stock_data = stock_data,stock=stock, 
           )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
