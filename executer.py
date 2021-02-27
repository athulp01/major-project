from multiprocessing.pool import ThreadPool
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
from robot import Robot
import sim

class Executer:
    def __init__(self, threads):
        self.pool = ThreadPool(processes=threads)
        self.warehouse = Warehouse(19999)
        self.robots = []

    def addRobot(self, name):
        self.robots.append(Robot(self.warehouse.client, name))

    def assignTask(self, idx, stop):
        finder = PathFinder(self.warehouse)
        _, pos = sim.simxGetObjectPosition(
            self.warehouse.client, self.robots[idx].base, -1, sim.simx_opmode_blocking
        )

        path = finder.find(pos, stop)
        tracker = PathTracker(path, 2.8, 5, self.robots[idx], self.warehouse)
        self.pool.apply_async(tracker.track)

    def finishAll(self):
        self.pool.close()
        self.pool.join()

