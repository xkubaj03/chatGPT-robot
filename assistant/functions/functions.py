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

def started():
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

def stop():
    response = requests.put(ROBOT_URL + "/state/stop")

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
        
