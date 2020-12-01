#%%
import cv2 as cv
from matplotlib import pyplot as plt
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class PathFinder:
    def __init__(self, simWidth, simHeight, simX, simY):
        self.simWidth = simWidth
        self.simHeight = simHeight
        self.simX = simX
        self.simY = simY

    def find(self, img):
        preproc = self.preprocess(img)
        #7.34 and 9.04 are actual dimension in the sim env
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
        # convert tuple to list
        path = path[0::4]
        self.path = [[p[0],p[1]] for p in path]
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
                    newpath[i][j] += amount*(self.path[i][j] - newpath[i][j]) + smoothness*(newpath[i-1][j] + newpath[i+1][j] - (2.0*newpath[i][j]))
                    change += abs(aux - newpath[i][j])
            print(change)
        self.path = newpath
        return newpath


    def preprocess(self, img):
        # flip the image to match the simulator
        img = cv.flip(img,1)
        # crop to the boundary
        img = img[ 17:495,50:475]
        # cv.imwrite("initial.png", img)
        self.img = img
        self.height = (len(img))
        self.width = (len(img[0]))
        edges = cv.Canny(img, 10 ,50)
        edges = (255-edges)
        # cv.imwrite("edges.png", edges)
        self.img = img
        increased = self.incBoundWidth(edges, 35)
        # cv.imwrite("increased.png", increased)
        return increased


    def createMapping(self, xStep, yStep):
        self.mapping = dict()
        for i in range(self.width):
            for j in range(self.height):
                # 3.67 and -4.72 
                self.mapping[(i,j)] = (3.67 - i*xStep, -4.72 + j*yStep)
            
    def incBoundWidth(self, edges, incWidth):
        # Increase horizontally
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
        #increace veritaclly
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

#%%
img = cv.imread("./test.png", cv.IMREAD_GRAYSCALE)
finder = PathFinder(0,0,0,0)
finder.find(img)
#%%
finder.smooth(10, 0.4, 50)

# %%
finder.visualizePath()

# %%
