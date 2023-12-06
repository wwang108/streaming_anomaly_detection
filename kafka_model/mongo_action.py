import pymongo
from typing import List
from entities import TransactionModel
class MongoDBCollection:
    def __init__(self,
                 username,
                 password,
                 ip_address,
                 database_name,
                 collection_name):
        '''
        Using ip_address, database_name, collection_name,
        initiate the instance's attributes including ip_address,
        database_name, collection_name, client, db and collection.

        For pymongo, see more details in the following.
        https://pymongo.readthedocs.io
        '''
        self.username = username
        self.password = password
        
        self.ip_address = ip_address
        self.database_name = database_name
        self.collection_name = collection_name

        self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{ip_address}")
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
        
        self.connection_string = f"mongodb+srv://{username}:{password}@{ip_address}/{database_name}.{collection_name}"


    def insert_transaction(self, transaction_data: dict):
        """
        Insert a transaction document into the collection.
        The transaction_data should be a dictionary representation of TransactionModel.
        """
        self.collection.insert_one(transaction_data)

    def count_all_documents(self):
        """
        Counts the total number of documents across all collections in the database.
        """
        total_documents = 0
        for collection_name in self.db.list_collection_names():
            collection = self.db[collection_name]
            total_documents += collection.count_documents({})

        return total_documents
