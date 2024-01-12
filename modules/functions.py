from typing import Self
import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import subprocess
import modules.robot as robot


load_dotenv()
ROBOT_URL = os.getenv('ROBOT_URL')

class FunctionHandler:
    codeCreatorText = ""
    functionSpecs = []
    robot: robot.Robot

    defaultValues = {
            'moveType': 'JUMP', # JUMP, LINEAR, JOINTS
            'velocity': 100,
            'acceleration': 100,
            'safe': True,
            'orientation': {
                'w': 0,
                'x': 1,
                'y': 0,
                'z': 0
            },
        }


    def __init__(self):
        #set up robot
        FunctionSpecs = False

        try:
            self.robot = robot.Robot(ROBOT_URL)
            FunctionSpecs = True

        except Exception as e:
            print(f"Failed to connect to the Robot: {e} \nAssistent is unable to control the robot!")

        #set up function specs
        with open('./txt_sources/functions.txt', 'r', encoding='utf-8') as file:
            json_data = file.read()

        self.functionSpecs = json.loads(json_data)

        if FunctionSpecs:
            with open('./txt_sources/robot_func.txt', 'r', encoding='utf-8') as file:
                json_data = file.read()
         
            self.functionSpecs.extend(json.loads(json_data))

        #set up code creator text
            with open('./txt_sources/codeCreatorText.txt', 'r', encoding='utf-8') as file:
                self.codeCreatorText = file.read()
 

    def getAllSpecs(self):
        return self.functionSpecs
        
    
    def HandleFunction(self, function_name, parameters):
        print("!!!" + function_name + " called!!! poggers :O ")

        if function_name in self.functions:
            return self.functions[function_name](self, parameters)
        else:
            raise Exception(f"Function {function_name} not found!")
        

    def started(self, parameter):
        return str(self.robot.Started())


    def start(self, parameters):
        return self.robot.Start()


    def stop(self, parameters):
        return self.robot.Stop()


    def getPose(self, parameters):
        return str(self.robot.GetPose())


    def putPose(self, parameters):
        if ("moveType" not in parameters) or ("pose" not in parameters):
            return "Missing required parameter: moveType or pose"

        """robot.Pose(
            parameters["pose"]["orientation"]["w"], 
            parameters["pose"]["orientation"]["x"], 
            parameters["pose"]["orientation"]["y"], 
            parameters["pose"]["orientation"]["z"], 
            parameters["pose"]["position"]["x"], 
            parameters["pose"]["position"]["y"], 
            parameters["pose"]["position"]["z"]
        )  """      


        return self.robot.PutPose(
            parameters["pose"], 
            parameters["moveType"], 
            parameters.get("velocity", "none"), 
            parameters.get("acceleration", "none"), 
            parameters.get("safe", "none")
        )


    def putHome(self, parameters):
        return self.robot.Home()


    def suck(self, parameters):
        return self.robot.Suck()


    def release(self, parameters):
        return self.robot.Release()


    def beltSpeed(self, parameters):
        return self.robot.BeltSpeed(parameters["direction"], parameters["velocity"])


    def beltDistance(self, parameters):
        return self.robot.BeltDistance(parameters["direction"], parameters["velocity"], parameters["distance"])


    def getDefValues(self, parameters):
        return json.dumps(FunctionHandler.defaultValues)


    def setDefValue(self, parameters):
        key = parameters["key"]
        value = parameters["value"]

        if key == "moveType":
            if value not in ["JUMP", "LINEAR", "JOINTS"]:
                return "Invalid value for moveType. Valid values are: JUMP, LINEAR, JOINTS"
        elif key == "velocity":
            if value < 0 or value > 100:
                return "Invalid value for velocity. Valid values are: 0-100"
        elif key == "acceleration":
            if value < 0 or value > 1:
                return "Invalid value for acceleration. Valid values are: 0-1"
        elif key == "safe":
            if value not in [True, False]:
                return "Invalid value for safe. Valid values are: True, False"
        #TODO: Check orientation 

        FunctionHandler.defaultValues[key] = value

        return "Default value was succesfully set!"


    def saveTXT(self, parameters):
        file_path = parameters["file_path"]
        text = parameters["text"]
        try:
            with open(file_path, 'w') as file:
                file.write(text)
            return (f"Text was succesfully saved! {file_path}")
        except Exception as e:
            return (f"Error occured: {e}")


    def getSavedPrograms(self, parameters):
        ret = ""
        folder = "./src"

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            mod_time = os.path.getmtime(file_path)
            
            readable_time = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            ret += (f"{filename} - Last change: {readable_time}\n")
        
        return ret
    

    def getSavedProgram(self, parameters):
        file_path = "./src/" + parameters["file_path"]
        try:
            with open(file_path, 'r') as file:
                return file.read()
            
        except Exception as e:
            return (f"Error occured: {e}")


    def runSavedProgram(self, parameters):
        file_path = parameters["file_path"]
        try:
            subprocess.run(["python", file_path])
            return (f"Program was succesfully run! {file_path}")
        except Exception as e:
            return (f"Error occured: {e}")


    def userGreeting(self, parameters):
        name = parameters["name"]
        return f"Hello {name}! I am your virtual assistant. I will help you with your dailY Tasks. How can I help you today?"


    def codeCreator(self, parameters):
        return self.codeCreatorText


    functions = {
        "started": started,        
        "start": start,
        "stop": stop,     
        "getPose": getPose,
        "putPose": putPose,
        "putHome": putHome,
        "suck": suck,
        "release": release,
        "beltSpeed": beltSpeed,
        "beltDistance": beltDistance,
        "userGreeting": userGreeting,
        "getDefValues": getDefValues,
        "setDefValue": setDefValue,
        "codeCreator": codeCreator,
        "runSavedProgram": runSavedProgram,
        "saveTXT": saveTXT,      
        "getSavedPrograms": getSavedPrograms,
        "getSavedProgram": getSavedProgram,
    }

