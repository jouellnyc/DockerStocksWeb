#!/usr/bin/env python3


"""

Main Flask application file

- This script is the WSGI form parser/validator.

- This script requires Flask to be installed.

- It expects to be passed:
    - stock name from nginx html form

- It sends all returnables to return flask's render_template

"""


import json
import logging

import flask
from flask import g
from flask import Flask
from flask import request
from flask import redirect
from flask import render_template
from flask_oidc import OpenIDConnect
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure

from lib import mongodb
from lib.mongodb import StockDoesNotExist


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': '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',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_SCOPES' : ['openid', 'email', 'profile']

})

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

oidc = OpenIDConnect(app)

@app.route('/')
def hello_world():
    if oidc.user_loggedin:
        email=oidc.user_getfield('email')
        email=oidc.user_getfield('given_name')
        print("email:",email)
        #return ('Hello, %s, <a href="/private">See private</a> '
        #        '<a href="/logout">Log out</a>') % \
        #    oidc.user_getfield('email')
        return render_template("welcome.html",email=email)
    else:
        return render_template("welcome_not_logged.html")

@app.route('/login_oauth')
@oidc.require_login
def hello_me():
    info = oidc.user_getinfo(['email', 'openid_id'])
    print(info)
    return redirect("/", code=302)
    #return ('Hello, %s (%s)! <a href="/">Return</a>' %
    #        (info.get('email'), info.get('openid_id')))


@app.route('/logout')
def logout():
    oidc.logout()
    return redirect("/", code=302)
    #return redirect("/http://www.example.com", code=302)
    #return 'You have been logged out! <a href="/">Return</a>'

@oidc.require_login
@app.route("/search/", methods=["POST", "GET"])
def get_data():
    """
    Return a view to Flask with relevant details

    'stock' comes in as a 'str' from the Flash HTML form  and most easily is tested
    by casting to 'int'. It is  then queried @mongodb and returns HTML
    Done this way it catches stock='' and if stock is None without explictly checking.
    """

    try:
        querystring = request.args
        app.logger.debug(f"querystring: {querystring}")
        stock = querystring.get("stock")
        if not str(stock):
            raise ValueError
    except (TypeError, ValueError):
        app.logger.error(f"Invalid data: querystring: {querystring} : invalid")
        return render_template("notastock.html", stock=stock)
    except Exception as e:
        msg = f"Bug: querystring:{querystring}, Error: {e}"
        app.logger.exception(msg)
        flask.abort(500)
    else:
        try:
            stock = str(stock).upper()
            mongocli = mongodb.MongoCli()
            stock_data = mongocli.lookup_stock(stock)
            if len(stock_data) < 2:
                return render_template("dne_stock.html", stock=stock)
            if stock_data["Error"]:
                return render_template("dne_stock.html", stock=stock)
        except mongodb.StockDoesNotExist as e:
            app.logger.error(str(e))
            return render_template("dne_stock.html", stock=stock)
        except ValueError as e:
            app.logger.error(str(e))
            return render_template("dne_stock.html", stock=stock)
        except OperationFailure as e:
            msg = "PROD FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        except ConnectionFailure as e:
            msg = "Connect FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        except ServerSelectionTimeoutError as e:
            msg = "Server FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html", stock=stock)
        else:
            # Each Financial Group will be broken down by the template
            return render_template(
                "stock_data.html", stock_data=stock_data, stock=stock,
            )


if __name__ == '__main__':
    app.run(ssl_context='adhoc')
