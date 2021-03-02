from multiprocessing.pool import ThreadPool
import queue
import threading
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
from robot import Robot
import sim

from flask import Flask,request, abort
import flask


class Executer:
    def __init__(self, threads):
        self.pool = ThreadPool(processes=threads)
        self.queue = queue.Queue()
        self.warehouse = Warehouse(19999)
        self.robots = []
        self.app = Flask("Warehouse")
        self.loop = threading.Thread(target=self._dispatcher) 
        self.freeRobots = threading.Semaphore(value=0)
        self.mutex = threading.Lock()
        self.app.add_url_rule('/addTask', 'addTaskHTTP', self.addTaskHTTP, methods=['POST'])

    def startHTTPServer(self):
        self.app.run()

    def addTaskHTTP(self):
        if not request.json or not 'position' in request.json:
            abort(400)
        status_code = flask.Response(status=201)
        print(request.json)
        self.addTask((request.json['position']['x'], request.json['position']['y']))
        return status_code

    def addRobotHTTP(self):
        if not request.json or not 'robot' in request.json:
            abort(400)
        self.addRobot(request.json['robot']['suffix'])
        status_code = flask.Response(status=201)
        print(request.json)
        return status_code

    def startListening(self):
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
