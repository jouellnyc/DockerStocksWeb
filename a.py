#!/usr/bin/env python3



import json

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


oidc = OpenIDConnect(app)

@app.before_request
def before_request_func():
    print('nsession' + str(session))

@app.route('/')
def hello_world():
    print('2nsession' + str(session))
    if oidc.user_loggedin:
        email=oidc.user_getfield('email')
        pic_url=oidc.user_getfield('picture')
        return render_template("welcome.html", email=email, pic_url=pic_url)
    else:
        print('3nsession' + str(session))
        return render_template("welcome_not_logged.html")

@app.route('/login_oauth')
@oidc.require_login
def hello_me():
    info = oidc.user_getinfo(['email', 'openid_id'])
    print('4nsession' + str(session))
    return redirect("/", code=302)


@app.route('/logout')
def logout():
    oidc.logout()
    return redirect("/", code=302)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')

