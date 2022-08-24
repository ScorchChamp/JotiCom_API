import flask
from flask import request
import json
import time
import requests
import os

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

@app.route('/messages/<group>', methods=['GET'])
def messages(group):
    if not os.path.isfile(f'./messages/{group}.json'):
        with open(f'./messages/{group}.json', 'w') as f: json.dump({"data": []}, f, indent=4)
    with open(f'./messages/{group}.json') as f:
        data = json.load(f)
    with open(f'./messages/global.json') as f:
        global_data = json.load(f)

    data["data"] += global_data["data"]
    data["data"] = sorted(data["data"], key=lambda x: x["datetime"])
    return flask.jsonify(data)

@app.route('/messages/<group>', methods=['POST'])
def post_message(group):
    data = []
    if not os.path.isfile(f'./messages/{group}.json'):
        with open(f'./messages/{group}.json', 'w') as f: json.dump({"data": data}, f, indent=4)
    else:
        with open(f'./messages/{group}.json') as f:
            data = json.load(f)
    body = flask.request.json
    body["datetime"] = int(time.time())
    data["data"].append(body)
    with open(f'./messages/{group}.json', 'w') as f: json.dump(data, f, indent=4)
    return flask.jsonify(data), 200

@app.route('/live_locaties/<group>', methods=['GET'])
def live_locaties(group):
    if not os.path.isfile(f'./live_locaties/{group}.json'):
        with open(f'./live_locaties/{group}.json', 'w') as f: json.dump({"data": []}, f, indent=4)
    with open(f'./live_locaties/{group}.json') as f: 
        data = json.load(f)

    returnal = {"data": []}
    for item in data["data"]:
        dt = data["data"][item]
        dt["username"] = item
        returnal["data"].append(dt)
    return flask.jsonify(returnal)



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

    if not os.path.exists(f'./live_locaties'): os.mkdir(f'./live_locaties/')
    if not os.path.exists(f'./live_locaties/{api_key}.json'):
        with open(f'./live_locaties/{api_key}.json', 'w') as f: json.dump({"data": {}}, f, indent=4)

    with open(f'./live_locaties/{api_key}.json') as f: data = json.load(f)
    data["data"][username] = {"datetime": time.time(), "latitude": lat, "longitude": long}
    with open(f'./live_locaties/{api_key}.json', 'w') as f:
        json.dump(data, f, indent=4)
    return {"message": "success"}, 200

@app.route('/announcements')
def announcements():
    with open('announcements.json') as f: data = json.load(f)
    return flask.jsonify(data)


app.run(host='0.0.0.0', port=20000)