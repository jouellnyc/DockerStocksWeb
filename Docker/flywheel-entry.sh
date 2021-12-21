#!/bin/bash
WORKDIR="stocks"
cd /$WORKDIR
/usr/local/bin/gunicorn fly_wheel:app  -c /$WORKDIR/external/gunicorn/gunicorn.conf.flywheel.py
