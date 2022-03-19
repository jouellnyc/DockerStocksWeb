#!/usr/bin/env python3

""" mongodb.py - interface into MongoDB
- This script requires the pymongo module.

- This file is intended as a loadable module only.

"""

import sys
import json
import yaml
import urllib.parse

### Allow for local, same directory testing and usage

try:
    from lib.aws_secrets import get_aws_secrets
except ModuleNotFoundError:
    from aws_secrets import get_aws_secrets

try:
    from lib.load_mongo_config import get_local_mongodb_config
except ModuleNotFoundError:
    from load_mongo_config import get_local_mongodb_config 

from pymongo import MongoClient


class StockDoesNotExist(Exception):
    pass


class MongoCli:
    def __init__(self, mode=None):
        if mode == 'AWS':
            self.mysecret      = self.GetSecrets()
            self.database      = urllib.parse.quote_plus(self.mysecret["database"])
            self.collection    = urllib.parse.quote_plus(self.mysecret["collection"])
            self.mongohost     = urllib.parse.quote_plus(self.mysecret["mongohost"])
            self.mongousername = urllib.parse.quote_plus(self.mysecret["mongousername"])
            self.mongopassword = urllib.parse.quote_plus(self.mysecret["mongopassword"])
            self.client_connect_string = f"mongodb+srv://{self.mongousername}\
            :{self.mongopassword}@{self.mongohost}/{self.database}?retryWrites=true&w=majority"
        else:
            self.database      = get_local_mongodb_config()['Infra']['database']
            self.collection    = get_local_mongodb_config()['Infra']['collection']
            self.mongohost     = get_local_mongodb_config()['Infra']['mongohost']
            self.port          = get_local_mongodb_config()['Infra']['port']
            self.client_connect_string = (self.mongohost, self.port)
        self.dbh = self.connect_to_mongo()

    def get_aws_secrets(self):
        try:
            return json.loads(get_secret(self.aws_secret, self.aws_region))
        except Exception:
            raise

    def connect_to_mongo(self):
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

        try:
            client = MongoClient(self.mongohost, self.port)
            #client = MongoClient('docker_stocks_db_1', 27017)
            #client = MongoClient('172.25.0.2', 27017)
            client.server_info()
            database_handle = client[self.database]
            return database_handle[self.collection]
        except Exception:
            raise

    def lookup_stock(self, stock):
        """ Simple Stock Query """
        response = self.dbh.find_one({"Stock": stock}, {"_id": 0})
        if response is None:
            raise StockDoesNotExist(f"{stock}  not found")
        else:
            return response

    def dump_all_stocks_sorted_by_date(self):
        """ Dump All Stocks with a Crawl Date, return oldest first by date """

        stocks = sorted(
            [
                (x["Stock"], x["DateCrawled"])
                for x in self.dbh.find({"DateCrawled": {"$exists": True}})
            ],
            key=lambda one_date: one_date[1],
        )
        return [one_stock[0] for one_stock in stocks]

    def dump_recent_stocks(self):
        """ Return all stocks split *after* the last crawled stock """
        all_stocks = self.dump_all_stocks()
        all_stocks_dict = {stock: int(i) for i, stock in enumerate(all_stocks, 1)}
        latest_stock = self.get_latest_stock()
        latest_stock_index = all_stocks_dict[latest_stock]
        return all_stocks[latest_stock_index:]

    def dump_all_stocks(self):
        """ Dump All Stocks (All should have a CD), sorted Alphabetically """
        return sorted([x["Stock"] for x in self.dbh.find({"Stock": {"$exists": True}})])

    def get_latest_stock(self):
        """ Pull down the last stock that got crawled """
        return self.dbh.find_one({"Stock": "last_good"}, {"Name": 1, "_id": 0})["Name"]

    def delete_one_stock(self, stock):
        """ Delete One Stock """
        result = self.dbh.delete_one({"Stock": stock})
        return bool(result.acknowledged and result.deleted_count == 1)

    def update_latest_stock(self, stock):
        """ Update DB with the last stock that got crawled """
        return self.dbh.update_one(
            {"Stock": "last_good"}, {"$set": {"Name": stock}}, upsert=True
        )

    def update_as_error(self, stock, msg):
        """ Replace existing Data with a blank if no Data Return from API """
        return self.dbh.replace_one({"Stock": stock}, {"Stock": stock, "Error": msg})

    def update_one_document(self, mongo_filter, mongo_doc):
        """ Update a fields on a doc, create if it does not exist. """
        return self.dbh.update_one(mongo_filter, {"$set": mongo_doc}, upsert=True)

    def insert_one_document(self, mongo_doc):
        """ Insert one document:                                         """
        """ Will create a DUP DOC with the same stock symbol if exists!  """
        new_result = self.dbh.insert_one(mongo_doc)
        return new_result.inserted_id

    def replace_one_document(self, mongo_filter, mongo_doc):
        """ Replace one document in MongoDB entirely/%100 """
        return self.dbh.replace_one(mongo_filter, mongo_doc, upsert=True)

    def drop_db(self):
        """  Drop all documents (testing/etc.) """
        return self.dbh.drop()
