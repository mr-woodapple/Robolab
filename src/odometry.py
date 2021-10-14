# !/usr/bin/env python3
# import ev3dev.ev3 as ev3
import math
import driving
import time
from planet import Direction


class Odometry:

    def __init__(self):

        # Gamma is the direction the robot is looking at (orientation).
        # The initial value come from the mothership (explorer), set here with the getFromDriving function
        self.DISTANCE_PER_TICK = 0.0523  # cm (measure by hand)
        self.WHEEL_GAUGE = 14 # 15cm distance between the middle of both wheels

        self.gamma = 0
        self.alpha = 0
        self.beta = 0
        self.x = 0
        self.y = 0
        self.oldtravelcountr = 0
        self.oldtravelcountl = 0

    # Writes the corrected x and y values to our odometry
    def getFromDriving(self, x, y, orientation):

        self.x = x * 50
        self.y = y * 50
        self.gamma = self.getGammaFromOrientation(orientation)

    # Calculates the driven distance -> CORRECT NOW??
    def getWheelDistance(self, ticksr, ticksl):

        r = 2.8  # wheel radius from the roboter
        self.distancel = -ticksl * self.DISTANCE_PER_TICK
        self.distancer = -ticksr * self.DISTANCE_PER_TICK

    # Calculates the alpha-angle
    def getAlpha(self):

        self.alpha = (self.distancer - self.distancel) / self.WHEEL_GAUGE

    # Calculates beta
    def getBeta(self):

        self.beta = self.alpha / 2

    # Calculates the delta for both x and y
    def getDeltaX(self):

        self.deltaX = math.sin(self.gamma + self.beta) * self.drivenDistance  # no -math.sin required

    def getDeltaY(self):

        self.deltaY = math.cos(self.gamma + self.beta) * self.drivenDistance

    # Calculates the new gamma (Orientation)
    def getGamma(self):

        # No need to save the old gamma, as gamma isn't updated before the new gamma is set, -= instead of +=
        self.gamma += self.alpha

    # Calculates distance s
    def getDrivenDistance(self):

        if self.alpha == 0:
            # distancer and distancel should be equal, doesn't matter which one you choose
            self.drivenDistance = self.distancer
            return

        self.drivenDistance = ((self.distancer + self.distancel) / self.alpha) * math.sin(self.beta)

    def calcPosition(self, *args):

        # Updates the values
        self.getWheelDistance(*args)
        self.getAlpha()
        self.getBeta()
        self.getDrivenDistance()
        self.getDeltaY()
        self.getDeltaX()
        self.getGamma()

        # Calculate the driven Distance
        self.x += self.deltaX
        self.y += self.deltaY
        return self.gamma, self.x, self.y

    # Translates the drivenDistance into coordinates (50cm = 1)
    def getCoordinates(self, x):

        if x % 50 >= 25:
            return int(x // 50 + 1)

        else:
            return int(x // 50)

    # Translates gamma into the cardinal direction
    def getOrientation(self, gamma):
        
        gammaR = (gamma + math.pi / 4) % (2 * math.pi)

        if 0 < gammaR <= math.pi / 2:
            return Direction.NORTH

        if math.pi / 2 < gammaR <= math.pi:
            return Direction.EAST

        if math.pi / 2 < gammaR <= 3 * math.pi / 2:
            return Direction. SOUTH

        if 3 * math.pi / 2 < gammaR <= 2 * math.pi:
            return Direction.WEST

    # Translates cardinal directions into the correct gamma values
    def getGammaFromOrientation(self, orientation):

        if orientation == Direction.NORTH:
            return 0.0

        elif orientation == Direction.EAST:
            return math.pi / 2

        elif orientation == Direction.SOUTH:
            return math.pi

        elif orientation == Direction.WEST:
            return 3 * math.pi / 2
