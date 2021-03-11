from multiprocessing.context import Process
from multiprocessing.pool import Pool
from multiprocessing import Queue
import queue
import threading
from flask.helpers import send_file

from flask.json import jsonify
from pathfinder import PathFinder
from pathtracker import PathTracker
from warehouse import Warehouse
from robot import Robot
from flask_socketio import SocketIO
import sim

from flask import Flask, request, abort
import flask


class Executer:
    def __init__(self, threads):
        #self.pool = Pool(processes=threads)
        self.queue = queue.Queue()
        self.warehouse = Warehouse(19999)
        self.robots = []
        self.tasks = []
        self.app = Flask("Warehouse")
        self.socketio = SocketIO(self.app,logger=True, engineio_logger=True, ping_timeout=120, ping_interval=30)
        self.socketio.on_event("addTask", self.handleAddTask)
        self.socketio.on_event("addRobot", self.handleAddRobot)
        self.loop = threading.Thread(target=self._dispatcher)
        self.freeRobots = threading.Semaphore(value=0)
        self.app.add_url_rule(
            "/<path:path>", "sendFile", self.sendFile, methods=["GET"]
        )
        self.app.add_url_rule("/getTasks", "sendTasksHTTP", self.sendTasksHTTP)

    def handle_message(self, data):
        print("received message: " + data)

    def handleGetTask(self):
        self.socketio.emit("get")

    def sendFile(self, path):
        return flask.send_from_directory("./", path)

    def sendPosHTTP(self):
        pos = self.warehouse.warehouse_to_img(
            self.robots[0].getPos()[0], self.robots[0].getPos()[1]
        )
        data = {"x": pos[0], "y": pos[1]}
        return jsonify(data)

    def sendTasksHTTP(self):
        return jsonify(self.tasks)

    def startHTTPServer(self):
        print("start server")
        self.socketio.run(self.app)

    def stopHTTP(self):
        self.finishAll()
        status_code = flask.Response(status=201)
        return status_code

    def handleAddTask(self, data):
        self.addTask(data)
        self.tasks.append(data)

    def handleAddRobot(self):
        if not request.json or not "robot" in request.json:
            abort(400)
        self.addRobot(request.json["robot"]["suffix"])
        status_code = flask.Response(status=201)
        print(request.json)
        return status_code

    def startListening(self):
        self.loop.start()
        #self.socketio.start_background_task(self._dispatcher)

    def _dispatcher(self):
        while True:
            print("start listening")
            points = self.queue.get()
            if points == None:
                break
            print("Preparing to dispatch", points)
            self.freeRobots.acquire()
            print("Dispatching", points)
            self._assignTask(points)

    def addRobot(self, name):
        self.robots.append(0)
        self.freeRobots.release()

    def addTask(self, stop):
        self.queue.put(stop)

    def release(self, num):
        print("Releasing")
        self.freeRobots.release()

    def _assignTask(self, task):
        pickup, drop = (task["pickup"]["x"], task["pickup"]["y"]), (
            task["drop"]["x"],
            task["drop"]["y"],
        )
        for i in range(len(self.robots)):
            if self.robots[i] == 0:
                image = self.warehouse.getImage()
                pos = self.warehouse.getRoboPos("0")
                self.warehouse.close()
                p = Process(target=self.doTask, args=["0", image, pos, pickup, drop])
                p.start()
                p.join()
                break

    def doTask(self, robot, image, pos, pickup, drop):
        finder = PathFinder(self.warehouse, image)
        start = self.warehouse.warehouse_to_img(pos[0], pos[1])
        pickupPath = finder.find(start, pickup)
        dropPath = finder.find(pickup, drop)
        # _, img = cv2.imencode(".jpg", finder.visualizePath())
        # img_bytes = img.tobytes()
        # self.socketio.emit('path', base64.b64encode(img_bytes))
        tracker = PathTracker(
            pickupPath, dropPath, 2.8, 5, robot)
        tracker.track()
        exit(0)


    def finishAll(self):
        self.queue.put(None)
        self.loop.join()
        self.pool.close()
        self.pool.join()
