from robot import Robot
from pathfinder import PathFinder
from pathtracker import PathTracker
import sim

robot = Robot(19999)
_, pos  = sim.simxGetObjectPosition(robot.client, robot.front, -1, sim.simx_opmode_blocking)
_, topleft = sim.simxGetObjectHandle(
    robot.client, "topleft", sim.simx_opmode_blocking)
_, bottomright = sim.simxGetObjectHandle(
    robot.client, "bottomright", sim.simx_opmode_blocking)
_, toplpos  = sim.simxGetObjectPosition(robot.client, topleft, -1, sim.simx_opmode_blocking)
_, bottomrpos  = sim.simxGetObjectPosition(robot.client, bottomright, -1, sim.simx_opmode_blocking)

finder = PathFinder(toplpos[0]-bottomrpos[0],bottomrpos[1]-toplpos[1], toplpos[0], toplpos[1])
path = finder.find(robot.getImage(), pos)
finder.visualizePath()
tracker = PathTracker(path, 1.5, 1, robot)
tracker.track()
