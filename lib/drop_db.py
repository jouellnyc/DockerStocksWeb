#!/usr/bin/env python3

import mongodb
import logging
from pymongo.errors import OperationFailure
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError


if __name__ == "__main__":

    try:
        mg = mongodb.MongoCli()
        drop = mg.drop_db()
        if drop is None:
            print("DB dropped OK")
    except OperationFailure as e:
        print("Permissions?", e)
    except ConnectionFailure as e:
        print("MongoDB ConnectionFailure: ", e)
        print("Is your IP whitelisted?")
    except Exception as e:
        logging.exception(e)
