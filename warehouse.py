import sim
import cv2 as cv
import numpy as np


class Warehouse:
    def __init__(self, port):
        sim.simxFinish(-1)
        self.port = port
        self.client = sim.simxStart("127.0.0.1", port, True, True, 5000, 5)

        _, topleft = sim.simxGetObjectHandle(
            self.client, "topleft", sim.simx_opmode_blocking
        )
        _, bottomright = sim.simxGetObjectHandle(
            self.client, "bottomright", sim.simx_opmode_blocking
        )

        _, self.toplpos = sim.simxGetObjectPosition(
            self.client, topleft, -1, sim.simx_opmode_blocking
        )
        _, self.bottomrpos = sim.simxGetObjectPosition(
            self.client, bottomright, -1, sim.simx_opmode_blocking
        )

        err, self.camera = sim.simxGetObjectHandle(
            self.client, "ceil_camera", sim.simx_opmode_blocking
        )
        self.width = abs(self.toplpos[0] - self.bottomrpos[0])
        self.height = abs(self.bottomrpos[1] - self.toplpos[1])
        self.imwidth = None
        self.imheight = None

    def getImage(self):
        err, resol, image = sim.simxGetVisionSensorImage(
            self.client, self.camera, 0, sim.simx_opmode_blocking
        )
        img = np.array(image, dtype=np.uint8)
        img.resize([resol[1], resol[0], 3])
        img = cv.flip(img, 1)
        # crop to the boundary
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        _, thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)
        contours, hierarchy = cv.findContours(
            thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )
        cnt = contours[0]
        x, y, w, h = cv.boundingRect(cnt)
        img = img[y : y + h, x : x + w]
        self.imheight = len(img)
        self.imwidth = len(img[0])
        return img

    def warehouse_to_img(self, x, y):
        if not self.imwidth:
            self.getImage()
        imgx = (-self.toplpos[0] + x) / (self.width / self.imwidth)
        imgy = (self.toplpos[1] - y) / (self.height / self.imheight)
        assert imgx < self.imwidth
        assert imgy < self.imheight
        return (int(imgx), int(imgy))

    def img_to_warehouse(self, x, y):
        if not self.imwidth:
            self.getImage()
        warex = self.toplpos[0] + x * (self.width / self.imwidth)
        warey = self.toplpos[1] - y * (self.height / self.imheight)
        return (warex, warey)
