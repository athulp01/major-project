from multiprocessing.pool import ThreadPool
import queue
import threading
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
from robot import Robot
import sim


class Executer:
    def __init__(self, threads):
        self.pool = ThreadPool(processes=threads)
        self.queue = queue.Queue()
        self.warehouse = Warehouse(19999)
        self.robots = []
        self.loop = threading.Thread(target=self._dispatcher) 
        self.freeRobots = threading.Semaphore(value=0)
        self.mutex = threading.Lock()

    def listen(self):
        self.loop.start()

    def _dispatcher(self):
        while True:
            stop = self.queue.get()
            if(stop == None):
                break
            print("Preparing to dispatch", stop)
            self.mutex.acquire()
            self.freeRobots.acquire()
            print("Dispatching", stop)
            self._assignTask(stop)

    def addRobot(self, name):
        self.robots.append(Robot(self.warehouse.client, name))
        self.freeRobots.release()
    
    def addTask(self, stop):
        self.queue.put(stop)

    def release(self, num):
        print("Releasing")
        self.freeRobots.release()


    def _assignTask(self, stop):
        for i in range(len(self.robots)):
            if not self.robots[i].busy:
                self.robots[i].makeBusy()
                finder = PathFinder(self.warehouse)
                _, pos = sim.simxGetObjectPosition(
                    self.warehouse.client, self.robots[i].base, -1, sim.simx_opmode_blocking
                )
                path = finder.find(pos, stop)
                finder.visualizePath()
                tracker = PathTracker(path, 2.8, 5, self.robots[i], self.warehouse)
                self.pool.apply_async(tracker.track, callback=self.release)
                self.mutex.release()
                return
        print("No free robots")

    def finishAll(self):
        self.queue.put(None)
        self.loop.join()
        self.mutex.acquire()
        self.pool.close()
        self.pool.join()
