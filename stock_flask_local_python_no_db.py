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
from flask import session
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
app.secret_key = 'super secret key ZZ ZZ'
app.config.update({
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_SCOPES' : ['openid', 'email', 'profile']

})

######################################################
app.debug = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)
######################################################


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

oidc = OpenIDConnect(app)

@app.route('/')
def hello_world():
    if oidc.user_loggedin:
        print('g.oidc_id_token',g.oidc_id_token)
        return render_template("welcome.html")
    else:
        return render_template("welcome_not_logged.html")

@app.route('/login_oauth')
@oidc.require_login
def hello_me():
    return redirect("/", code=302)

@app.route('/logout')
def logout():
    oidc.logout()
    return redirect("/", code=302)

@oidc.require_login
@app.route("/search/", methods=["POST", "GET"])
def get_data():
    """
    Return a view to Flask with relevant details

    'stock' comes in as a 'str' from the Flash HTML form and most easily is tested by casting to 'int'. 
    It is  then queried @mongodb and returns HTML.

    Done this way it catches stock='' and if stock is None without explictly checking.
    """
    if oidc.user_loggedin:
        email=oidc.user_getfield('email')
        pic_url=oidc.user_getfield('picture')
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
            return render_template("dne_stock.html", stock=stock, pic_url=pic_url, email=email)
        else:
            # Each Financial Group will be broken down by the template
            return render_template(
                "stock_data.html", stock_data=stock_data, stock=stock, email=email, pic_url=pic_url
            )


if __name__ == '__main__':
    app.run(ssl_context='adhoc',debug=True)
