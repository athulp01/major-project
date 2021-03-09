import cv2 as cv
from matplotlib import pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder


class PathFinder:
    def __init__(self, warehouse):
        self.warehouse = warehouse

    def find(self, start, end):
        print(start, end)
        self.img = self.warehouse.getImage()
        self.imshow(self.img)
        preproc = self.preprocess(self.img)
        self.imshow(preproc)
        # 7.34 and 9.04 are actual dimension in the sim env
        grid = Grid(matrix=preproc)
        cv.circle(self.img, start, 10, (255,0,0), 3)
        startGrid = grid.node(*start)
        cv.circle(self.img, end, 10, (0,255,0), 3)
        endGrid = grid.node(*end)
        finder = AStarFinder()
        path, _ = finder.find_path(startGrid, endGrid, grid)
        if len(path) == 0:
            self.imshow(self.img)
            raise IOError()
        path = path[0::4]
        self.path = [[p[0], p[1]] for p in path]
        self.path = self.smooth(30, 0.6, 40)
        actualPath = []
        for point in path:
            actualPath.append(self.warehouse.img_to_warehouse(*point))
        return actualPath

    def imshow(self, image):
        print("imshow disabled")
        ##plt.imshow(image)
        #plt.show()

    def visualizePath(self):
        img = self.img
        for point in self.path:
            img[int(point[1]), int(point[0])] = 0
        self.imshow(img)
        return img

    def smooth(self, amount, smoothness, tolerance):
        newpath = self.path.copy()
        change = tolerance
        while change >= tolerance:
            change = 0.0
            for i in range(1, len(self.path) - 1):
                for j in range(2):
                    aux = newpath[i][j]
                    newpath[i][j] += amount * (
                        self.path[i][j] - newpath[i][j]
                    ) + smoothness * (
                        newpath[i - 1][j] + newpath[i + 1][j] - (2.0 * newpath[i][j])
                    )
                    change += abs(aux - newpath[i][j])
        self.path = newpath
        return newpath

    def preprocess(self, img):
        self.height = len(img)
        self.width = len(img[0])
        edges = cv.Canny(img, 10, 50)
        edges = 255 - edges
        increased = self.incBoundWidth(edges, 35)
        return increased

    def incBoundWidth(self, edges, incWidth):
        # Increase horizontally
        for i in range(self.height):
            j = 0
            while j < self.width:
                if edges[i][j] == 0:
                    temp = j
                    count = 0
                    while temp >= 0 and count < incWidth:
                        edges[i][temp] = 0
                        temp -= 1
                        count += 1
                    count = 0
                    while j < self.width and count < incWidth:
                        edges[i][j] = 0
                        j = j + 1
                        count = count + 1
                j = j + 1
        # increace veritaclly
        for i in range(self.width):
            j = 0
            while j < self.height:
                if edges[j][i] == 0:
                    temp = j
                    count = 0
                    while temp >= 0 and count < incWidth:
                        edges[temp][i] = 0
                        temp -= 1
                        count += 1
                    count = 0
                    while j < self.height and count < incWidth:
                        edges[j][i] = 0
                        j = j + 1
                        count = count + 1
                j = j + 1
        return edges
