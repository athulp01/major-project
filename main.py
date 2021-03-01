#%%
from executer import Executer

ROBOT_WIDHT = 5
LOOKDIST = 2.8

executer = Executer(4)
print("Adding robo0")
executer.addRobot("0")
executer.listen()

print("addin task")
executer.addTask((285, 467))
executer.addTask((224, 143))
print("addin task")

executer.finishAll()
