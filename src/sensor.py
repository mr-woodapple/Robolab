# Managing the data from the sensor

import ev3dev.ev3 as ev3
import math


class Sensor:
    def __init__(self):
        pass

    # Returns the color in raw rgb data
    def getColor(self):
        cs = ev3.ColorSensor()
        cs.mode = 'RGB-RAW'
        return cs.bin_data("hhh")

    def getBrightness(self):
        cs = ev3.ColorSensor()
        cs.mode = 'RGB-RAW'
        r, g, b = cs.bin_data("hhh")
        return math.sqrt(0.299*r**2 + 0.587*g**2 + 0.114*b**2)

    def obstacleTest(self):
        # Returns the distance in cm that the robot is away from an obstacle
        us = ev3.UltrasonicSensor()
        us.mode = 'US-DIST-CM'  # Continuous measurement in centimeters
        return us.distance_centimeters

