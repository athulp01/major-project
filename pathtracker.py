import math


class PathTracker:
    def __init__(self, path):
        self.path = path

    def curvature(self, point, prev, after):
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

    def distance(self, point1, point2):
        return math.sqrt(pow(point1[0]-point2[1], 2) + pow(point1[2] - point2[1], 2))
