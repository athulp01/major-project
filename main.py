#%%
from executer import Executer
from flask import Flask,request, abort
import flask

ROBOT_WIDHT = 5
LOOKDIST = 2.8

app = Flask("warehouse")
executer = Executer(4)
executer.addRobot("0")
executer.startListening()
executer.startHTTPServer()
#executer.addTask((285, 467))
#executer.addTask((224, 143))

