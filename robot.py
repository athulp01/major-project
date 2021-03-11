import sim
import math


class Robot:
    def __init__(self, client, num):
        self.client = client 
        err, self.blmotor = sim.simxGetObjectHandle(
            self.client, "joint_back_left_wheel#"+num, sim.simx_opmode_blocking)
        err, self.brmotor = sim.simxGetObjectHandle(
            self.client, "joint_back_right_wheel#"+num, sim.simx_opmode_blocking)
        err, self.flmotor = sim.simxGetObjectHandle(
            self.client, "joint_front_left_wheel#"+num, sim.simx_opmode_blocking)
        err, self.frmotor = sim.simxGetObjectHandle(
            self.client, "joint_front_right_wheel#"+num, sim.simx_opmode_blocking)
        err, self.base = sim.simxGetObjectHandle(
            self.client, "body#"+num, sim.simx_opmode_blocking)
        err, self.front = sim.simxGetObjectHandle(
            self.client, "front#"+num, sim.simx_opmode_blocking)

    def setVelocity(self, handle, velocity):  # Angular velocity(deg/s)
        err = sim.simxSetJointTargetVelocity(
            self.client, handle, velocity, sim.simx_opmode_oneshot)

    def getPos(self):
        err, pos  = sim.simxGetObjectPosition(
            self.client, self.base, -1, sim.simx_opmode_blocking)
        assert err == 0
        return pos

    def setLeftVelocity(self, velocity):
        self.setVelocity(self.blmotor, velocity)
        self.setVelocity(self.flmotor, velocity)

    def setRightVelocity(self, velocity):
        self.setVelocity(self.frmotor, velocity)
        self.setVelocity(self.brmotor, velocity)

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


    def steer(self, lfactor, rfactor, speed):
        self.setVelocity(self.blmotor, lfactor*speed)
        self.setVelocity(self.brmotor, rfactor * -speed)
        self.setVelocity(self.flmotor, lfactor*speed)
        self.setVelocity(self.frmotor, rfactor * -speed)
    
    def getAngle(self):
        err, res = sim.simxGetObjectOrientation(
            self.client, self.base, -1, sim.simx_opmode_blocking)
        return res[2]

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
