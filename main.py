#%%
from pathfinder import PathFinder
import eventlet
eventlet.monkey_patch()
from executer import Executer

ROBOT_WIDHT = 5
LOOKDIST = 2.8

executer = Executer(1)
executer.addRobot("0")
#executer.addRobot("1")
executer.startListening()
executer.startHTTPServer()
#executer.addTask((285, 467))
#executer.addTask((224, 143))

