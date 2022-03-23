#!/usr/bin/python3

import sys
sys.path.append('../lib/')

from mongodb import MongoCli
mg = MongoCli()

if __name__ == "__main__" :

    mg = MongoCli()
    mg.drop_db()

