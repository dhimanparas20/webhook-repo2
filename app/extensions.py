import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import pymongo
from pymongo.collection import Collection
from pymongo.database import Database
from dotenv import load_dotenv
import logging

# Load environment variables from .env if present
load_dotenv()

DEFAULT_CONNECTION_STRING = os.getenv(
    "MONGO_URI", "mongodb://localhost:27017/")


class MongoDB:
    def __init__(self, db_name=None, collection_name=None, connection_str=DEFAULT_CONNECTION_STRING):
        try:
            self.client = pymongo.MongoClient(connection_str)
            self.db = self.client[db_name] if db_name is not None else None
            self.collection = self.db[collection_name] if (
                self.db is not None and collection_name is not None) else None
        except Exception as e:
            print(f"[MongoDB] Failed to connect: {e}")
            self.client = None
            self.db = None
            self.collection = None

    def set_collection(self, db_name, collection_name):
        if self.client is not None:
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
        else:
            print("[MongoDB] No client available to set collection.")

    def insert(self, data: Dict[str, Any]) -> bool:
        """
        Insert a single document into the collection.
        :param data: Document to insert.
        :return: True if successful, False otherwise.
        """
        if self.collection is None:
            print("[MongoDB] No collection selected for insert.")
            return False
        try:
            self.collection.insert_one(data)
            return True
        except Exception as e:
            print(f"[MongoDB] Insert failed: {e}")
            return False

    def fetch(
        self,
        query: Optional[Dict[str, Any]] = None,
        show_id: bool = False,
        time_field: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch documents from the collection based on the query and optional time range.
        :param query: Dictionary query to filter documents.
        :param show_id: If True, includes '_id' in results.
        :param time_field: Name of the datetime field to filter on (e.g., 'timestamp_utc').
        :param since: Only fetch documents with time_field >= since.
        :param until: Only fetch documents with time_field <= until.
        :return: List of documents.
        """
        if self.collection is None:
            print("[MongoDB] No collection selected for fetch.")
            return []

        mongo_query = query.copy() if query else {}

        # Add time-based filtering if requested
        if time_field and (since or until):
            time_query = {}
            if since:
                time_query["$gte"] = since
            if until:
                time_query["$lte"] = until
            mongo_query[time_field] = time_query

        projection = {} if show_id else {"_id": 0}
        try:
            documents = self.collection.find(mongo_query, projection)
            result = []
            for doc in documents:
                if show_id and "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                result.append(doc)
            return result[::-1]  # Reverse order for latest first
        except Exception as e:
            print(f"[MongoDB] Fetch failed: {e}")
            return []
