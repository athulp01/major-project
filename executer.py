from concurrent.futures import ThreadPoolExecutor
import queue
import threading
import json

from flask.json import jsonify
from werkzeug import debug
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
        self.pool = ThreadPoolExecutor(threads)
        self.queue = queue.Queue()
        self.warehouse = Warehouse(19999)
        self.robots = []
        self.tasks = []
        self.app = Flask("Warehouse")
        self.socketio = SocketIO(self.app, pingTimeout=60, pingInterval=60)
        self.socketio.on_event("addTask", self.handleAddTask)
        self.socketio.on_event("addRobot", self.handleAddRobot)
        self.loop = threading.Thread(target=self._dispatcher)
        self.freeRobots = threading.Semaphore(value=0)
        self.mutex = threading.Lock()
        self.app.add_url_rule(
            "/<path:path>", "sendFile", self.sendFile, methods=["GET"]
        )
        self.app.add_url_rule(
            "/", "sendHomePage", self.sendHomePage, methods=["GET"]
        )
        self.app.add_url_rule("/getTasks", "sendTasksHTTP", self.sendTasksHTTP)
        self.app.add_url_rule("/getRobotsPos", "sendRobotsPos", self.sendRobotsPos)

    def handle_message(self, data):
        print("received message: " + data)

    def handleGetTask(self):
        self.socketio.emit("get")

    def sendFile(self, path):
        return flask.send_from_directory("./", path)

    def sendHomePage(self):
        return flask.send_file("./html/index.html")

    def sendRobotsPos(self):
        pos = []
        for robot in self.robots:
            curPos = robot.getPos()
            mappedPos = self.warehouse.warehouse_to_img(curPos[0], curPos[1])
            pos.append({"id": robot.id, "x": mappedPos[0], "y": mappedPos[1]})
        return jsonify(pos)

    def sendTasksHTTP(self):
        return jsonify(self.tasks)

    def startHTTPServer(self):
        self.socketio.run(self.app, host="0.0.0.0")

    def stopHTTP(self):
        self.finishAll()
        status_code = flask.Response(status=201)
        return status_code

    def handleAddTask(self, data):
        data = json.loads(data)
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

    def _dispatcher(self):
        while True:
            print("waiting")
            points = self.queue.get()
            if points == None:
                break
            print("Preparing to dispatch", points)
            self.mutex.acquire()
            self.freeRobots.acquire()
            print("Dispatching", points)
            self.pool.submit(self._assignTask, points)

    def addRobot(self, name):
        self.robots.append(Robot(self.warehouse.client, name))
        self.freeRobots.release()

    def addTask(self, stop):
        self.queue.put(stop)

    def release(self, num):
        print("Releasing")
        self.robots[num].makeFree()
        self.freeRobots.release()

    def _assignTask(self, task):
        print(type(task))
        pickup, drop = (task["pickup"]["x"], task["pickup"]["y"]), (
            task["drop"]["x"],
            task["drop"]["y"],
        )
        print(pickup, drop)
        for i in range(len(self.robots)):
            if not self.robots[i].busy:
                self.robots[i].makeBusy(task)
                self.mutex.release()
                self.socketio.emit(
                    "assignTo", {"uuid": task["uuid"], "robot": self.robots[i].id}
                )
                task["status"] = "Computing Path"
                self.socketio.emit(
                    "updateStatus", {"uuid": task["uuid"], "status": "Computing Path"}
                )
                finder = PathFinder(self.warehouse)
                _, pos = sim.simxGetObjectPosition(
                    self.warehouse.client,
                    self.robots[i].base,
                    -1,
                    sim.simx_opmode_blocking,
                )
                start = self.warehouse.warehouse_to_img(pos[0], pos[1])
                pickupPathImg, pickupPath = finder.find(start, pickup)
                if len(pickupPath) == 0:
                    task["status"] = "No route"
                    self.socketio.emit(
                        "updateStatus", {"uuid": task["uuid"], "status": task["status"]}
                    )
                    self.release(i)
                    return
                dropPathImg, dropPath = finder.find(pickup, drop)
                if len(dropPath) == 0:
                    task["status"] = "No route"
                    self.socketio.emit(
                        "updateStatus", {"uuid": task["uuid"], "status": task["status"]}
                    )
                    self.release(i)
                    return
                self.socketio.emit(
                    "path",
                    {
                        "uuid": task["uuid"],
                        "pickup": pickupPathImg,
                        "drop": dropPathImg,
                    },
                )
                task["status"] = "In Transit"
                self.socketio.emit(
                    "updateStatus", {"uuid": task["uuid"], "status": "In Transit"}
                )
                tracker = PathTracker(
                    pickupPath,
                    dropPath,
                    2.8,
                    5,
                    self.robots[i],
                    self.warehouse,
                    self.socketio,
                )
                tracker.track()
                curPos = self.robots[i].getPos()
                mappedPos = self.warehouse.warehouse_to_img(curPos[0], curPos[1])
                self.robots[i].task["status"] = "Finished"
                self.socketio.emit(
                    "updateStatus",
                    {"uuid": self.robots[i].task["uuid"], "status": "Finished"},
                )
                self.socketio.emit(
                    "updateRobotPos",
                    {"id": self.robots[i].id, "x": mappedPos[0], "y": mappedPos[1]},
                )
                self.release(i)
                return

    def finishAll(self):
        self.queue.put(None)
        self.loop.join()
        self.mutex.acquire()
        self.pool.shutdown()
