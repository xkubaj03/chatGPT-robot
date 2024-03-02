import json
import os
from datetime import datetime
import subprocess
import modules.robot as r
import modules.logger as l

def load_file(file_path):
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            return file.read()
            
    except Exception as e:
        return (f"Error occured: {e}")


class FunctionHandler:
    functions: dict
    robot: r.Robot
    robot_running = False

    def __init__(self, debug, url):
        self.debug = debug
        self.url = url

        #set up robot
        try:
            self.robot = r.Robot(url, "assistant")
            self.robot_running = True #This makes the robot functions available

        except Exception as e:  
            l.FancyPrint(l.Role.SYSTEM, f"Failed to connect to the Robot: {e} \nAssistent is unable to control the robot!")

        self.functions = {
            "started": self.started,        
            "start": self.start,
            "stop": self.stop,     
            "getPose": self.get_pose,
            "putPose": self.put_pose,
            "putHome": self.put_home,
            "suck": self.suck,
            "release": self.release,
            "beltSpeed": self.belt_speed,
            "beltDistance": self.belt_distance,
            "runSavedProgram": self.run_program,
            "saveTXT": self.save_txt,      
            "getSavedPrograms": self.get_saved_programs,
            "getSavedProgram": self.get_program,
        }
        

    def get_all_specs(self):
        """
        returns function specs and robot function specs (if robot is awailable)
        """

        json_data = load_file('./txt_sources/functions.json')
        function_specs = json.loads(json_data)
        
        if self.robot_running:
            json_data = load_file('./txt_sources/robot_func.json')
         
            function_specs.extend(json.loads(json_data))

        return function_specs

    
    def get_prompt_message(self):
        """
        returns initial prompt message filled with sample code
        """
    
        prompt = load_file('./txt_sources/prompt.txt')
        sample = load_file('./txt_sources/sample.py')

        # Insert sample code into prompt on ###CODE### position
        prompt = prompt.replace("###CODE###", sample)

        return prompt


    def get_welcome_message(self):
        return load_file('./txt_sources/intro.txt')


    def handle_function(self, function_name, parameters):
        """
        Calls function with given name and parameters (or raises exception if function is not found)
        """

        if(self.debug > 0):
            l.FancyPrint(l.Role.DEBUG, "!!!" + function_name + " called!!! poggers :O ")

        if function_name not in self.functions:
            raise KeyError(f"Function {function_name} not found!")
        
        return self.functions[function_name](parameters)


    def started(self, parameter):
        return str(self.robot.started())


    def start(self, parameters):
        return self.robot.start()


    def stop(self, parameters):
        return self.robot.stop()


    def get_pose(self, parameters):
        return str(self.robot.get_pose())


    def put_pose(self, parameters):
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


        return self.robot.move_to(
            pose, 
            parameters["moveType"], 
            parameters.get("velocity", None), 
            parameters.get("acceleration", None), 
            parameters.get("safe", None)
        )


    def put_home(self, parameters):
        return self.robot.home()


    def suck(self, parameters):
        return self.robot.suck()


    def release(self, parameters):
        return self.robot.release()


    def belt_speed(self, parameters):
        if "direction" not in parameters:
            return "Missing required parameter (direction)"
        
        if "velocity" not in parameters:
            return "Missing required parameter (velocity)"
        
        return self.robot.belt_speed(parameters["direction"], parameters["velocity"])


    def belt_distance(self, parameters):
        if "direction" not in parameters:
            return "Missing required parameter (direction)"
        
        if "velocity" not in parameters:
            return "Missing required parameter (velocity)"
        
        if "distance" not in parameters:
            return "Missing required parameter (distance)"
        
        return self.robot.belt_distance(parameters["direction"], parameters["velocity"], parameters["distance"])


    def save_txt(self, parameters):
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


    def get_saved_programs(self, parameters):
        ret = ""
        folder = "./src"

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            mod_time = os.path.getmtime(file_path)
            
            readable_time = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')

            ret += (f"{filename} - Last change: {readable_time}\n")
        
        return ret
    

    def get_program(self, parameters):
        if "file_path" not in parameters:
            return "Missing required parameter (file_path)"
        
        file_path = parameters["file_path"]

        if "./src/" not in file_path:
            file_path = "./src/" + file_path

        return load_file(file_path)


    def run_program(self, parameters):
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

 
    