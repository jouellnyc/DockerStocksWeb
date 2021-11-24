#!/bin/bash
WORKDIR="stocks"
cd /$WORKDIR
/usr/local/bin/gunicorn stock_flask:app  -c /$WORKDIR/external/gunicorn/gunicorn.conf.py
