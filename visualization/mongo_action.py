import pymongo
from typing import List, Dict
from entities import TransactionModel
import pytz


class MongoDBCollection:
    def __init__(self, username, password, ip_address, database_name, collection_name):
        """
        Using ip_address, database_name, collection_name,
        initiate the instance's attributes including ip_address,
        database_name, collection_name, client, db and collection.

        For pymongo, see more details in the following.
        https://pymongo.readthedocs.io
        """
        self.username = username
        self.password = password

        self.ip_address = ip_address
        self.database_name = database_name
        self.collection_name = collection_name

        self.client = pymongo.MongoClient(
            f"mongodb+srv://{username}:{password}@{ip_address}"
        )
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
        return self.collection.count_documents({})

    def count_transactions_in_interval(self, start_time, end_time):
        start_time = start_time.replace(tzinfo=pytz.UTC)
        end_time = end_time.replace(tzinfo=pytz.UTC)
        query = {"writein_time": {"$gte": start_time, "$lt": end_time}}

        return self.collection.count_documents(query)

    def calculate_average(self, field_name: str) -> float:
        """
        Calculate the average of a specified field.
        """
        pipeline = [{"$group": {"_id": None, "average": {"$avg": f"${field_name}"}}}]
        result = list(self.collection.aggregate(pipeline))
        return result[0]["average"] if result else 0

    def calculate_statistics_in_interval(
        self, field_names: List[str], start_time, end_time
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistics (average, min, max) for a list of fields in a given time interval.
        """
        # Ensure the times are timezone-aware and in UTC
        start_time = start_time.replace(tzinfo=pytz.UTC)
        end_time = end_time.replace(tzinfo=pytz.UTC)

        # The match stage for filtering based on time interval
        match_stage = {
            "$match": {"writein_time": {"$gte": start_time, "$lt": end_time}}
        }

        # The group stage for calculating statistics
        group_stage = {"_id": None}
        for field in field_names:
            group_stage.update(
                {
                    f"{field}_average": {"$avg": f"${field}"},
                    f"{field}_min": {"$min": f"${field}"},
                    f"{field}_max": {"$max": f"${field}"},
                }
            )

        # The pipeline combining match and group stages
        pipeline = [match_stage, {"$group": group_stage}]

        # Executing the pipeline
        result = list(self.collection.aggregate(pipeline))
        return result[0] if result else {}
