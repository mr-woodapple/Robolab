#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from os import DirEntry
from typing import List, Tuple, Dict, Union

from math import inf 
from heapq import heappush, heappop


class PriorityQueue:

    """ 
    A simple priority queue
    for planet.shortest_path(...)
    """

    def __init__(self):
        self.items = []

    def __contains__(self, item):
        return any(y == item for x, y in self.items)

    def empty(self):
        return len(self.items) == 0 

    def push(self, item, priority: int):
        heappush(self.items, (priority, item))

    def pop(self):
        return heappop(self.items)[1]

    def update(self, item, oldPriority: int, newPriority: int):

        #self.items = filter(lambda x: x[1] != item, self.items)
        self.items.remove((oldPriority, item))
        self.push(item, newPriority)


@unique
class Direction(IntEnum):
    """ Directions in shortcut """
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:

    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """
        self.paths = dict()


    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):

        """
        Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target: 2-Tuple
        :param weight: Integer
        :return: void
        """

        node1 = start[0]
        node2 = target[0]
        dir1 = Direction(start[1])
        dir2 = Direction(target[1])

        pathsFromNode1 = self.paths.get(node1, dict())
        pathsFromNode2 = self.paths.get(node2, dict())
        pathsFromNode1[dir1] = node2, dir2, weight
        pathsFromNode2[dir2] = node1, dir1, weight
        self.paths[node1] = pathsFromNode1
        self.paths[node2] = pathsFromNode2


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:

        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2),
                    Direction.WEST: ((0, 3), Direction.NORTH, 1)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        return self.paths


    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:

        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        # Implementation of Djikstra's algorithm

        # Initialize data structures 
        allNodes = list(self.paths.keys())
        queue = PriorityQueue()
        queue.push(start, 0)

        distance = {x : (0 if x == start else inf) for x in allNodes}
        predecessor = {x: (x if x == start else None) for x in allNodes}


        # Core loop
        while not queue.empty():
            currentNode = queue.pop()

            for neighbourData in self.__getNeighbourDatas(currentNode):

                neighbour = neighbourData[0]
                neighbourDir = neighbourData[1]
                neighbourWeight = neighbourData[2]
                newDistance = distance[currentNode] + neighbourWeight

                if neighbour in queue and distance[neighbour] > newDistance:
                    queue.update(neighbour, distance[neighbour], newDistance)
                    distance[neighbour] = newDistance
                    predecessor[neighbour] = currentNode, neighbourDir

                elif predecessor[neighbour] is None:
                    queue.push(neighbour, newDistance)
                    distance[neighbour] = newDistance
                    predecessor[neighbour] = currentNode, neighbourDir
        

        # Piece together a shortest path or return None if no shortest path can be found
        print("Shortest path wird berechnet")
        getPath = lambda node: getPath(predecessor[node][0]) + [predecessor[node]] if node != start else []
        try: return getPath(target)
        except: return None


    def __getNeighbourDatas(self, node: Tuple[int, int]):

        """
        Helper method for shortest_path(...)
        """

        nodeData = self.paths[node].items()
        return [(path[0], dir, path[2]) for dir, path in nodeData if path[2] > 0]


    def updateWeight(self, node1: Tuple[int, int], dir1: Direction):

        """
        If an obstacle has been found, this method attempts to update the weight of 
        the corresponding path
        If there is no corresponding, it does nothing

        node1 is the starting node, dir1 is the direction in which the robot was traveling
        """
        
        try:
            pathsFromNode1 = self.paths[node1]
            node2, dir2 = pathsFromNode1[dir1][:2]

            dir1 = Direction(dir1)
            dir2 = Direction(dir2)

            pathsFromNode2 = self.paths[node2]
            pathsFromNode1[dir1] = node2, dir2, -1
            pathsFromNode2[dir2] = node1, dir1, -1
            self.paths[node1] = pathsFromNode1
            self.paths[node2] = pathsFromNode2

        except:
            return