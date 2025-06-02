from flask import Blueprint, json, request,jsonify
from ..extensions import MongoDB
from datetime import datetime
import pytz
db = MongoDB("actions", "GithubActions")

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST","GET"])
def receiver():
    if request.method == "POST":
        try:
            if request.headers['Content-Type'] == 'application/json':
                data = request.json
                try:
                    action = data['action'] 
                except:
                    action = None    
                
                if action == "opened" or action == "closed":
                    actiontype, id, timestamp = None,None,None
                    if action == "opened":
                        id = data['pull_request']['id']
                        timestamp = data['pull_request']['created_at']
                        actiontype = "PULL_REQUEST"
                    elif action == "closed":
                        timestamp = data['pull_request']['merged_at']
                        id = data['pull_request']['merge_commit_sha']
                        actiontype = "MERGE"

                    from_branch = data['pull_request']['head']['ref']
                    to_branch = data['pull_request']['base']['ref']
                    author = data['pull_request']['user']['login']
                    
                    dt = datetime.fromisoformat(timestamp)
                    utc_dt = dt.astimezone(pytz.UTC)
                    readable_format = utc_dt.strftime("%d-%B-%Y - %I:%M %p UTC")
                    schema = {
                        "request_id": id,
                        "author": author,
                        "action": actiontype,
                        "from_branch": from_branch,
                        "to_branch": to_branch,
                        "timestamp": readable_format
                    }
                    resp = db.insert(data=schema)
                    if resp == True:
                        schema["_id"] = str(schema["_id"])
                        return schema
                
                else:
                    branch = data['ref']
                    author = data['commits'][0]['author']
                    reqID = data['commits'][0]['id']
                    timestamp = data['commits'][0]['timestamp']
                    dt = datetime.fromisoformat(timestamp)
                    utc_dt = dt.astimezone(pytz.UTC)
                    readable_format = utc_dt.strftime("%d-%B-%Y - %I:%M %p UTC")
                    
                    schema = {
                        "request_id": reqID,
                        "author": author['name'],
                        "action": "PUSH",
                        "from_branch": branch.split("/")[-1],
                        "to_branch": branch.split("/")[-1],
                        "timestamp": readable_format
                    }
                    resp = db.insert(data=schema)
                    if resp == True:
                        schema["_id"] = str(schema["_id"])
                        return schema
            
            return {"error": "Invalid Data Type"}

        except Exception as e:
            print("Exception:" ,e)
            return {"error": str(e)}
    
    elif request.method == "GET":
        data = db.fetch(show_id=True)
        try: 
            for item in data:
                item['_id'] = str(item['_id'])  # Convert ObjectId to string
                return jsonify(data),200
        except Exception as e:
            print(f"Error processing data: {e}")
            return {"message": "Error processing data"}, 500    
    
    return {"message": "Method not allowed"}, 405