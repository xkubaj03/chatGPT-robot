from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()


class Pose:
    def __init__(self, position, orientation):
        if not isinstance(position, Position):
            raise Exception("1st parameter position must be of type Position")
        
        if not isinstance(orientation, Orientation):
            raise Exception("2nd parameter orientation must be of type Orientation")
        
        self.position = position
        self.orientation = orientation
        

    def to_dict(self):
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict()
        }
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


class Position:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


class Orientation:
    def __init__(self, w, x, y, z):
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


    def to_dict(self):
        return {
            "w": self.w,
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    def __str__(self):
        return json.dumps(self.to_dict(), indent=4)


class Robot:
    robot_url = ""
    type = "" 

    def __init__(self, url = os.getenv('ROBOT_URL'), type = "default"): 
        if type != "default" and type != "assistant":
            raise Exception("Type must be either 'default' or 'assistant'")
        
        self.robot_url = url
        self.type = type

        try:
            response = requests.get(self.robot_url + "/state/started")

            if response.status_code != 200:
                raise Exception(f"Robot is not running as expected. Status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to the Robot: {e}")
            

    def Started(self):
        response = requests.get(self.robot_url + "/state/started")


        if self.type == "default" and response.status_code != 200:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 200:
             return (f"Robot is not running as expected.  Error: {response.text}")


        if response.text == "true\n":
            return True
        else:
            return False
    

    def Start(self):
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
        response = requests.put(self.robot_url + "/state/start", data=json_data, headers={'Content-Type': 'application/json'})
    
        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        
        return response.text
    

    def Stop(self):
        response = requests.put(self.robot_url + "/state/stop")
        
        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")

        return "Stopped!"
    

    def GetPose(self):
        response = requests.get(self.robot_url + "/eef/pose")

        if self.type == "default" and response.status_code != 200:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 200:
             return (f"Robot is not running as expected. Error: {response.text}")


        tmp = json.loads(response.text)

        return Pose(
            Position(
                tmp['position']['x'], 
                tmp['position']['y'], 
                tmp['position']['z']
            ), 
            Orientation(
                tmp['orientation']['w'], 
                tmp['orientation']['x'], 
                tmp['orientation']['y'], 
                tmp['orientation']['z']
            )
        )
    

    def PutPose(self, pose, moveType, velocity="none", acceleration="none", safe="none"):
        if type(pose) is not Pose:
            raise Exception("Pose must be of type Pose")

        full_url = f"{self.robot_url}/eef/pose?moveType={moveType}"

        if velocity != "none":
            full_url += f"&velocity={velocity}"

        if acceleration != "none":
            full_url += f"&acceleration={acceleration}"

        if safe != "none":
            full_url += f"&safe={safe}"

        response = requests.put(full_url, json=pose.to_dict(), headers={'Content-Type': 'application/json'})


        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        

        return "Position set!"


    def Home(self):
        response = requests.put(self.robot_url + "/home", headers={'accept': '*/*'})

        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
             
        return "Success!"


    def Suck(self):
        response = requests.put(self.robot_url + "/suck", headers={'accept': '*/*'})

        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        
        return "Sucked!"


    def Release(self):
        response = requests.put(self.robot_url + "/release", headers={'accept': '*/*'})

        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        
        return "Released!"
   

    def BeltSpeed(self, direction, velocity): 
        full_url = f"{self.robot_url}/conveyor/speed?velocity={velocity}&direction={direction}"

        response = requests.put(full_url, headers={'accept': '*/*'})

        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        
        return "Belt speed was succesfully set!"


    def BeltDistance(self, direction, velocity, distance):
        direction = direction.lower()
        if direction != "forward" and direction != "backwards":
            return ("Direction must be either 'forward' or 'backwards'")

        full_url = f"{self.robot_url}/conveyor/distance?velocity={velocity}&direction={direction}&distance={distance}"

        response = requests.put(full_url, headers={'accept': '*/*'})

        if self.type == "default" and response.status_code != 204:
            raise Exception(f"Robot is not running as expected. Error: {response.text}")
                    
        if self.type == "assistant" and response.status_code != 204:
             return (f"Robot is not running as expected. Error: {response.text}")
        
        return "Belt distance was succesfully set!"


