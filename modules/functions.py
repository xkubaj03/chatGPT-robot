import json
import os
from datetime import datetime
import subprocess
import modules.robot as r


class FunctionHandler:
    prompt_message = ""
    welcome_message = ""
    function_specs = []
    robot: r.Robot

    defaultValues = {
            "moveType": "JUMP", # JUMP, LINEAR, JOINTS
            "velocity": 100,
            "acceleration": 100,
            "safe": True,
            "orientation": {
                "w": 0,
                "x": 1,
                "y": 0,
                "z": 0
            },
            "platform_A": {
                "position": {
                    "x": 0.014,
                    "y": -0.293,
                    "z": -0.104
                },
                "orientation": {
                    "w": 0,
                    "x": -0.691,
                    "y": 0.723,
                    "z": 0
                }
            },
            "platform_B": {
                "position": {
                    "x": 0.0903,
                    "y": -0.281,
                    "z": -0.1038
                },
                "orientation": {
                    "w": 0,
                    "x": -0.59,
                    "y": 0.807,
                    "z": 0
                }
            },
            "beltPosition": {
                "position": {
                    "x": 0.325,
                    "y": -0.021,
                    "z": -0.047
                },
                "orientation": {
                    "w": 0,
                    "x": -0.59,
                    "y": 0.807,
                    "z": 0
                }
            },
        }


    def __init__(self, debug, url):
        self.debug = debug
        self.url = url

        #set up robot
        function_specs = False

        try:
            self.robot = r.Robot(url, "assistant")
            function_specs = True

        except Exception as e:
            print(f"Failed to connect to the Robot: {e} \nAssistent is unable to control the robot!")

        #set up function specs
        with open('./txt_sources/functions.txt', 'r', encoding='utf-8') as file:
            json_data = file.read()

        self.function_specs = json.loads(json_data)

        if function_specs:
            with open('./txt_sources/robot_func.txt', 'r', encoding='utf-8') as file:
                json_data = file.read()
         
            self.function_specs.extend(json.loads(json_data))

        
        with open('./txt_sources/prompt.txt', 'r', encoding='utf-8') as file:
            self.prompt_message = file.read()

        
        with open('./txt_sources/intro.txt', 'r', encoding='utf-8') as file:
            self.welcome_message = file.read()
 

    def getAllSpecs(self):
        return self.function_specs

    
    def getPrompt_message(self):
        return self.prompt_message
    
    def get_welcome_message(self):
        return self.welcome_message
    
    def HandleFunction(self, function_name, parameters):
        if(self.debug > 0):
            print("!!!" + function_name + " called!!! poggers :O ")

        if function_name not in self.functions:
            raise Exception(f"Function {function_name} not found!")
        
        return self.functions[function_name](self, parameters)

    def started(self, parameter):
        return str(self.robot.Started())


    def start(self, parameters):
        return self.robot.Start()


    def stop(self, parameters):
        return self.robot.Stop()


    def getPose(self, parameters):
        return str(self.robot.GetPose())


    def putPose(self, parameters):
        if "moveType" not in parameters:
            return "Missing required parameter (moveType)"
        
        if "pose" not in parameters:
            return "Missing required parameter (pose)"
        
        if "position" not in parameters["pose"] or \
            "orientation" not in parameters["pose"]:
            return "Pose missing required (position or orientation)"
    

        pose = r.Pose(
            r.Position(
                parameters["pose"]["position"]["x"], 
                parameters["pose"]["position"]["y"], 
                parameters["pose"]["position"]["z"]
            ),
            r.Orientation(
                parameters["pose"]["orientation"]["w"], 
                parameters["pose"]["orientation"]["x"], 
                parameters["pose"]["orientation"]["y"], 
                parameters["pose"]["orientation"]["z"]            
            )                           
        )        


        return self.robot.PutPose(
            pose, 
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
        if "direction" not in parameters:
            return "Missing required parameter (direction)"
        
        if "velocity" not in parameters:
            return "Missing required parameter (velocity)"
        
        return self.robot.BeltSpeed(parameters["direction"], parameters["velocity"])


    def beltDistance(self, parameters):
        if "direction" not in parameters:
            return "Missing required parameter (direction)"
        
        if "velocity" not in parameters:
            return "Missing required parameter (velocity)"
        
        if "distance" not in parameters:
            return "Missing required parameter (distance)"
        
        return self.robot.BeltDistance(parameters["direction"], parameters["velocity"], parameters["distance"])

    def saveTXT(self, parameters):
        if "file_path" not in parameters:
            return "Missing required parameter (file_path)"
        
        if "text" not in parameters:
            return "Missing required parameter (text)"
        
        # Static check for program
        if parameters["file_path"].endswith(".py"):
            if "import modules.robot as robot" not in parameters["text"]:
                return "Program must contain \"import modules.robot as robot\""

            if "= robot.Robot()" not in parameters["text"]:
                return "Program must contain robot initialization: \"r = robot.Robot()\""

        try:
            with open(parameters["file_path"], 'w', encoding="utf-8") as file:
                file.write(parameters["text"])

            return (f'Text was succesfully saved! {parameters["file_path"]}')
        
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
        if "file_path" not in parameters:
            return "Missing required parameter (file_path)"
        
        file_path = parameters["file_path"]

        if "./src/" not in file_path:
            file_path = "./src/" + file_path

        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                return file.read()
            
        except Exception as e:
            return (f"Error occured: {e}")


    def runSavedProgram(self, parameters):
        if "file_path" not in parameters:
            return "Missing required parameter (file_path)"
        
        file_path = parameters["file_path"]

        if "./src/" not in file_path:
            file_path = "./src/" + file_path
        
        try:
            result = subprocess.run(["python", file_path], capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                return f"Program was successfully run! Output:\n{output}"
            
            else:
                error = result.stderr
                return f"Program exited with errors. Error:\n{error}"
            
        except Exception as e:
            return f"Error occurred: {e}"

 
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
        "runSavedProgram": runSavedProgram,
        "saveTXT": saveTXT,      
        "getSavedPrograms": getSavedPrograms,
        "getSavedProgram": getSavedProgram,
    }

