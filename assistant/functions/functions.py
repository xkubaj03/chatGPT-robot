from typing import Self
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
ROBOT_URL = os.getenv('ROBOT_URL')

startedSpec = {
    "name": "started",
    "description": "Checks if the robot is started",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def started(parameters):
    response = requests.get(ROBOT_URL + "/state/started")

    return response.text

startSpec = {
    "name": "start",
    "description": "Starts the robot",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def start(parameters):
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
    response = requests.put(ROBOT_URL + "/state/start", data=json_data, headers={'Content-Type': 'application/json'})
    
    return response.text

stopSpec = {
    "name": "stop",
    "description": "Stops the robot",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def stop(parameters):
    response = requests.put(ROBOT_URL + "/state/stop")

    return response.text

getPoseSpec = {
    "name": "getPose",
    "description": "Gets the robot's arm current position and orientation",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def getPose(parameters):
    response = requests.get(ROBOT_URL + "/eef/pose")

    return response.text

putPoseSpec = {
    "name": "putPose",
    "description": "Sets the robot's arm current position and orientation." + 
     "If I want to move the robots arm use default " +
     "orientation x = 1, x,z,w = 0, " +
     "velocity = 50, "+
     "acceleration = 0.5,"  +
     "safe = true "
     "moveType = JUMP ",
    "parameters": {      
        "type": "object",  
        "properties": {
            "moveType": {
                "type": "string",
                "enum": ["JUMP", "LINEAR", "JOINTS"],
                "description": "Type of movement",
            },
            "velocity": {
                "type": "number",
                "description": "Velocity of movement in percentage",
            },
            "acceleration": {
                "type": "number",
                "description": "Acceleration of movement",
            },
            "safe": {
                "type": "boolean",
                "description": "If true, the robot will avoid obstacles in set environment",
            },
            "orientation": {
                "type": "object",
                "properties": {
                    "w": {
                        "type": "number",
                    },
                    "x": {
                        "type": "number",
                    },
                    "y": {
                        "type": "number",
                    },
                    "z": {
                        "type": "number",
                    },
                },
            },
            "position": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                    },
                    "y": {
                        "type": "number",
                    },
                    "z": {
                        "type": "number",
                    },
                },
            },
        },
    },
    "requiredParams": ["moveType", "velocity", "acceleration", "safe","orientation", "position"],
}

def putPose(parameters):
    print(parameters)
    required_params = ["moveType", "velocity", "acceleration", "safe", "orientation", "position"]
    for param in required_params:
        if param not in parameters:
            print(f"Missing required parameter: {param}")
            return (f"Missing required parameter: {param}")

    moveType = parameters["moveType"]
    velocity = parameters["velocity"]
    acceleration = parameters["acceleration"]
    safe = parameters["safe"]
    orientation = parameters["orientation"]
    position = parameters["position"]

    full_url = f"{ROBOT_URL}/eef/pose?moveType={moveType}&velocity={velocity}&acceleration={acceleration}&safe={safe}"

    payload = {
        "orientation": orientation,
        "position": position
    }

    response = requests.put(full_url, json=payload, headers={'Content-Type': 'application/json'})

    return response.text

putHomeSpec = {
    "name": "putHome",
    "description": "Moves the robot arm to home position",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def putHome(parameters):
    response = requests.put(ROBOT_URL + "/home", headers={'accept': '*/*'})

    if response.status_code == 204:
            return "Comming home!"
    return response.text

suckSpec = {
    "name": "suck",
    "description": "Turns on the vacuum on (holds object).",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def suck(parameters):
    response = requests.put(ROBOT_URL + "/suck", headers={'accept': '*/*'})

    if response.status_code == 204:
            return "Sucked!"
    return response.text

releaseSpec = {
    "name": "release",
    "description": "Turns on the vacuum off (release object that arm holding).",
    "parameters": {      
        "type": "object",  
        "properties": {
        },
    },
    "requiredParams": [],
}

def release(parameters):
    response = requests.put(ROBOT_URL + "/release", headers={'accept': '*/*'})

    if response.status_code == 204:
            return "Released!"
    return response.text

beltSpeedSpec = {
    "name": "beltSpeed",
    "description": "Sets the belt speed and direction.",
    "parameters": {      
        "type": "object",  
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["forward", "backward"],
                "description": "Type of movement",
            },
            "velocity": {
                "type": "number",
                "description": "Velocity of movement in percentage",
            },
        },
        "requiredParams": ["direction", "velocity"],
    }
}

def beltSpeed(parameters):
    direction = parameters["direction"]
    velocity = parameters["velocity"]

    full_url = f"{ROBOT_URL}/conveyor/speed?velocity={velocity}&direction={direction}"

    response = requests.put(full_url, headers={'accept': '*/*'})

    if response.status_code == 204:
        return "Belt speed was succesfully set!"
    return response.text

beltDistanceSpec = {
    "name": "beltDistance",
    "description": "Sets the belt, distance and direction.",
    "parameters": {      
        "type": "object",  
        "properties": {
            "direction": {
                "type": "string",
                "enum": ["forward", "backward"],
                "description": "Type of movement",
            },
            "velocity": {
                "type": "number",
                "description": "Velocity of movement in percentage",
            },
            "distance": {
                "type": "number",
                "description": "Distance of movement in meters",
            },
        },
        "requiredParams": ["direction", "velocity", "distance"],
    }
}

def beltDistance(parameters):
    direction = parameters["direction"]
    velocity = parameters["velocity"]
    distance = parameters["distance"]

    full_url = f"{ROBOT_URL}/conveyor/distance?velocity={velocity}&direction={direction}&distance={distance}"

    response = requests.put(full_url, headers={'accept': '*/*'})

    if response.status_code == 204:
            return "Belt distance was succesfully set!"
    return response.text

saveTXTSpec = {
    "name": "saveTXT",
    "description": "Saves text to file",
    "parameters": {      
        "type": "object",  
        "properties": {
            "file_path": {
                "type": "string",
                "description": "File path",
            },
            "text": {
                "type": "string",
                "description": "Text to save",
            },
        },
    },
    "requiredParams": ["file_path", "text"],
}

def saveTXT(parameters):
    file_path = parameters["file_path"]
    text = parameters["text"]
    try:
        with open(file_path, 'w') as file:
            file.write(text)
        return (f"Text was succesfully saved! {file_path}")
    except Exception as e:
        return (f"Error occured: {e}")

userGreetingSpec = {
    "name": "userGreeting",
    "description": "Greets the user using their name and constant text.",
    "parameters": {      
        "type": "object",  
        "properties": {
            "name": {
                "type": "string",
                "description": "User name",
            },
        },
    },
    "requiredParams": ["name"],
}

def userGreeting(parameters):
    name = parameters["name"]
    return f"Hello {name}! I am your virtual assistant. I will help you with your dailY Tasks. How can I help you today?"




class FunctionHandler:
    functions = {
        "started":  {
            "Func": started,
            "Spec": startedSpec
        },
        "start":  {
            "Func": start,
            "Spec": startSpec
        },
        "stop":  {
            "Func": stop,
            "Spec": stopSpec
        },
        "saveTXT":  {
            "Func": saveTXT,
            "Spec": saveTXTSpec
        },
        "userGreeting":  {
            "Func": userGreeting,
            "Spec": userGreetingSpec
        },    
        "getPose":  {
            "Func": getPose,
            "Spec": getPoseSpec
        },
        "putPose":  {
            "Func": putPose,
            "Spec": putPoseSpec
        },
        "putHome":  {
            "Func": putHome,
            "Spec": putHomeSpec
        },
        "suck":  {
            "Func": suck,
            "Spec": suckSpec
        },
        "release":  {
            "Func": release,
            "Spec": releaseSpec
        },
        "beltSpeed":  {
            "Func": beltSpeed,
            "Spec": beltSpeedSpec
        },
        "beltDistance":  {
            "Func": beltDistance,
            "Spec": beltDistanceSpec
        },
    }
        
    def __init__(self):
        pass

    def getAllSpecs(self):
        return [func_info["Spec"] for func_name, func_info in self.functions.items()]
    
    def HandleFunction(self, function_name, parameters):
        print("!!!"+function_name + " called!!! poggers :O ")

        if function_name in self.functions:
            return self.functions[function_name]["Func"](parameters)
        else:
            raise Exception(f"Function {function_name} not found!")
        
