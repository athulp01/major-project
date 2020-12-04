import math
from robot import Robot
import numpy as np
from numpy.core.numeric import NaN


class PathTracker:
    def __init__(self, path, lookdist, width, robot):
        self.lookdist = lookdist
        self.path = path
        self.prevLookahead = None
        self.prevLookindex = -0.5
        self.angle = robot.getAngle()
        self.pos = robot.getPos()[0:2]
        self.pos[0] += 1
        # self.pos = [0,0]
        self.width = width
        self.dt = 0.005
        self.robot = robot

    def track(self):
        while True:
            lookpoint = self.lookhead(self.pos)
            curv = self.curvature(lookpoint)
            wheels = self.turn(curv, 3, self.width)
            print(wheels)
            self.robot.setLeftVelocity(wheels[0])
            self.robot.setRightVelocity(-wheels[1])
            # while(lookpoint[0] > pos[0] and lookpoint[1] > pos[1]):
            #     pos = self.robot.getPos()
            # self.robot.setLeftVelocity(0)
            # self.robot.setRightVelocity(0)
            self.pos = self.robot.getPos()[0:2]
            self.angle = self.robot.getAngle()
            [a_i - b_i for a_i, b_i in zip(self.pos,list(self.path[-1]))]
            # if (np.linalg.norm([a_i - b_i for a_i, b_i in zip(self.pos,list(self.path[-1]))]) < 2):
            #     break
    
    def turn(self,curv, vel, trackwidth):
        return  [vel*(2+curv*trackwidth)/2, vel*(2-curv*trackwidth)/2]

    def curve(self, point, prev, after):
        x1, y1 = point[0], point[1]
        x1 += 0.00001  # divide by zero error
        x2, y2 = after[0], after[1]
        x3, y3 = prev[0], prev[1]
        k1 = 0.5*(pow(x1, 2) + pow(y1, 2) - pow(x2, 2), pow(y2, 2))/(x1-x2)
        k2 = (y1 - y2)/(x1 - x2)
        b = 0.5*(pow(x2, 2) - 2*x2*k1 + pow(y2, 2)-pow(x3, 2) +
                 2*x3*k1 - pow(y3, 2))/(x3*k2-y3+y2-x2*k2)
        a = k1 - k2*b
        r = math.sqrt(pow(x1-a, 2) + pow(y1-b, 2))
        return 1/r

    def curvature(self, lookapoint):
        side = np.sign(math.sin(self.angle)*(lookapoint[0]-self.pos[0]) - math.cos(
            self.angle)*(lookapoint[1]-self.pos[1]))
        a = -math.tan(self.angle)
        c = math.tan(self.angle)*self.pos[0] - self.pos[1]
        x = abs(a*lookapoint[0] + lookapoint[1] + c) / math.sqrt(a**2 + 1)
        return side * (2*x/(self.lookdist**2))

    def distance(self, point1, point2):
        return np.linalg.norm(point1 - point2)

    def lookhead(self, robot_pos):
        for i in range(math.ceil(self.prevLookindex), len(self.path)-1):
            line_start = self.path[i]
            line_end = self.path[i+1]
            d = np.subtract(line_end, line_start)
            f = np.subtract(line_start, robot_pos)

            a = np.dot(d, d)
            b = np.dot(2*f, d)
            c = np.dot(f, f)-(self.lookdist*self.lookdist)

            discriminant = b*b-(4*a*c)

            if discriminant >= 0:
                discriminant = math.sqrt(discriminant)
                t1 = (-b - discriminant)/(2 * a)
                t2 = (-b + discriminant)/(2 * a)
                if 0 <= t1 <= 1:
                    self.prevLookindex = i + t1
                    self.prevLookahead = line_start + t1*d
                    return self.prevLookahead
                if 0 <= t2 <= 1:
                    self.prevLookindex = i + t2
                    self.prevLookahead = line_start + t2*d
                    return self.prevLookahead
        return self.prevLookahead

# tracker = PathTracker([[0,0], [1,1]], 1, 0.001, None)
# print(tracker.lookhead([0,0]))
# print(tracker.curvature([0.707, 0.707]))