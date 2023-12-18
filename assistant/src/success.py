from module.robot import Robot

robot = Robot()
if not robot.Started():
    robot.Start()
current_position = robot.GetPose()
print(current_position)