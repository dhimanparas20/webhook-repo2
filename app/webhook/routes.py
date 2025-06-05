import os
from flask import Blueprint, request, jsonify, current_app
from ..extensions import MongoDB
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import logging

# Load environment variables from a .env file if present
load_dotenv()

# Get MongoDB collection and database names from environment variables
MONGO_DB =  os.getenv("MONGO_DB", "actions")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "GithubActions")


db = MongoDB(MONGO_DB, MONGO_COLLECTION)
db.set_collection(MONGO_DB, MONGO_COLLECTION)


webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')
"""
Blueprint for handling webhook events.
Provides endpoints for receiving and querying webhook data.
"""

def parse_iso8601(timestamp: str) -> datetime:
    """
    Parse an ISO8601 timestamp string to a timezone-aware datetime object.
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.astimezone(pytz.UTC)
    except Exception as e:
        raise ValueError(f"Invalid timestamp format: {timestamp}") from e

@webhook.route('/receiver', methods=["POST"])
def webhook_receiver():
    """
    Receives webhook events (POST) and stores them in MongoDB.
    """
    try:
        if request.headers.get('Content-Type') != 'application/json':
            return jsonify({"error": "Invalid Content-Type, expected application/json"}), 400

        data = request.get_json(force=True)
        action = data.get('action')

        # Handle Pull Request events
        if action in ("opened", "closed"):
            pr = data.get('pull_request', {})
            if action == "opened":
                event_id = pr.get('id')
                timestamp = pr.get('created_at')
                action_type = "PULL_REQUEST"
            else:  # closed
                event_id = pr.get('merge_commit_sha')
                timestamp = pr.get('merged_at')
                action_type = "MERGE"

            from_branch = pr.get('head', {}).get('ref')
            to_branch = pr.get('base', {}).get('ref')
            author = pr.get('user', {}).get('login')

        # Handle Push events
        else:
            commits = data.get('commits', [{}])
            commit = commits[0] if commits else {}
            event_id = commit.get('id')
            timestamp = commit.get('timestamp')
            action_type = "PUSH"
            from_branch = to_branch = data.get('ref', '').split('/')[-1]
            author = commit.get('author', {}).get('name')

        # Parse and format timestamp
        dt = parse_iso8601(timestamp)
        readable_format = dt.strftime("%d-%B-%Y - %I:%M %p UTC")

        schema = {
            "request_id": event_id,
            "author": author,
            "action": action_type,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": readable_format,
            "timestamp_utc": datetime.now().replace(tzinfo=pytz.UTC) 
        }
        # print(timestamp,datetime.now().replace(tzinfo=pytz.UTC) )

        if db.insert(data=schema):
            current_app.logger.info(f"New webhook event inserted: {schema}")
            # Fetch the inserted document to get its _id
            # inserted = db.fetch({"request_id": event_id}, show_id=True)
            # if inserted:
            #     inserted[0]['_id'] = str(inserted[0]['_id'])
            #     return jsonify(inserted[0]), 201
            return jsonify(schema), 201

        return jsonify({"error": "Database insert failed"}), 500

    except Exception as e:
        current_app.logger.error(f"Exception in webhook receiver: {e}")
        return jsonify({"error": str(e)}), 500

@webhook.route('/events', methods=["GET"])
def webhook_events():
    """
    Returns webhook events that occurred in the last 15 seconds (GET).
    """
    try:
        now = datetime.now().replace(tzinfo=pytz.UTC)
        sixty_seconds_ago = now - timedelta(seconds=60)
        # print(sixty_seconds_ago)
        query = {"timestamp_utc": {"$gte": sixty_seconds_ago, "$lte": now}}
        data = db.fetch(query, show_id=True)
        if data:
            for item in data:
                item['_id'] = str(item['_id'])
            current_app.logger.info(f"Fetched New Webhook events: {data}")
            return jsonify(data), 200
        current_app.logger.info(f"No New Webhook events Found in last 60 sec")
        return jsonify({}), 404
    except Exception as e:
        current_app.logger.error(f"Error processing data: {e}")
        return jsonify({"message": "Error processing data"}), 500