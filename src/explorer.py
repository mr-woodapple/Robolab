#!/usr/bin/env python3

from typing import Tuple
from time import sleep
from planet import Planet, Direction


class Explorer:

    """
    Is used to figure out where to go next and adjusts the current route in case of 
    target messages and obstacles and the like.

    Explanation for directions:

    0,0-------------> (exit Direction)
     ^
     | (entrance Direction)
     |

    """


    def __init__(self, communication):

        self.planet = Planet()
        self.communication = communication

        # REMOVE BEFORE EXAM, for debugging only!!
        #self.communication.sendTestPlanet("Fassaden")

        self.currentNode = None
        self.target = None
        self.visitedNodes = set()

        self.poppedPath = None
        self.currentRoute = []
        self.DFSqueue = []


    # Methods to be called by the Driving class

    def onNodeReached(self, node: Tuple[int, int], entranceDirection: Direction, obstacleFound: bool):
        
        # Reset communication
        self.communication.targetMessage = None
        self.communication.correctedDirection = None
        self.communication.pathUnveiledMessages = [] 

        previousNode = self.currentNode
        self.currentNode = node
        self.entranceDirection = entranceDirection
        self.pathsForQueue = []
        self.__doPathMessage(previousNode, obstacleFound)

        if obstacleFound:
            self.planet.updateWeight(self.currentNode, self.exitDirection)
            self.__resetRoute()

        if self.currentNode == self.target:
            self.target = None
            self.communication.targetReached()
            return None

        return self.currentNode, self.entranceDirection


    def wasScanned(self):

        """
        Returns True if the currentNode has been scanned already, False otherwise
        This method is called in the driving class to figure out wether a node needs to be scanned
        """

        # If all outgoing paths are known already then there's no need to scan the node again
        try:
            if len(self.planet.paths[self.currentNode]) == 4:

                self.DFSqueue = [(self.currentNode, direction) for direction in
                                 [Direction.SOUTH, Direction.NORTH, Direction.EAST, Direction.WEST]
                                ] + self.DFSqueue
                return True

        except: pass

        return self.currentNode in self.visitedNodes

    
    def getNextDirection(self, scannedDirections):

        """
        scannedDirections should be None if the currentNode has already been scanned, 
        otherwise it is a list that contains the directions of discovered Paths
        """

        self.__testTargetChanged()
        self.__testPathUnveiled()
        self.visitedNodes.add(self.currentNode)

        nextDirection = self.__computeNextDirection(scannedDirections)
        if nextDirection is None:
            return None

        self.exitDirection = nextDirection
        self.__doPathSelectedMessage()

        try: self.DFSqueue.remove((self.currentNode, self.exitDirection))
        except: pass
        return self.exitDirection


    # Helper methods for subprocesses

    def __doPathMessage(self, previousNode, obstacleFound):
        
        # If we are on the starting node then there is no path message to send
        if previousNode is None:

            self.communication.sendReady()
            sleep(3)

            name, x, y, o = self.communication.getPlanetMessage()
            self.currentNode = (x, y)
            self.entranceDirection = Direction(o)
            self.communication.subscribePlanet()
            return


        rotate = lambda dir: (dir + 180) % 360

        if obstacleFound:
            self.communication.sendDiscoveredPath(
                *self.currentNode, self.exitDirection, *self.currentNode, rotate(self.entranceDirection), "blocked")

        else:
            self.communication.sendDiscoveredPath(
                *previousNode, self.exitDirection, *self.currentNode, rotate(self.entranceDirection), "free")


        sleep(3)
        pathMessage = self.communication.getPathMessage()
        Xc, Yc = pathMessage[3:5]
        weight = pathMessage[7]
        Dc = Direction(rotate(pathMessage[5]))

        if (Xc, Yc) != self.currentNode or Dc != self.entranceDirection:
            self.currentNode = (Xc, Yc)
            self.entranceDirection = Dc
            self.__resetRoute()

        self.planet.add_path((previousNode, self.exitDirection), (self.currentNode, rotate(self.entranceDirection)), weight)


    def __doPathSelectedMessage(self):

        self.communication.sendPathSelected(*self.currentNode, self.exitDirection)
        sleep(3)
        Dc = self.communication.getCorrectedDirection()

        if Dc is not None and Dc != self.exitDirection:

            try:
                endNode, endDir, weight = self.planet.paths[self.currentNode][Dc]
            except:
                endNode, endDir, weight = None, None, None

            # If a path with startNode != endNode is blocked, then it must have been free at some point during discovery.
            # Only if a path was free at some point should "path select --force" be ignored and a path message be sent immediately.
            if weight == -1 and endNode != self.currentNode:
                self.communication.sendDiscoveredPath(*self.currentNode, Dc, *endNode, endDir, "blocked")
                return

            self.exitDirection = Direction(Dc)
            self.__resetRoute()


    def __testTargetChanged(self):
 
        newTarget = self.communication.getTargetMessage()
        if newTarget is None:
            return

        self.target = tuple(newTarget)

        if self.currentNode == self.target:
            self.target = None
            self.communication.targetReached()
        else: 
            self.__resetRoute()


    def __testPathUnveiled(self):

        newPaths = self.communication.getPathUnveiledMessages()

        for newPath in newPaths:

            Xs, Ys, Ds, Xe, Ye, De, status, weight = newPath
            Ds = Direction(Ds)
            De = Direction(De)
            self.planet.add_path(((Xs, Ys), Ds), ((Xe, Ye), De), weight)
            self.__resetRoute()

            if weight == -1:

                try:
                    self.DFSqueue.remove(((Xs, Ys), Ds))
                    self.DFSqueue.remove(((Xe, Ye), De))
                except: pass

            else:
                self.pathsForQueue.append(((Xs, Ys), Ds))


    def __computeNextDirection(self, scannedDirections):

        self.updateQueue(scannedDirections)

        if len(self.currentRoute) == 0:

            nextDiscoveryStep = self.getDiscoveryStep()


            if self.target is not None:

                routeToTarget = self.planet.shortest_path(self.currentNode, self.target)

                if routeToTarget is None and nextDiscoveryStep is None:
                    self.communication.explorationCompleted()
                    return None
                    
                elif routeToTarget is None:
                    self.currentRoute = nextDiscoveryStep
                
                else:
                    self.currentRoute = routeToTarget
                    self.poppedPath = None
                    self.DFSqueue = self.oldDFSqueue[:]


            else:

                if nextDiscoveryStep is None:
                    self.communication.explorationCompleted()
                    return None

                self.currentRoute = nextDiscoveryStep
                
        return self.currentRoute.pop(0)[1]


    def updateQueue(self, scannedDirections):
        
        # scannedDirections is None if self.currentNode has already been visited
        if scannedDirections is not None:

            # This is done to protect DFS from a bug in Driving.scanNodes()
            # This bug is almost definitely gone by now
            scannedDirections = set(scannedDirections)
            self.DFSqueue = [(self.currentNode, direction) for direction in scannedDirections] + self.DFSqueue

        # Filter out paths that are no longer of interest to us
        self.DFSqueue = [x for x in self.pathsForQueue if x not in self.DFSqueue] + self.DFSqueue
        self.DFSqueue = list(filter(self.__pathIsInteresting, self.DFSqueue))


    # Method for computing the next DFS step

    def getDiscoveryStep(self):

        """
        Uses a modified version of DFS to get a route through the graph that 
        includes every node that has not yet been visited while using low-cost routes

        Calling this method advances the DFS by one step
        """

        if len(self.DFSqueue) == 0:
            return None

        self.oldDFSqueue = self.DFSqueue[:]
        pathsFromCurrentNode = [(node, direction) for (node, direction) in self.DFSqueue if node == self.currentNode]

        if len(pathsFromCurrentNode) > 0:

            nextPath = pathsFromCurrentNode[0]
            self.poppedPath = nextPath
            self.DFSqueue.remove(nextPath)
            return [nextPath]

        for i in range(len(self.DFSqueue)):

            self.DFSqueue = self.oldDFSqueue[:]
            nextPath = self.DFSqueue.pop(i)
            self.poppedPath = nextPath

            node = nextPath[0]
            backtrackingPath = self.planet.shortest_path(self.currentNode, node)

            if backtrackingPath is not None:
                return backtrackingPath + [nextPath]

        return None


    def __pathIsInteresting(self, path):

        startingNode = path[0]
        direction = path[1]

        try:
            endNode = self.planet.paths[startingNode][direction][0]
        except:
            return True

        if self.planet.paths[startingNode][direction][2] == -1:
            return False

        # Check whether endNode has already been visited
        if endNode in self.visitedNodes:
            return False

        # Check whether we already know 4 paths starting at endNode 
        if len(self.planet.paths[endNode]) == 4:
            return False

        return True


    def __resetRoute(self):
        self.currentRoute = []

        if self.poppedPath is not None:
            self.DFSqueue.insert(0, self.poppedPath)