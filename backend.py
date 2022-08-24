import flask
from flask import request
import json
import time
import requests
import os
import joticom_db as db

app = flask.Flask(__name__)
app.config['DEBUG'] = True

def getEndpointData(endpoint):
    if not os.path.isfile(f'{endpoint}.json'): refreshData(endpoint)
    with open(f'{endpoint}.json') as f: data = json.load(f)
    if (data['laatste_update'] + 60) < time.time(): data = refreshData(endpoint)
    if endpoint == "scorelijst": data["data"] = sorted(data["data"], key=lambda x: x["plaats"])
    elif endpoint == "deelnemers": data["data"] = sorted(data["data"], key=lambda x: x["id"])
    else: data["data"] = sorted(data["data"], key=lambda d: d['datum']) 
    
    return data


def refreshData(endpoint):
    print("[LOG] Refreshing data for endpoint: " + endpoint)
    data = {"laatste_update": time.time()}
    data["data"] = []
    data["data"] += requests.get(f"https://jotihunt.net/api/1.0/{endpoint}").json()["data"]
    with open(f'{endpoint}.json', 'w') as f: json.dump(data, f, indent=4)
    return data

@app.route('/vossen_locaties', methods=['GET'])
def vossen_locaties():
    with open('vossen_locaties.json') as f:
        data = json.load(f)
    data["data"] = sorted(data["data"], key=lambda d: d['datetime']) 
    return flask.jsonify(data)

@app.route('/nieuws', methods=['GET'])
def nieuws(): return flask.jsonify(getEndpointData('nieuws'))
@app.route('/hints', methods=['GET'])
def hints(): return flask.jsonify(getEndpointData('hint'))
@app.route('/opdrachten', methods=['GET'])
def opdrachten(): return flask.jsonify(getEndpointData('opdracht'))
@app.route('/scores', methods=['GET'])
def scorelijst(): return flask.jsonify(getEndpointData('scorelijst'))
@app.route('/deelnemers', methods=['GET'])
def deelnemers(): return flask.jsonify(getEndpointData('deelnemers'))

@app.route('/messages/<api_key>', methods=['GET'])
def messages(api_key): return flask.jsonify({"data": db.getMessages(api_key)}), 200

@app.route('/messages/<api_key>', methods=['POST'])
def post_message(api_key):
    body = json.loads(request.data)
    print(body)
    if not body: return flask.jsonify({"error": "No data"}), 400
    if not 'username' in body: return flask.jsonify({"error": "No username"}), 400
    if not 'message' in body: return flask.jsonify({"error": "No message"}), 400
    try: db.addMessage(body['username'], api_key, body['message'])
    except Exception as e: return flask.jsonify({"error": "Database Error"}), 500
    return flask.jsonify({"data": db.getMessages(api_key)}), 200


@app.route('/live_locaties/<api_key>', methods=['GET'])
def live_locaties(api_key): return flask.jsonify( {"data": db.getLocations(api_key)}), 200



@app.route('/live_locatie/<api_key>', methods=['POST'])
def live_locatie(api_key):
    body = json.loads(request.data)
    print(body)
    if not body: return flask.jsonify({"error": "No data"}), 400
    if not 'username' in body: return flask.jsonify({"error": "No username"}), 400
    if not 'latitude' in body: return flask.jsonify({"error": "No latitude"}), 400
    if not 'longitude' in body: return flask.jsonify({"error": "No longitude"}), 400
    username = body['username']
    lat = body['latitude']
    long = body['longitude']

    try: db.addLocation(username, api_key, time.time(), lat, long)
    except Exception as e: 
        print(e)
        return {"error": "Database error"}, 500

    return {"message": "success"}, 200

@app.route('/announcements')
def announcements(): return flask.jsonify( {"data": db.getAnnouncement()}), 200

app.run(host='0.0.0.0', port=20000)