#%%
from robot import Robot
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
import sim
import threading

warehouse = Warehouse(19999)
robot0 = Robot(warehouse.client, "0")
robot1 = Robot(warehouse.client, "1")
end0 = (190, 150)
_, pos0  = sim.simxGetObjectPosition(robot0.client, robot0.base, -1, sim.simx_opmode_blocking)

finder0 = PathFinder(warehouse)
path0 = finder0.find(pos0, end0)
finder0.visualizePath()
#%%
tracker0 = PathTracker(path0, 5, 1.4, robot0, warehouse)


# _, pos1  = sim.simxGetObjectPosition(robot1.client, robot1.front, -1, sim.simx_opmode_blocking)
# finder1 = PathFinder(warehouse.width,warehouse.height,warehouse.toplpos[0], warehouse.toplpos[1])
end0 = (403, 740)
# path1 = finder1.find(warehouse.getImage(), pos1, end1)
# finder1.visualizePath()
# tracker1 = PathTracker(path1, 2.1, 1, robot1)

thread0 = threading.Thread(target=tracker0.track)
# thread1 = threading.Thread(target=tracker1.track)

thread0.start()
# thread1.start()

thread0.join()
# thread1.join()
