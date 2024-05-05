#Sample task for creating program: Write me a program that lifts up a cube (5cm) from a certain position and then drops it. Load the current arm position as a cube location and use it as a variable.
#Here is the sample code:
# Import is always needed
import modules.robot as robot
# If it is necessary to initialize Pose (usually using function calling), use literal values
# It is nice when you separate on multiple lines so it becomes more readable
cube_pose = robot.Pose(
    robot.Position(x=0.014, y=-0.292, z=-0.052),
    robot.Orientation(w=0, x=-0.690, y=0.724, z=0)
)
# create an instance (you don't need to know why but it is important for some reasons)
r = robot.Robot()
# Moves to cube position
r.move_to(pose=cube_pose, moveType="JUMP", velocity=100, acceleration=100, safe=False)
# attach cube
r.suck()
# create or change Pose (values are in meters so 0.05 is 5 cm on the z axis) 
cube_pose.position.z += 0.05
# move to change / new Pose
r.move_to(pose=cube_pose, moveType="JUMP", velocity=100, acceleration=100, safe=False)
# release cube
r.release()