import flask
from flask import request
import json
import time
import requests
import os
import joticom_db as db

app = flask.Flask(__name__)
app.config['DEBUG'] = True

def check_params(body, needed_params):
    if not body: raise Exception(f"No data")
    for param in needed_params:
        if param not in body: raise Exception(f"Missing parameter: {param}")

def getEndpointData(endpoint):
    try:
        if not os.path.isfile(f'{endpoint}.json'): 
            try: refreshData(endpoint)
            except: pass
        with open(f'{endpoint}.json') as f: data = json.load(f)
        if (data['laatste_update'] + 60) < time.time(): 
            try: data = refreshData(endpoint)
            except: pass
        if endpoint == "scorelijst": data["data"] = sorted(data["data"], key=lambda x: x["plaats"])
        elif endpoint == "deelnemers": data["data"] = sorted(data["data"], key=lambda x: x["id"])
        else: data["data"] = sorted(data["data"], key=lambda d: d['datum']) 
        return data
    except Exception as e:
        return {"data": [], "error": str(e)}


def refreshData(endpoint):
    print("[LOG] Refreshing data for endpoint: " + endpoint)
    data = {"laatste_update": time.time()}
    data["data"] = []
    data["data"] += requests.get(f"https://jotihunt.net/api/1.0/{endpoint}").json()["data"]
    with open(f'{endpoint}.json', 'w') as f: json.dump(data, f, indent=4)
    return data

@app.route('/vossen_locaties/<api_key>', methods=['GET'])
def vossen_locaties(api_key):
    data = {"data": db.getVossenLocations(api_key)}
    if "data" in data: data["data"] = sorted(data["data"], key=lambda d: d['datetime']) 

    return_data = {"data": {
        "Alpha": [],
        "Bravo": [],
        "Charlie": [],
        "Delta": [],
        "Echo": [],
        "Foxtrot": []
    }}
    for locatie in data["data"]:
        return_data["data"][locatie["team"]].append(locatie)
    return flask.jsonify(return_data)

@app.route('/vossen_locaties/<api_key>', methods=['POST'])
def add_vossen_locaties(api_key):
    try: body = json.loads(request.data)
    except: return flask.jsonify({"error": "No body"}), 400
    
    try: check_params(body, ["vossen_team", "datetime", "location_type", "latitude", "longitude"])
    except Exception as e: return flask.jsonify({"error": str(e)}), 400
    print(body)
    try: db.addVossenLocation(api_key, body['vossen_team'], body['datetime'], body['location_type'], body['latitude'], body['longitude'])
    except Exception as e: return flask.jsonify({"error": "Database Error", "details": str(e)}), 500
    return flask.jsonify({"message": "success"}), 200

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
@app.route('/vossen', methods=['GET'])
def vossen(): return flask.jsonify(getEndpointData('vossen'))

@app.route('/messages/<api_key>', methods=['GET'])
def messages(api_key): return flask.jsonify({"data": db.getMessages(api_key)}), 200

@app.route('/messages/<api_key>', methods=['POST'])
def post_message(api_key):
    try: body = json.loads(request.data)
    except: return flask.jsonify({"error": "No body"}), 400
    
    try: check_params(body, ["username", "message"])
    except Exception as e: return flask.jsonify({"error": str(e)}), 400

    try: db.addMessage(body['username'], api_key, body['message'])
    except Exception as e: return flask.jsonify({"error": "Database Error"}), 500
    return flask.jsonify({"data": db.getMessages(api_key)}), 200


@app.route('/live_locaties/<api_key>', methods=['GET'])
def live_locaties(api_key): return flask.jsonify( {"data": db.getLocations(api_key)}), 200



@app.route('/live_locatie/<api_key>', methods=['POST'])
def live_locatie(api_key):
    try: body = json.loads(request.data)
    except: return flask.jsonify({"error": "No body"}), 400

    try: check_params(body, ["username", "latitude", "longitude"])
    except Exception as e: return flask.jsonify({"error": str(e)}), 400
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