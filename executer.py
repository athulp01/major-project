from multiprocessing.pool import ThreadPool
import base64
import queue
import threading
from flask.helpers import send_file

from flask.json import jsonify
import socketio
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
from robot import Robot
from flask_socketio import SocketIO
import cv2
import sim

from flask import Flask, request, abort
import flask


class Executer:
    def __init__(self, threads):
        self.pool = ThreadPool(processes=threads)
        self.queue = queue.Queue()
        self.warehouse = Warehouse(19999)
        self.robots = []
        self.tasks = [{}]
        self.app = Flask("Warehouse")
        self.socketio = SocketIO(self.app)
        self.socketio.on_event('addTask', self.handleAddTask)
        self.socketio.on_event('addRobot', self.handleAddRobot)
        self.loop = threading.Thread(target=self._dispatcher)
        self.freeRobots = threading.Semaphore(value=0)
        self.mutex = threading.Lock()
        self.app.add_url_rule("/<path:path>", "sendFile", self.sendFile, methods=["GET"])

    def handle_message(self,data):
        print('received message: ' + data)

    def sendFile(self, path):
        return flask.send_from_directory('./', path)

    def sendPosHTTP(self):
        pos = self.warehouse.warehouse_to_img(self.robots[0].getPos()[0], self.robots[0].getPos()[1])
        data = {'x':pos[0], 'y':pos[1]}
        return jsonify(data)

    def startHTTPServer(self):
        self.socketio.run(self.app)

    def stopHTTP(self):
        self.finishAll()
        status_code = flask.Response(status=201)
        return status_code

    def handleAddTask(self, data):
        points = [(data["pickup"]["x"], data["pickup"]["y"]), (data["drop"]["x"], data["drop"]["y"])]
        self.addTask(points)

    def handleAddRobot(self):
        if not request.json or not "robot" in request.json:
            abort(400)
        self.addRobot(request.json["robot"]["suffix"])
        status_code = flask.Response(status=201)
        print(request.json)
        return status_code

    def startListening(self):
        self.loop.start()

    def _dispatcher(self):
        while True:
            points = self.queue.get()
            if points == None:
                break
            print("Preparing to dispatch", points)
            self.mutex.acquire()
            self.freeRobots.acquire()
            print("Dispatching", points)
            self._assignTask(*points)

    def addRobot(self, name):
        self.robots.append(Robot(self.warehouse.client, name))
        self.freeRobots.release()

    def addTask(self, stop):
        self.queue.put(stop)
        self.tasks.append(stop)

    def release(self, num):
        print("Releasing")
        self.freeRobots.release()

    def _assignTask(self, pickup, drop):
        for i in range(len(self.robots)):
            if not self.robots[i].busy:
                self.robots[i].makeBusy()
                finder = PathFinder(self.warehouse)
                _, pos = sim.simxGetObjectPosition(
                    self.warehouse.client,
                    self.robots[i].base,
                    -1,
                    sim.simx_opmode_blocking,
                )
                start = self.warehouse.warehouse_to_img(pos[0], pos[1])
                pickupPath = finder.find(start, pickup)
                dropPath = finder.find(pickup, drop)
                #_, img = cv2.imencode(".jpg", finder.visualizePath())
                #img_bytes = img.tobytes()
                #self.socketio.emit('path', base64.b64encode(img_bytes))
                tracker = PathTracker(pickupPath, dropPath, 2.8, 5, self.robots[i], self.warehouse)
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
