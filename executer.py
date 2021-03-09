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
        self.paths = []
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

    def sendPathHTTP(self):
        _, img = cv2.imencode(".jpg", self.paths[0])
        bytes = img.tobytes()
        send_file(bytes, mimetype="image.jpeg")

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
        if "position" in data:
            self.addTask((data["position"]["x"], data["position"]["y"]))

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
            stop = self.queue.get()
            if stop == None:
                break
            print("Preparing to dispatch", stop)
            self.mutex.acquire()
            self.freeRobots.acquire()
            print("Dispatching", stop)
            self._assignTask(stop)

    def addRobot(self, name):
        self.robots.append(Robot(self.warehouse.client, name))
        self.paths.append(None)
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
                    self.warehouse.client,
                    self.robots[i].base,
                    -1,
                    sim.simx_opmode_blocking,
                )
                path = finder.find(pos, stop)
                _, img = cv2.imencode(".jpg", finder.visualizePath())
                img_bytes = img.tobytes()
                self.socketio.emit('path', base64.b64encode(img_bytes))
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
