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
from flask import session
from flask import url_for
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.errors import OperationFailure
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth

from lib import mongodb
from lib.mongodb import StockDoesNotExist
from lib.init import Credentials

#nb:02/25/23 - If the Instance cannot connect to MongoDB, Nginx will return 404 
mongocli = mongodb.MongoCli()
secrets = Credentials().get_all_credentials()

app = Flask(__name__)
app.secret_key = secrets["APP_SECRET_KEY"]
app.url_map.strict_slashes = False

logging.basicConfig(level=logging.DEBUG)

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id     = secrets["AUTH0_CLIENT_ID"],
    client_secret = secrets["AUTH0_CLIENT_SECRET"],
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{secrets["AUTH0_DOMAIN"]}/.well-known/openid-configuration',
)


@app.route("/")
def home():
    user_data    = session.get('user')
    if user_data is not None:
        user_info              = user_data.get('userinfo')
        session['first_name']  = user_info.get('given_name')
        session['email']       = user_info.get('email')
        session['picture_url'] = user_info.get('picture')
    else:
        session['picture_text'] = "Welcome - " 
        session['email_text'] = "There!" 
    return render_template("welcome.html")

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/search")
def search():
    """
    Return a view to Flask with relevant details

    'stock' comes in as a 'str' from the Flash HTML form  and most easily is tested
    by casting to 'int'. It is  then queried @mongodb and returns HTML Done this way it catches stock='' and if stock is None without explictly checking.
    """
    try:
        querystring = request.args
        app.logger.debug(f"querystring: {querystring}")
        stock = querystring.get("stock")
        if not str(stock):
            raise ValueError
    except (TypeError, ValueError):
        app.logger.error(f"Invalid data: querystring: {querystring} : invalid")
        return render_template("dne_stock.html")
    except Exception as e:
        msg = f"Bug: querystring:{querystring}, Error: {e}"
        app.logger.exception(msg)
        flask.abort(500)
    else:
        try:
            stock = str(stock).upper()
            g.stock = stock
            stock_data = mongocli.lookup_stock(stock)
            if len(stock_data) < 2:
                return render_template("dne_stock.html")
            if stock_data["Error"]:
                return render_template("dne_stock.html")
        except mongodb.StockDoesNotExist as e:
            app.logger.error(str(e))
            return render_template("dne_stock.html")
        except ValueError as e:
            app.logger.error(str(e))
            return render_template("dne_stock.html")
        except OperationFailure as e:
            msg = "PROD FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html")
        except ConnectionFailure as e:
            msg = "Connect FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html")
        except ServerSelectionTimeoutError as e:
            msg = "Server FAILURE! " + str(e)
            app.logger.error(msg)
            return render_template("dne_stock.html")
        else:
            return render_template("stock_data.html", stock_data=stock_data)


if __name__ == '__main__':
    app.run(debug=True)
