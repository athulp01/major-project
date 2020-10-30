import cv2 as cv
import sim
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class PathFinder:
    def __init__(self, simWidth, simHeight, simX, simY, img):
        self.simWidth = simWidth
        self.simHeight = simHeight
        self.simX = simX
        self.simY = simY

    def find(self, img):
        preproc = self.preprocess(img)
        self.createMapping(7.34/self.width, 9.04/self.height)
        grid = Grid(matrix=preproc)
        start = grid.node(287, 44)
        end = grid.node(52, 420)
        finder = AStarFinder()
        path, _ = finder.find_path(start, end, grid)
        actualPath = []
        for point in (path):
            x = self.mapping[(point[0], point[1])][0]
            y = self.mapping[(point[0], point[1])][1]
            actualPath.append((x,y,0.33))
        self.path = path
        return actualPath

    def imshow(self, img):
        cv.imshow("Image", img)
        cv.waitKey()

    def visualizePath(self):
        img = self.img
        for point in self.path:
            img[point[1],point[0]] = 100
        self.imshow(img)

    def preprocess(self, img):
        img = cv.flip(img,1)
        img = img[ 17:495,50:475]
        self.img = img
        self.height = (len(img))
        self.width = (len(img[0]))
        edges = cv.Canny(img, 10 ,50)
        edges = (255-edges)
        increased = self.incBoundWidth(edges, 35)
        return increased


    def createMapping(self, xStep, yStep):
        self.mapping = dict()
        for i in range(self.width):
            for j in range(self.height):
                self.mapping[(i,j)] = (3.67 - i*xStep, -4.72 + j*yStep)
            
    def incBoundWidth(self, edges, incWidth):
        for i in range(self.height):
            j = 0
            while j < self.width:
                if edges[i][j] == 0:
                    temp = j
                    count = 0
                    while temp >=0 and count < incWidth:
                        edges[i][temp] = 0
                        temp -= 1
                        count += 1
                    count = 0
                    while j < self.width and count < incWidth:
                        edges[i][j] = 0
                        j = j + 1
                        count = count + 1
                j = j + 1
        for i in range(self.width):
            j = 0
            while j < self.height:
                if edges[j][i] == 0:
                    temp = j
                    count = 0
                    while temp >=0 and count < incWidth:
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


img = cv.imread("./test.png", cv.IMREAD_GRAYSCALE)
finder = PathFinder(0,0,0,0,img)
finder.find(img)
finder.visualizePath()
