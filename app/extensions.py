import pymongo
import random
import string
from passlib.hash import pbkdf2_sha256
from typing import Optional

# Default MongoDB connection string
DEFAULT_STRING = "mongodb://localhost:27017/"
# DEFAULT_STRING = "mongodb://mongodb:27017/"



class MongoDB:
    """
    MongoDB Helper Class to simplify MongoDB operations like insert, fetch, update, delete, etc.
    Supports connection string, database, and collection management.
    """

    def __init__(self, db_name=None, collection_name=None, connection_str=DEFAULT_STRING):
        """
        Initialize MongoDB connection.
        :param db_name: Database name to connect to (optional).
        :param collection_name: Collection name to connect to (optional).
        :param connection_str: MongoDB connection string.
        """
        try:
            self.client = pymongo.MongoClient(connection_str)
            self.db = self.client[db_name] if db_name else None
            self.collection = self.db[collection_name] if collection_name else None
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def insert(self, data: dict) -> bool:
        """ Insert a single document into the collection. """
        try:
            self.collection.insert_one(data)
            return True
        except Exception as e:
            print(f"Insert failed: {e}")
            return False

    def fetch(self, query=None, show_id=False) -> list:
        """
        Fetch documents from the collection based on the query.
        :param query: Dictionary query to filter documents.
        :param show_id: If True, includes '_id' in results.
        """
        result = []
        projection = {"_id": 0} if not show_id else {}
        try:
            documents = self.collection.find(query or {}, projection)
            for doc in documents:
                if show_id and "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                result.append(doc)
            return result[::-1]  # Reverse order
        except Exception as e:
            print(f"Fetch failed: {e}")
            return []

    def count(self, query=None) -> int:
        """ Count the number of documents matching a query. """
        return self.collection.count_documents(query or {})        