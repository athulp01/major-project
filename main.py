from robot import Robot
from pathfinder import PathFinder
from pathtracker import PathTracker

robot = Robot(19999)
finder = PathFinder(0,0,0,0)
path = finder.find(robot.getImage())
# finder.visualizePath()
tracker = PathTracker(path, 1.4, 1, robot)
tracker.track()