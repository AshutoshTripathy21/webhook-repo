from flask import Flask, request, jsonify, render_template
import json
from pymongo import MongoClient
from bson.json_util import dumps
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["github_events"]
collection = db["events"]


@app.route("/")
def index():
    #print(request.data)
    return render_template("events.html")

@app.route('/webhook', methods=['POST'])
def api_gh_message():
    if request.headers['Content-Type'] == 'application/json':
        my_info = request.get_json()
        if 'pusher' in my_info:  
            formatted_info = {
                'author': my_info['pusher']['name'],
                'action': 'PUSH',
                'from_branch': '',  
                'to_branch': '',    
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        elif 'pull_request' in my_info:  
            formatted_info = {
                'author': my_info['pull_request']['user']['login'],
                'action': 'PULL_REQUEST',
                'from_branch': my_info['pull_request']['head']['ref'],
                'to_branch': my_info['pull_request']['base']['ref'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        elif 'ref' in my_info:
            branch_parts = my_info['ref'].split('/')
            from_branch = branch_parts[-2]
            to_branch = branch_parts[-1]
            formatted_info = {
                'author': my_info['pusher']['name'],
                'action': 'MERGE',
                'from_branch': from_branch,
                'to_branch': to_branch,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        collection.insert_one(formatted_info)
        print(dumps(formatted_info))
        return "Event received", 200

@app.route('/events')
def events():
    events = list(collection.find({}))
    formatted_events = []
    for event in events:
        
        if 'author' in event:
            formatted_event = {
                'author': event['author'],
                'action': event.get('action', ''),
                'from_branch': event.get('from_branch', ''),
                'to_branch': event.get('to_branch', ''),
                'timestamp': event.get('timestamp', '')
            }
            formatted_events.append(formatted_event)
    return jsonify(formatted_events)


if __name__ == "__main__":
    app.run(debug=True)
