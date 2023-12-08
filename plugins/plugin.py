from flask import Flask, Response, request
import requests
import json

robot_url = "http://localhost:5018"

app = Flask(__name__)

def pass_response(response):
    flask_response = Response(response.text, status=response.status_code)

    for header in response.headers:
        flask_response.headers[header] = response.headers[header]

    return flask_response

@app.route('/', methods=['GET'])
def home():
    return "Running!"

@app.route('/state/started', methods=['GET'])
def started():
    response = requests.get(robot_url + "/state/started")

    return pass_response(response)

@app.route('/state/start', methods=['PUT'])
def start():
    data = {
      "orientation": {
        "w": 1,
        "x": 0,
        "y": 0,
        "z": 0
      },
      "position": {
        "x": 0,
        "y": 0,
        "z": 0
      }
    }
    
    json_data = json.dumps(data)
    response = requests.put(robot_url + "/state/start", data=json_data, headers={'Content-Type': 'application/json'})
    
    return pass_response(response)

@app.route('/state/stop', methods=['PUT'])
def stop():
    response = requests.put(robot_url + "/state/stop", headers={'accept': '*/*'})

    return pass_response(response)

@app.route('/eef/pose', methods=['GET'])
def get_pose():
    response = requests.get(robot_url + "/eef/pose")

    return pass_response(response)

@app.route('/eef/pose', methods=['PUT'])
def set_pose():
    requests_data = request.get_json()

    response = requests.put(robot_url + "/eef/pose", json=requests_data, headers={'Content-Type': 'application/json'})

    return pass_response(response)

@app.route('/home', methods=['PUT'])
def home_pose():
    response = requests.put(robot_url + "/home", headers={'accept': '*/*'})

    return pass_response(response)

@app.route('/suck', methods=['PUT'])
def suck():
    response = requests.put(robot_url + "/suck", headers={'accept': '*/*'})

    return pass_response(response)

@app.route('/release', methods=['PUT'])
def release():
    response = requests.put(robot_url + "/release", headers={'accept': '*/*'})

    return pass_response(response)

@app.route('/conveyor/speed', methods=['PUT'])
def set_speed():
    response = requests.put(robot_url + "/suck", headers={'accept': '*/*'})

    return pass_response(response)

@app.route('/conveyor/distance', methods=['PUT'])
def set_distance():
    response = requests.put(robot_url + "/suck", headers={'accept': '*/*'})

    return pass_response(response)

if __name__ == '__main__':
    app.run(port=5005)   
