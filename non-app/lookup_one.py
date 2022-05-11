#!/usr/bin/python3

import sys
sys.path.append("../lib/")

import mongodb
mg = mongodb.MongoCli()
print(mg.lookup_stock(sys.argv[1]))
