from dotenv import load_dotenv
from enum import Enum
import os
import requests
import json

load_dotenv()
URL = os.getenv('ROBOT_URL')


class Position:
    """
    Struct to store the position of the robot (values in meters)
    """
    def __init__(self, x: float, y: float, z: float):
        """
        Initializes the Position object with x, y and z

        Args:
            z (float): The z-coordinate in meters of the position.
            x (float): The x-coordinate in meters of the position.
            y (float): The y-coordinate in meters of the position.
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def to_dict(self):
        """
        Returns the Position object as a dictionary
        """
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    def __str__(self):
        """
        Returns the Position object as a JSON string
        """
        return json.dumps(self.to_dict(), indent=4)


class Orientation:
    """
    Struct to store the orientation of the robot (values in quaternions)
    """
    def __init__(self, w: float, x: float, y: float, z: float):
        """
        Initializes the Orientation object with w, x, y and z

        Args:
            w (float): The w-coordinate in quaternions of the orientation.
            x (float): The x-coordinate in quaternions of the orientation.
            y (float): The y-coordinate in quaternions of the orientation.
            z (float): The z-coordinate in quaternions of the orientation.
        """
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


    def to_dict(self):
        """
        Returns the Orientation object as a dictionary
        """
        return {
            "w": self.w,
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    def __str__(self):
        """
        Returns the Orientation object as a JSON string
        """
        return json.dumps(self.to_dict(), indent=4)


class Pose:
    """
    Struct to store position and orientation of the robot
    """
    def __init__(self, position: Position, orientation: Orientation):
        """
        Initializes the Pose object with position and orientation

        Args:
            position (Position): The position of the robot.
            orientation (Orientation): The orientation of the robot.
        """
        if not isinstance(position, Position):
            raise ValueError("1st parameter position must be of type Position")
        
        if not isinstance(orientation, Orientation):
            raise ValueError("2nd parameter orientation must be of type Orientation")
        
        self.position = position
        self.orientation = orientation
        

    def to_dict(self):
        """
        Returns the Pose object as a dictionary
        """
        return {
            "position": self.position.to_dict(),
            "orientation": self.orientation.to_dict()
        }
    
    def __str__(self):
        """
        Returns the Pose object as a JSON string
        """
        return json.dumps(self.to_dict(), indent=4)


class Mode(Enum):
    """
    Modes for robot (only difference is in error handling) 
    """

    DEFAULT = "default"
    ASSISTANT = "assistant"


def check_response(response: requests.Response, mode: Mode) -> tuple[str, bool]:
    """
    returns message or raise error (True if error, False if not)

    Args:
        response (requests.Response): The response from the robot.
        mode (Mode): The mode of the robot.
    """

    if response.ok:
        if response.text == "":
            return "Success!", False
        
        return response.text, False
    
    if mode == Mode.DEFAULT:
        raise requests.exceptions.HTTPError(f"Robot is not running as expected. Error: {response.text}")
    
    else:
        return (f"Robot is not running as expected. Error: {response.text}"), True
    

class Robot:
    """
    Class to control the robot
    """

    def __init__(self, url: str = URL, mode: Mode = Mode.DEFAULT): 
        """
        Initializes the Robot object and establishes connection to the robot
        """
        self.robot_url = url
        self.mode = mode

        # Check connection to robot
        try:
            response = requests.get(self.robot_url + "/state/started")

            if response.status_code != 200:
                raise Exception(f"Robot is not running as expected. Status code: {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to the Robot: {e}")
            

    def started(self) -> bool:
        """
        Returns True if the robot is started, False if not
        """
        response = requests.get(self.robot_url + "/state/started")

        msg, err = check_response(response, self.mode)

        if err:
            return msg

        if msg == "true\n":
            return True
        else:
            return False
    

    def start(self) -> str:
        """
        Starts the robot

        Returns:
            str: A message indicating the result of the operation.
        """
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
    
        msg, _ = check_response(response, self.mode)

        return msg
    

    def stop(self) -> str:
        """
        Stops the robot

        Returns:
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/state/stop")
        
        msg, _ = check_response(response, self.mode)

        return msg
    

    def get_pose(self) -> Pose:
        """
        Returns:
            Pose: The current pose of the robot.
        """
        response = requests.get(self.robot_url + "/eef/pose")

        text, err = check_response(response, self.mode)

        if err:
            return text

        tmp = json.loads(text)

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
    

    def move_to(self, pose: Pose, moveType: str, velocity: int = None, acceleration: int = None, safe: bool = None) -> str:
        """
        Moves the robot to the specified pose with various movement parameters.

        Args:
            pose (Pose): The target pose to move the robot to.
            moveType (str): The type of movement to perform ('JUMP', 'LINEAR', 'JOINS').
            velocity (int, optional): The velocity of the movement (1-100). Defaults to None.
            acceleration (int, optional): The acceleration of the movement (1-100). Defaults to None.
            safe (bool, optional): A flag to indicate safe movement. Defaults to None.

        Raises:
            ValueError: If the provided pose is not of type Pose.

        Returns:
            str: A message indicating the result of the operation.
        """

        if type(pose) is not Pose:
            raise ValueError("Pose must be of type Pose")

        full_url = f"{self.robot_url}/eef/pose?moveType={moveType}"

        if velocity is not None:
            full_url += f"&velocity={velocity}"

        if acceleration is not None:
            full_url += f"&acceleration={acceleration}"

        if safe is not None:
            full_url += f"&safe={safe}"

        response = requests.put(full_url, json=pose.to_dict(), headers={'Content-Type': 'application/json'})


        msg, _ = check_response(response, self.mode)

        return msg


    def home(self) -> str:
        """
        Calibrates the robot and moves to home position

        Returns:
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/home", headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


    def suck(self) -> str:
        """
        Turns on the vacuum. (Holds an object)

        returns:
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/suck", headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


    def release(self) -> str:
        """
        Turns off the vacuum. (Releases an object)

        Returns: 
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/release", headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg
   

    def belt_speed(self, direction: str, velocity: int) -> str: 
        """
        Starts the conveyor belt with the given velocity and direction

        Args:
            direction (str): The direction of the conveyor belt ('forward', 'backwards').
            velocity (int): The velocity of the conveyor belt (1-50).

        Returns:
            str: A message indicating the result of the operation.
        """

        full_url = f"{self.robot_url}/conveyor/speed?velocity={velocity}&direction={direction}"

        response = requests.put(full_url, headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


    def belt_distance(self, direction: str, velocity: int, distance: float) -> str:
        """
        Parameters: self, direction (forward, backwards), velocity(int 1 - 50), distance (float in meters)
        Moves the conveyor belt with the given velocity, direction and distance

        Args:
            direction (str): The direction of the conveyor belt ('forward', 'backwards').
            velocity (int): The velocity of the conveyor belt (1-50).
            distance (float): The distance to move the conveyor belt in meters.

        Returns:
            str: A message indicating the result of the operation.
        """

        direction = direction.lower()
        if direction != "forward" and direction != "backwards":
            return ("Direction must be either 'forward' or 'backwards'")

        full_url = f"{self.robot_url}/conveyor/distance?velocity={velocity}&direction={direction}&distance={distance}"

        response = requests.put(full_url, headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


