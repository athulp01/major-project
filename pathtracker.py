import math
import matplotlib.pyplot as plt
import numpy as np
import pathfinder
import sim


class PathTracker:
    def __init__(
        self, pickupPath, dropPath, lookdist, width, robot, warehouse, socketio, pkg
    ):
        self.lookdist = lookdist
        self.pkg = pkg
        self.warehouse = warehouse
        self.socketio = socketio
        self.pickupPath = pickupPath
        self.dropPath = dropPath
        # self.pos = [0,0]
        self.width = width
        self.robot = robot
        self.velocity = 4
        self.reset()

    def reset(self):
        self.prevLookindex = -0.5
        self.angle = self.robot.getAngle()
        self.pos = self.robot.getPos()[0:2]
        self.pos[0] += 1
        self.prevLookahead = self.pos

    def track(self):
        print("start tracking")
        while True:
            if (self.pos[0] - self.pickupPath[-1][0]) ** 2 + (
                self.pos[1] - self.pickupPath[-1][1]
            ) ** 2 < 2:
                self.robot.setLeftVelocity(0)
                self.robot.setRightVelocity(0)
                break
            lookpoint = self.lookhead(self.pos, self.pickupPath)
            curv = self.curvature(lookpoint)
            wheels = self.turn(curv, self.width)
            self.robot.setLeftVelocity(wheels[0])
            self.robot.setRightVelocity(-wheels[1])
            self.pos = self.robot.getPos()[0:2]
            self.angle = self.robot.getAngle()
            self.socketio.sleep(0)

        self.reset()
        print("start picking")
        print(self.robot)
        err, platform = sim.simxGetObjectHandle(
            self.warehouse.client,
            "platform_" + self.robot.id,
            sim.simx_opmode_blocking,
        )
        err, pos = sim.simxGetObjectPosition(
            self.warehouse.client, platform, -1, sim.simx_opmode_blocking
        )
        pos[2] = pos[2] + 0.1
        self.warehouse.movePackage(self.pkg, pos, platform)
        self.warehouse.movePackage(self.pkg, pos, platform)
        self.warehouse.movePackage(self.pkg, pos, platform)

        while True:
            if (self.pos[0] - self.dropPath[-1][0]) ** 2 + (
                self.pos[1] - self.dropPath[-1][1]
            ) ** 2 < 2:
                self.robot.setLeftVelocity(0)
                self.robot.setRightVelocity(0)
                break
            lookpoint = self.lookhead(self.pos, self.dropPath)
            curv = self.curvature(lookpoint)
            wheels = self.turn(curv, self.width)
            self.robot.setLeftVelocity(wheels[0])
            self.robot.setRightVelocity(-wheels[1])
            self.pos = self.robot.getPos()[0:2]
            self.angle = self.robot.getAngle()
            self.socketio.sleep(0)

        err, pos = sim.simxGetObjectPosition(
            self.warehouse.client, platform, -1, sim.simx_opmode_blocking
        )
        pos[2] = 0.1
        pos[0] = pos[0] - 0.3
        pos[1] = pos[1] - 0.3
        self.warehouse.movePackage(self.pkg, pos, -1)
        self.warehouse.movePackage(self.pkg, pos, -1)

    def turn(self, curv, trackwidth):
        return [
            self.velocity * (2 + curv * trackwidth) / 2,
            self.velocity * (2 - curv * trackwidth) / 2,
        ]

    def curve(self, point, prev, after):
        x1, y1 = point[0], point[1]
        x1 += 0.00001  # divide by zero error
        x2, y2 = after[0], after[1]
        x3, y3 = prev[0], prev[1]
        k1 = 0.5 * (pow(x1, 2) + pow(y1, 2) - pow(x2, 2), pow(y2, 2)) / (x1 - x2)
        k2 = (y1 - y2) / (x1 - x2)
        b = (
            0.5
            * (
                pow(x2, 2)
                - 2 * x2 * k1
                + pow(y2, 2)
                - pow(x3, 2)
                + 2 * x3 * k1
                - pow(y3, 2)
            )
            / (x3 * k2 - y3 + y2 - x2 * k2)
        )
        a = k1 - k2 * b
        r = math.sqrt(pow(x1 - a, 2) + pow(y1 - b, 2))
        return 1 / r

    def curvature(self, lookapoint):
        side = np.sign(
            math.sin(self.angle) * (lookapoint[0] - self.pos[0])
            - math.cos(self.angle) * (lookapoint[1] - self.pos[1])
        )
        a = -math.tan(self.angle + 0.0000001)
        c = math.tan(self.angle + 0.0000001) * self.pos[0] - self.pos[1]
        x = abs(a * lookapoint[0] + lookapoint[1] + c) / math.sqrt(a ** 2 + 1)
        return side * (2 * x / (self.lookdist ** 2))

    def lookhead(self, robot_pos, path):
        for i in range(math.ceil(self.prevLookindex), len(path) - 1):
            line_start = path[i]
            line_end = path[i + 1]
            d = np.subtract(line_end, line_start)
            f = np.subtract(line_start, robot_pos)

            a = np.dot(d, d)
            b = np.dot(2 * f, d)
            c = np.dot(f, f) - (self.lookdist * self.lookdist)

            discriminant = b * b - (4 * a * c)

            if discriminant >= 0:
                discriminant = math.sqrt(discriminant)
                t1 = (-b - discriminant) / (2 * a)
                t2 = (-b + discriminant) / (2 * a)
                if 0 <= t1 <= 1:
                    self.prevLookindex = i + t1
                    self.prevLookahead = line_start + t1 * d
                    return self.prevLookahead
                if 0 <= t2 <= 1:
                    self.prevLookindex = i + t2
                    self.prevLookahead = line_start + t2 * d
                    return self.prevLookahead
        return self.prevLookahead
