# This file includes all driving related things

import ev3dev.ev3 as ev3
import time
import math

import sensor
import odometry
import explorer


DEBUGPRINTS = False  # Allows to easily switch debug prints in the console on or off

# Setting constants, needed in turnToPath
PI2 = math.pi / 2
PI4 = math.pi / 4


class Driving:

    shutdown = False

    # Defining initial behaviour, setting everything up
    def __init__(self, communication):

        self.lm = ev3.LargeMotor("outA")  # lm = left motor
        self.rm = ev3.LargeMotor("outD")  # rm = right motor
        self.resetMotors()
        self.shutdown = False  # Boolean False if driving
        self.obstacleFound = False  # Boolean False if no obstacle has been detected
        self.prevtickl = 0
        self.prevtickr = 0

        # Initialization for various needed classes
        self.sensor = sensor.Sensor()
        self.sound = ev3.Sound()
        self.explorer = explorer.Explorer(communication)
        self.odo = odometry.Odometry()

        # List for the scanned directions on a node
        self.scannedDirections = []

        # Calibrate the sensor or use standard values if calibration is disabled
        self.rBlue, self.gBlue, self.bBlue = (49, 180, 93)
        self.rRed, self.gRed, self.bRed = (159, 61, 13)
        self.initialOffset = 220

        # Can be disabled for debugging, fallback to the values above
        self.calibrateSensor()

    # Allows to wait until a button is pressed (to confirm an action)
    def buttonPressed(self):
        btn = ev3.Button()

        while not btn.any():
            pass

    # Calibrating procedure for blue, red, black and white
    def calibrateSensor(self):

        print(">> Press any button to scan blue for calibration.")
        self.buttonPressed()

        self.rBlue = 0
        self.gBlue = 0
        self.bBlue = 0

        for i in range(10):
            rBLUE, gBLUE, bBLUE = self.sensor.getColor()
            self.rBlue += rBLUE
            self.gBlue += gBLUE
            self.bBlue += bBLUE

        self.rBlue = int(self.rBlue / 10)
        self.gBlue = int(self.gBlue / 10)
        self.bBlue = int(self.bBlue / 10)

        print("Calibrated colour values for blue:", self.rBlue, self.gBlue, self.bBlue)
        print(">> Press any button to scan red for calibration.")
        self.buttonPressed()

        self.rRed = 0
        self.gRed = 0
        self.bRed = 0

        for i in range(10):

            rRED, gRED, bRED = self.sensor.getColor()
            self.rRed += rRED
            self.gRed += gRED
            self.bRed += bRED

        self.rRed = int(self.rRed / 10)
        self.gRed = int(self.gRed / 10)
        self.bRed = int(self.bRed / 10)

        print("Calibrated colour values for red:", self.rRed, self.gRed, self.bRed)
        print(">> Press any button to scan black for calibration.")
        self.buttonPressed()

        self.brightnessBlack = 0
        for i in range(10):

            brightnessBlack1 = self.sensor.getBrightness()
            self.brightnessBlack += brightnessBlack1

        self.brightnessBlack /= 10

        print("Calibrated colour values black:", self.brightnessBlack)
        print(">> Press any button to scan white for calibration.")
        self.buttonPressed()

        self.brightnessWhite = 0
        for i in range(10):

            brightnessWhite1 = self.sensor.getBrightness()
            self.brightnessWhite += brightnessWhite1

        self.brightnessWhite /= 10

        print("Calibrated colour values white:", self.brightnessWhite)

        # Calculates the offset from black and white
        self.initialOffset = (self.brightnessWhite + self.brightnessBlack) / 2
        print("Calculated offset = ", self.initialOffset)
        input("Press 🦆r to start the robot!")

    # PID algorithm
    def lineFollower(self):

        if DEBUGPRINTS: print("LineFollower")

        # Initialize the variables needed:
        kp = 0.3  # 0.1, for the p
        kd = 0.1  # 0.05, how much it turns away from the line, multiplier for the derivative
        ki = 0.15  # 0.03, factor for multiplying with the integral
        speed = 150  # 150, target speed
        integral = 0
        olderror = 0

        self.shutdown = False

        while not self.shutdown:

            # Brightness-values: black = (38, 77, 15) -> 62, white = (285, 503, 200) -> 424
            r, g, b = self.sensor.getColor()
            brightness = self.sensor.getBrightness()

            # Changes target speed and offset depending on the brightness
            if 100 < brightness < 370:
                self.offset = 230  # 230
                speed = 150  # 150

            elif brightness < 100:
                self.offset = 160  # 160
                speed = 125  # 150

            elif brightness > 370:
                # needs to be negative to have an appropriate turn value
                self.offset = 300  # 300
                speed = 125  # 150

            # Calculates variables and then the turn value
            error = brightness - self.offset
            integral = integral * 5/6 + error
            deri = error - olderror
            turn = (kp * error + ki * integral + kd * deri)

            # Saves the error as olderror for the next iteration
            olderror = error

            # Calculates the new speed from target speed and turn, multiplied by the correction factor for the battery
            self.powerl = speed + turn  # * self.batteryCorrection
            self.powerr = speed - turn  # * self.batteryCorrection

            # Sets the calculated power as the new speed (negotiates them, because our motors are mounted backwards)
            self.run(-self.powerl, -self.powerr)

            # Checks for obstacles
            if self.sensor.obstacleTest() < 10:

                self.stopMotors()
                self.shutdown = True

                # Warn everyone else
                self.sound.play('/home/robot/src/sounds/uhoh.wav').wait()

                # Backs the robot up a little
                self.run(100, 100)
                time.sleep(1)
                self.stopMotors()

                if DEBUGPRINTS: print("Ouch! Obstacle detected!")

                # Boolean we later send to explorer, setting this path to blocked
                self.obstacleFound = True

                # Turn around and go back to the previous node
                self.turnToPath(self.odo.gamma - PI2)
                self.lineFollower()

            # Sets the values for blue and red nodes
            isBlue = lambda r, g, b: r in range(self.rBlue - 30, self.rBlue + 30) and g in range(self.gBlue - 30, self.gBlue + 30) and b in range(self.bBlue - 30, self.bBlue + 30)
            isRed = lambda r, g, b: r in range(self.rRed - 30, self.rRed + 30) and g in range(self.gRed - 30, self.gRed + 30) and b in range(self.bRed - 30, self.bRed + 30)

            # Checks if a red or blue node is detected and performs an action
            if isRed(r, g, b) or isBlue(r, g, b):

                self.stopMotors()
                self.shutdown = True

                # Collects information for the explorer and explores the node, if node unknown
                if DEBUGPRINTS: print("Our x, y and gamma are = ", self.odo.x, self.odo.y, self.odo.gamma)

                node = (self.odo.getCoordinates(self.odo.x), self.odo.getCoordinates(self.odo.y))
                direction = self.odo.getOrientation(self.odo.gamma)
                correctedOdoData = self.explorer.onNodeReached(node, direction, self.obstacleFound)

                if correctedOdoData is None:
                    print("We're finished. Hooray! (In case we're not, just pretend we are.)")
                    self.sound.play('/home/robot/src/sounds/mission-passed.wav').wait()
                    return

                (self.newX, self.newY), self.oldDir = correctedOdoData
                
                # Writes the values in odometry to the new, correct ones
                self.odo.getFromDriving(self.newX, self.newY, self.oldDir)
                if DEBUGPRINTS: print("CORRECTED x, y and gamma are = ", self.odo.x, self.odo.y, self.odo.gamma)

                if not self.explorer.wasScanned():

                    self.scanNode()

                    # Send x and y coordinates, the orientation, the obstacle boolean and the list of new
                    # directions if node is new to the explorer
                    self.newDir = self.explorer.getNextDirection(self.scannedDirections)

                else:
                    # If node has been scanned before
                    self.newDir = self.explorer.getNextDirection(None)
                    self.run(-100, -100)

                    time.sleep(1)
                    self.stopMotors()

                if self.newDir is None:
                    print("We're finished. Hooray! (In case we're not, just pretend we are.)")
                    self.sound.play('/home/robot/src/sounds/mission-passed.wav').wait()
                    return

                # Beep at end of communication phase:
                self.sound.play('/home/robot/src/sounds/blip4.wav').wait()

                # Resets the motors (and therefore x and y in the odometry) and then turns to the new path
                self.resetMotors()
                self.obstacleFound = False
                self.turnToPath(self.odo.getGammaFromOrientation(self.newDir))

                # Check if obstacle is right in front of the robot, if so turn around and report "path blocked"
                if self.sensor.obstacleTest() < 20:

                    # Warn everyone else
                    self.sound.play('/home/robot/src/sounds/uhoh.wav').wait()

                    self.turnToPath(self.odo.gamma - 180)

                self.resetMotors()
                self.lineFollower()

    #  Easy access to the odometry
    def odoInfo(self):

        # Gets the current wheel position
        tickl, tickr = self.getWheelPosition()

        # Calculates how much the wheel position has changed
        self.odo.calcPosition(tickl - self.prevtickl, tickr - self.prevtickr)

        # Saves the old ticks for the next round
        self.prevtickl = tickl
        self.prevtickr = tickr

    # Return the current wheel position
    def getWheelPosition(self):

        return self.lm.position, self.rm.position

    # Resets the motors (and therefore odometry), sets obstacleFound to False
    def resetMotors(self):

        self.lm.reset()
        self.rm.reset()

        self.prevtickl = 0
        self.prevtickr = 0

    # Stops the motors according to the defined braking-behaviour
    def stopMotors(self):

        # Defining the robots brake behaviour
        self.lm.stop_action = "brake"
        self.rm.stop_action = "brake"

        # Stops the motors
        self.lm.stop()
        self.rm.stop()

    # Allows easy access to the motors
    def run(self, lmSpeed, rmSpeed):

        self.odoInfo()
        self.lm.speed_sp = lmSpeed
        self.rm.speed_sp = rmSpeed
        self.lm.command = "run-forever"
        self.rm.command = "run-forever"

    # Helper function to round the gamma-angle and return the 
    # number of multiples of pi / 2 in the rounded angle
    def turnsRequired(self, x):

        if x % PI2 > PI4:
            res = (1 + x // PI2)
        else:
            res = (x // PI2)

        # This is like taking the angle mod 2pi
        return res % 4

    # Turns the robot to the new direction it should continue driving
    def turnToPath(self, gammaTarget):

        gammaPrev = self.odo.gamma
        turnsRequired = self.turnsRequired(gammaTarget - self.odo.gamma)
        turnMade = 0

        # The robot attempts to aling itself with the path in case
        # it is to go straight forward
        if turnsRequired == 0:

            while turnMade < PI4 and self.sensor.getBrightness() > 100:
                self.run(-100, 100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

            turnMade = 0
            self.stopMotors()

            while turnMade < PI2 and self.sensor.getBrightness() > 100:
                self.run(100, -100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

            turnMade = 0
            self.stopMotors()

            # If no line can be found in front of the robot, 
            # return to the original orientation
            while turnMade < PI4 and self.sensor.getBrightness() > 100:
                self.run(-100, 100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

        elif turnsRequired == 1 or turnsRequired == -3:
            while turnMade < PI4 or self.sensor.getBrightness() > 100:
                self.run(-100, 100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

        elif turnsRequired == -1 or turnsRequired == 3:
            while turnMade < PI4 or self.sensor.getBrightness() > 100:
                self.run(100, -100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

        elif turnsRequired == 2 or turnsRequired == -2:
            while turnMade < 3 * PI4 or self.sensor.getBrightness() > 100:
                self.run(-100, 100)
                turnMade += abs(gammaPrev - self.odo.gamma)
                gammaPrev = self.odo.gamma

    # Scans the current node for other paths, add their cardinal direction to a list
    def scanNode(self):

        # Empty List, that way we don't have any old data in it
        self.scannedDirections = []

        # Move to the center of the node
        self.run(-100, -100)
        time.sleep(1.2)
        self.stopMotors()

        # Creates a local variable, used to determine how far the robot should turn
        gammaInitial = self.odo.gamma  

        # Scans for path to the left
        self.shutdown = False
        while not self.shutdown:

            self.run(200, -200)

            if self.sensor.getBrightness() < 100 and self.odo.gamma < gammaInitial - 0.78:

                self.stopMotors()
                self.shutdown = True
                direction = self.odo.getOrientation(self.odo.gamma)
                self.scannedDirections.append(direction)

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("Hooray, I found a new path in this direction: ", direction)

            elif self.odo.gamma < gammaInitial - 2.35:

                self.stopMotors()
                self.shutdown = True

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("No path found to the left. :/")

        # Scans for path right in front of the robot
        self.shutdown = False
        while not self.shutdown:

            self.run(-200, 200)

            if self.sensor.getBrightness() < 100 and self.odo.gamma > gammaInitial - 0.78:

                self.stopMotors()
                self.shutdown = True
                direction = self.odo.getOrientation(self.odo.gamma)
                self.scannedDirections.append(direction)

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("Hooray, I found a new path in this direction: ", direction)

            elif self.odo.gamma > gammaInitial + 0.78:

                self.stopMotors()
                self.shutdown = True

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("No path found to the front. :/")

        # Scans for path to the right
        self.shutdown = False
        while not self.shutdown:

            self.run(-200, 200)

            if self.sensor.getBrightness() < 100 and self.odo.gamma > gammaInitial + 0.78:

                self.stopMotors()
                self.shutdown = True
                direction = self.odo.getOrientation(self.odo.gamma)
                self.scannedDirections.append(direction)

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("Hooray, I found a path in this direction: ", direction)

            elif self.odo.gamma > gammaInitial + 2.35:

                self.stopMotors()
                self.shutdown = True

                if DEBUGPRINTS: print("Gamma = ", self.odo.gamma)
                if DEBUGPRINTS: print("No path found to the right. :/")

        # Turns back to the middle (initial viewing direction)
        self.shutdown = False
        while not self.shutdown:

            self.run(100, -100)

            if self.odo.gamma < gammaInitial:

                self.stopMotors()
                self.shutdown = True

                print(self.explorer.currentNode, "Possible new directions are: ", self.scannedDirections)
