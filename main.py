#%%
import sim
from executer import Executer

ROBOT_WIDHT = 5
LOOKDIST = 2.8

executer = Executer(4)
executer.addRobot("0")
executer.addRobot("1")

executer.assignTask(0, (403, 740))
executer.assignTask(1, (224, 143))

executer.finishAll()
