import cv2 as cv
from matplotlib import pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class PathFinder:
    def __init__(self, simWidth, simHeight, simX, simY):
        self.simWidth = abs(simWidth)
        self.simHeight = abs(simHeight)
        self.simX = simX
        self.simY = simY
        print(self.simWidth, self.simHeight, self.simX, self.simY)

    def find(self, img, start):
        preproc = self.preprocess(img)
        # 7.34 and 9.04 are actual dimension in the sim env
        self.createMapping(self.simWidth/self.width, self.simHeight/self.height)
        newx = (-self.simX + start[0])/(self.simWidth/self.width)
        newy = (self.simY - start[1])/(self.simHeight/self.height)
        print(start)
        print(self.width, self.height, newx, newy)
        grid = Grid(matrix=preproc)
        start = grid.node(int(newx), int(newy))
        end = grid.node(190, 150)
        finder = AStarFinder()
        path, _ = finder.find_path(start, end, grid)
        path = path[0::4]
        self.path = [[p[0], p[1]] for p in path]
        path = self.smooth(10, 0.4, 50)
        actualPath = []
        for point in (path):
            x = self.mapping[(int(point[0]), int(point[1]))][0]
            y = self.mapping[(int(point[0]), int(point[1]))][1]
            actualPath.append((x, y))
        return actualPath

    def imshow(self, image):
        plt.imshow(image)
        plt.show()

    def visualizePath(self):
        img = self.img
        for point in self.path:
            img[int(point[1]), int(point[0])] = 0
        # cv.imwrite("path.png", img)
        self.imshow(img)

    def smooth(self, amount, smoothness, tolerance):
        newpath = self.path.copy()
        change = tolerance
        while change >= tolerance:
            change = 0.0
            for i in range(1, len(self.path)-1):
                for j in range(2):
                    aux = newpath[i][j]
                    newpath[i][j] += amount*(self.path[i][j] - newpath[i][j]) + smoothness*(
                        newpath[i-1][j] + newpath[i+1][j] - (2.0*newpath[i][j]))
                    change += abs(aux - newpath[i][j])
        self.path = newpath
        return newpath

    def preprocess(self, img):
        # flip the image to match the simulator
        img = cv.flip(img, 1)
        self.imshow(img)
        # crop to the boundary
        gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        _,thresh = cv.threshold(gray,1,255,cv.THRESH_BINARY)
        contours,hierarchy = cv.findContours(thresh,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        x,y,w,h = cv.boundingRect(cnt)
        self.img = img[y:y+h,x:x+w]
        #img = img[17:495, 50:475]
        # cv.imwrite("initial.png", img)
        self.height = (len(self.img))
        self.width = (len(self.img[0]))
        edges = cv.Canny(self.img, 10, 50)
        edges = (255-edges)
        # cv.imwrite("edges.png", edges)
        increased = self.incBoundWidth(edges, 35)
        # cv.imwrite("increased.png", increased)
        return increased

    def createMapping(self, xStep, yStep):
        self.mapping = dict()
        for i in range(self.width):
            for j in range(self.height):
                self.mapping[(i, j)] = (self.simX + i*xStep, self.simY - j*yStep)
        print(self.mapping[(195,320)])

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
