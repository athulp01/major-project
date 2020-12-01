import sim
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import math
from queue import Queue
from pathfinder import PathFinder


class Robot:
    def __init__(self, port):
        sim.simxFinish(-1)
        self.client = sim.simxStart("127.0.0.1", port, True, True, 5000, 5)
        err, self.blmotor = sim.simxGetObjectHandle(
            self.client, "joint_back_left_wheel", sim.simx_opmode_blocking)
        err, self.brmotor = sim.simxGetObjectHandle(
            self.client, "joint_back_right_wheel", sim.simx_opmode_blocking)
        err, self.flmotor = sim.simxGetObjectHandle(
            self.client, "joint_front_left_wheel", sim.simx_opmode_blocking)
        err, self.frmotor = sim.simxGetObjectHandle(
            self.client, "joint_front_right_wheel", sim.simx_opmode_blocking)
        err, self.camera = sim.simxGetObjectHandle(
            self.client, "ceil_camera", sim.simx_opmode_blocking)
        err, self.base = sim.simxGetObjectHandle(
            self.client, "body", sim.simx_opmode_blocking)
        self.plot = None

    def setVelocity(self, handle, velocity):  # Angular velocity(deg/s)
        err = sim.simxSetJointTargetVelocity(
            self.client, handle, velocity, sim.simx_opmode_blocking)

    def getPos(self):
        pos, err = sim.simxGetObjectPosition(self.client, self.base, -1, sim.simx_opmode_blocking)
        return pos

    def moveForward(self, velocity):
        self.setVelocity(self.flmotor, velocity)
        self.setVelocity(self.frmotor, -velocity)
        self.setVelocity(self.blmotor, velocity)
        self.setVelocity(self.brmotor, -velocity)

    def moveBackward(self, velocity):
        self.setVelocity(self.flmotor, -velocity)
        self.setVelocity(self.frmotor, velocity)
        self.setVelocity(self.blmotor, -velocity)
        self.setVelocity(self.brmotor, velocity)

    def stop(self):
        self.setVelocity(self.flmotor, 0)
        self.setVelocity(self.frmotor, 0)
        self.setVelocity(self.blmotor, 0)
        self.setVelocity(self.brmotor, 0)

    def getImage(self, i):
        err, resol, image = sim.simxGetVisionSensorImage(
            self.client, self.camera, 0, sim.simx_opmode_blocking)
        img = np.array(image, dtype=np.uint8)
        img.resize([resol[1], resol[0], 3])
        if self.plot is None:
            self.plot = plt.imshow(img)
        else:
            self.plot.set_data(img)
        return img

    def steer(self, lfactor, rfactor, speed):
        self.setVelocity(self.blmotor, lfactor*speed)
        self.setVelocity(self.brmotor, rfactor * -speed)
        self.setVelocity(self.flmotor, lfactor*speed)
        self.setVelocity(self.frmotor, rfactor * -speed)

    def rotate(self, angle):
        speed = 1
        def normalize(x): return (x+math.pi) % (2*math.pi)
        rfactor = 2 if angle > 0 else 1
        lfactor = 2 if angle < 0 else 1
        self.steer(lfactor, rfactor, speed)

        err, res = sim.simxGetObjectOrientation(
            self.client, self.base, -1, sim.simx_opmode_blocking)
        prev_ang = normalize(res[2])
        rot = 0.0
        while True:
            err, res = sim.simxGetObjectOrientation(
                self.client, self.base, -1, sim.simx_opmode_blocking)
            cur_ang = normalize(res[2])
            da = cur_ang - prev_ang
            # From 0 to 2pi
            if da > math.pi:
                da = (2*math.pi - cur_ang) + prev_ang
            # from 2pi to 0
            elif da < -math.pi:
                da = (cur_ang + (2*math.pi - prev_ang))
            rot += abs(da)
            prev_ang = cur_ang
            if(rot >= abs(angle)):
                self.stop()
                break


robot = Robot(19999)
pathfinder = PathFinder(0,0,0,0)
img = robot.getImage(2)
path = pathfinder.find(img)
q = Queue(maxsize=10000)
[q.put(i) for i in path]
while not q.empty():
    point = q.get()
pathfinder.visualizePath()
robot.moveForward(4)

while True:
    err, res = sim.simxGetObjectPosition(robot.client, robot.base, -1, sim.simx_opmode_blocking)
