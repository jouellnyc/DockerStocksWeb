#!/bin/bash
WORKDIR="stocks"
cd /$WORKDIR
./lib/aws_secrets.py
/usr/local/bin/gunicorn stock_flask:app  -c /$WORKDIR/external/gunicorn/gunicorn.conf.py
