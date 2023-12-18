from functions import functions
import json
#$Env:PYTHONPATH += ";D:\Vskola\Bak\plugin\chatGPT-robot\assistant"
class Robot:
    def Started(self):
        if functions.started(None) == "true\n":
            return True
        else:
            return False
    
    def Start(self):
        tmp = functions.start(None)
        if tmp != "":
            raise Exception(tmp)
    
    def Stop(self):
        tmp = functions.stop(None)
        if tmp != "":
            raise Exception(tmp)

    def GetPose(self):
        return json.loads(functions.getPose(None))
    
    def PutPose(self, moveType, velocity, acceleration, safe, orientation, position): 
        parameters = {
            "moveType": moveType, 
            "velocity": velocity, 
            "acceleration": acceleration, 
            "safe": safe, 
            "orientation": orientation, 
            "position": position,
        }

        tmp = functions.putPose(parameters)
        if tmp != "":
            raise Exception(tmp)

    def MoveHome(self):
        tmp = functions.putHome(None)
        if tmp != "Comming home!":
            raise Exception(tmp)
        
    def Suck(self):
        tmp = functions.suck(None)
        if tmp != "Sucked!":
            raise Exception(tmp)
        
    def Release(self):
        tmp = functions.release(None)
        if tmp != "Released!":
            raise Exception(tmp)
        
    def BeltSpeed(self, direction, velocity): 
        parameters = {
            "direction": direction,
            "velocity": velocity,
        }

        tmp = functions.beltSpeed(parameters)
        if tmp != "Belt speed was succesfully set!":
            raise Exception(tmp)


    def BeltDistance(self, direction, velocity, distance):
        parameters = {
            "direction": direction,
            "velocity": velocity,
            "distance": distance,
        }

        tmp = functions.beltSpeed(parameters)
        if tmp != "Belt speed was succesfully set!":
            raise Exception(tmp)
