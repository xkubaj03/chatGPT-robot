from dotenv import load_dotenv
from enum import Enum
import os
import requests
import json
import math
from pyquaternion import Quaternion

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
    
    def rotate(self, angle: float, axis: str) -> 'Position':
        """
        Rotates the position around the specified axis

        Args:
            angle (float): The angle in degrees to rotate the position.
            axis (str): The axis to rotate around ('x', 'y', 'z').
        Raises:
            ValueError: If the axis is invalid.
        Returns:
            New position after rotation
        """
        rad = math.radians(angle)

        if axis == "x":
            x = self.x
            y = self.y * math.cos(rad) - self.z * math.sin(rad)
            z = self.y * math.sin(rad) + self.z * math.cos(rad)
        
        elif axis == "y":
            x = self.x * math.cos(rad) - self.z * math.sin(rad)
            y = self.y
            z = self.x * math.sin(rad) + self.z * math.cos(rad)
        
        elif axis == "z":
            x = self.x * math.cos(rad) - self.y * math.sin(rad)
            y = self.x * math.sin(rad) + self.y * math.cos(rad)
            z = self.z

        else:
            raise ValueError("Axis must be 'x', 'y', or 'z'")
        
        return Position(x, y, z)
        
    def to_dict(self) -> dict[str, float]:
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

    def rotate(self, angle_deg: float, axis: str) -> 'Orientation':
        """
        Rotates the orientation around the specified axis

        Args:
            angle_deg (float): The angle in degrees to rotate the orientation.
            axis (str): The axis to rotate around ('x', 'y', 'z').
        Raises:
            ValueError: If the axis is invalid.
        Returns:
            New orientation after rotation
        """
        angle_rad = math.radians(angle_deg)

        if axis == 'x':
            rotation_quaternion = Quaternion(axis=[1, 0, 0], angle=angle_rad)
        elif axis == 'y':
            rotation_quaternion = Quaternion(axis=[0, 1, 0], angle=angle_rad)
        elif axis == 'z':
            rotation_quaternion = Quaternion(axis=[0, 0, 1], angle=angle_rad)
        else:
            raise ValueError("Axis must be 'x', 'y', or 'z'")
        
        quat = Quaternion(w=self.w, x=self.x, y=self.y, z=self.z)
        rotated = rotation_quaternion * quat
        
        return Orientation(rotated.w, rotated.x, rotated.y, rotated.z)       
        
    def to_dict(self) -> dict[str, float]:
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
        

    def to_dict(self) -> dict[str, dict[str, float]]:
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
        Initializes the Robot object and establishes a connection to the robot
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
        Calibrates the robot and moves to the home position

        Returns:
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/home", headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


    def suck(self) -> str:
        """
        Turn on the vacuum. (Holds an object)

        returns:
            str: A message indicating the result of the operation.
        """
        response = requests.put(self.robot_url + "/suck", headers={'accept': '*/*'})

        msg, _ = check_response(response, self.mode)

        return msg


    def release(self) -> str:
        """
        Turn off the vacuum. (Releases an object)

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


    def get_joins(self) -> list[float]:
        """
        Args:
            pose (Pose, optional): The pose to get the joins from. 
        Returns:
            list[float]: The current joins of the robot.
        """
        response = requests.get(self.robot_url + "/joints") 

        msg, err = check_response(response, Mode.DEFAULT)

        if err:
            return msg

        return json.loads(msg)
    

    def calculate_ik(self, pose: Pose = None) -> list[float]:
        """
        Better get_joins, returns None if IK is not possible

        Args:
            pose (Pose, optional): The pose to calculate the IK from. Defaults to current pose.
        Returns:
            list: The calculated joins of the robot (1st to 5th joint).
        """
        if pose is None:
            pose = self.get_pose()
        
        
        data = json.dumps(pose.to_dict())

        response = requests.put(self.robot_url + "/ik", data=data, headers={'Content-Type': 'application/json'})

        msg, err = check_response(response, Mode.ASSISTANT)

        if err:
            if "Failed to compute IK." in msg:
                return None
            
            raise Exception(f"Robot is not running as expected. Error: {msg['message']}")
        
        data = json.loads(msg)
        
        values: list[float] = []
        for joint in data:
            values.append(joint["value"])

        return values


    def move_object(self, src_pose: Pose, dst_pose: Pose, velocity: int = 100, rtrn_to_origin: bool = False) -> str:
        """
        Moves an object from one pose to another
        Moves the robot to the source pose, picks up the object, moves to the destination pose, and releases the object.
        (Optional: Returns to the source pose after the operation.)

        Args:
            src_pose (Pose): The source pose of the object.
            dst_pose (Pose): The destination pose of the object.
            velocity (int, optional): The velocity of the movement (1-100). Defaults to 100.
            rtrn_to_origin (bool, optional): A flag to indicate if the robot should return to the source pose after the operation. Defaults to False.

        Returns:
            str: A message indicating the result of the operation.
        """
        origin = self.get_pose()
        
        if self.calculate_ik(src_pose) is None or self.calculate_ik(dst_pose) is None:
            raise ValueError("Invalid poses")
                
        self.move_to(src_pose, "LINEAR", velocity)
        self.suck()
        self.move_to(dst_pose, "JUMP", velocity)
        
        if rtrn_to_origin:
            self.move_to(origin, "LINEAR", velocity)
        
        return "Success!"
    

    def rotate_arm_degrees(self, angle_deg: float, velocity: int = 100, maintain_ori: bool = False) -> str:
        """
        Rotates the arm to the specified angle (z-axis rotation)

        Args:
            angle_deg (float): The angle in degrees to rotate the arm to. (Positive value = clockwise, Negative value = counterclockwise)
            velocity (int, optional): The velocity of the movement (1-100). Defaults to 100.
            maintain_ori (bool, optional): A flag to indicate if the orientation should be maintained. Defaults to False.

        Returns:
            str: A message indicating the result of the operation.
        """
        pose = self.get_pose()
        
        pose.position.rotate(angle_deg, "z")
        
        
        if not maintain_ori or self.calculate_ik(pose) is None:
            pose.orientation.rotate(angle_deg, "z")
        
        return self.move_to(pose, "LINEAR", velocity)


    @staticmethod
    def fix_orientation(dest_pose: Pose, src_pose: Pose = Pose(Position(20,0,0),Orientation(0,0,0,0))) -> int:
        print(f"Pose1: [{dest_pose.position.x}, {dest_pose.position.y}], Pose2: [{src_pose.position.x}, {src_pose.position.y}]")

        numenator = dest_pose.position.x * src_pose.position.x + dest_pose.position.y * src_pose.position.y
        norm1 = math.sqrt(dest_pose.position.x**2 + dest_pose.position.y**2)
        norm2 = math.sqrt(src_pose.position.x**2 + src_pose.position.y**2)
        cos = numenator / (norm1 * norm2)
        angle_rad = math.acos(cos)
        angle_deg = math.degrees(angle_rad)
        # TODO: zjistit směr otáčení, orotovat a vrátit z5
        return angle_deg
    