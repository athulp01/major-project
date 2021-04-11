#!/bin/env python
from executer import Executer

ROBOT_WIDHT = 5.5
LOOKDIST = 2.4

executer = Executer(4)
executer.addRobot("0")
executer.addRobot("1")
executer.startListening()
executer.startHTTPServer()
# executer.addTask((285, 467))
# executer.addTask((224, 143))
