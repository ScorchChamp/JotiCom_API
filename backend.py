import flask
import json


app = flask.Flask(__name__)
app.config['DEBUG'] = True

@app.route('/vossen_locaties', methods=['GET'])
def vossen_locaties():
    with open('vossen_locaties.json') as f:
        data = json.load(f)
    return flask.jsonify(data)

app.run(host='0.0.0.0', port=6000)