#!/usr/bin/env python3

""" mongodb.py - interface into MongoDB

- This script requires the pymongo module.

- This file:

    - is intended as a loadable module only.
    - contains the following methods:

     ConnectToMongo
        Connect to MongoDB and return DB handle
     insert_one_document
        Insert one doc to mongodb
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError

import logging


class MongoCli:
    def __init__(self):

        self.database_name = "stocks"
        self.collection_name = "data"
        self.dbh = self.ConnectToMongo()

    def ConnectToMongo(self):
        """
        Return a database_handle to the caller

        Parameters
        ----------
        database_name : str
            The Default db name
        collection_name : str
            The Default collection name

        Returns
        -------
            collection_handle :  pymongo connect object
        """

        collection_name = self.collection_name
        database_name = self.database_name

        try:
            MONGOCLIENTLINE
            client.server_info()
            database_handle = client[database_name]
            collection_handle = database_handle[collection_name]
            return collection_handle
        except Exception:
            raise

    def lookup_stock(self, stock):
        response = self.dbh.find_one({"Stock": stock}, {"_id": 0})
        if response is None:
            raise ValueError(f"{stock}  not found")
        else:
            return response

    def update_one_document(self, mongo_filter, mongo_doc, verbose=False):
        """
        Update only one document in MongoDB, create it if it does not exist.
        Parameters
        ----------
        mongo_filter
            - hash to specify mongo restriction
        mongo_doc
            - key : value pairs making up the document

        Returns
        -------
        Items
            {MongoCli object}  of all the local posts in the free section
        """
        new_result = self.dbh.update_one(mongo_filter, mongo_doc, upsert=True)
        if verbose:
            print(new_result.raw_result)
        return new_result

    def insert_one_document(self, mongo_filter, mongo_doc):
        """
        Insert  only one document in MongoDB; do not create it if it does not exist.

        Parameters
        ----------
        mongo_filter
            - hash to specify mongo restriction
        mongo_doc
            - key : value pairs making up the document

        Returns
        -------
        Items
            {MongoCli object}  of all the local posts in the free section
        """
        new_result = self.dbh.insert_one(mongo_filter, mongo_doc)
        print(new_result.inserted_id)
        return new_result

    def drop_db(self):
        """
        Drop all documents (testing/etc.)

        Parameters
        ----------
        None

        Returns
        -------
        new_result

        Exceptions
        ----------
        Failure/Connection
        """

        new_result = self.dbh.drop()
        return new_result


if __name__ == "__main__":

    import sys

    try:
        mg = MongoCli()
        print(mg.lookup_stock({"Stock": "AGEN"}))
    except ConnectionFailure as e:
        print("MongoDB ConnectionFailure: ", e)
        print("Is your IP whitelisted?")
    except Exception as e:
        logging.exception(e)
