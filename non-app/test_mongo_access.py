#!/usr/bin/python3

""" Simple Smoke Test to see if container Should be started """

import sys
sys.path.append("../lib/")
import logging

import mongodb
logging.basicConfig(
        filename='/tmp/mongo.test',
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
)

try:
    mg = mongodb.MongoCli()
    out = mg.lookup_stock('AAPL')
except Exception as e:
    logging.error(e)
    sys.exit(1)
else:
    logging.info('Mongo Test Successful')
    logging.info(out)
    sys.exit(0)

