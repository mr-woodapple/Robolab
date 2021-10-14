#!/usr/bin/env python3

import unittest
from planet import Direction, Planet



class ExampleTestPlanet(unittest.TestCase):


    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """

        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST ), ((0, 0), Direction.WEST ), 1)


    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """

        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))



class TestRoboLabPlanet(unittest.TestCase):


    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths
        """
        
        """
        planet:

                  2,5-----4,5--+
        +--+       |           |
        |  |       +-------+   |
        +-0,3------+       |   | 
           |       |       |   +
          0,2-----2,2-3,2-4,2-5,2-----7,2  
           |      /            +       |
        +-0,1    /             |       |
        |  |    /              |       |
        +-0,0-1,0-2,0----------+       |
                   |                   |
                   +-------------------+

        """

        self.planet = Planet()

        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)

        self.planet.add_path(((0, 1), Direction.WEST ), ((0, 0), Direction.WEST ), 1)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST ), 1)

        self.planet.add_path(((0, 0), Direction.EAST ), ((1, 0), Direction.WEST ), 1)
        self.planet.add_path(((1, 0), Direction.EAST ) ,((2, 0), Direction.WEST ), 1)

        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST ), ((2, 2), Direction.WEST ), 1)
        self.planet.add_path(((0, 3), Direction.EAST ), ((2, 2), Direction.NORTH), 1)

        self.planet.add_path(((2, 2), Direction.EAST ), ((3, 2), Direction.WEST ), 1)
        self.planet.add_path(((3, 2), Direction.EAST ), ((4, 2), Direction.WEST ), 1)
        self.planet.add_path(((4, 2), Direction.EAST ), ((5, 2), Direction.WEST ), 1)

        self.planet.add_path(((2, 5), Direction.EAST ), ((4, 5), Direction.WEST ), 3)
        self.planet.add_path(((5, 2), Direction.NORTH), ((4, 5), Direction.EAST ), 3)
        self.planet.add_path(((2, 5), Direction.SOUTH), ((4, 2), Direction.NORTH), 6)
        self.planet.add_path(((2, 0), Direction.EAST ), ((5, 2), Direction.SOUTH), 999)

        self.planet.add_path(((7, 2), Direction.WEST ), ((5, 2), Direction.EAST ), -1)
        self.planet.add_path(((7, 2), Direction.SOUTH), ((2, 0), Direction.SOUTH), 653)


        """
        planet_not_reachable:

        +--+
        |  |
        +-0,3------+
                   |
                  2,2 
                   |
        +-0,1--+   |
        |      |   |
        +-0,0--+  2,0

        """

        self.planet_not_reachable = Planet()

        self.planet_not_reachable.add_path(((0, 0), Direction.EAST ), ((0, 1), Direction.EAST ), 1)
        self.planet_not_reachable.add_path(((0, 0), Direction.WEST ), ((0, 1), Direction.WEST ), 1)

        self.planet_not_reachable.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST ), 1)
        self.planet_not_reachable.add_path(((0, 3), Direction.EAST ), ((2, 2), Direction.NORTH), 1)
        self.planet_not_reachable.add_path(((2, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), -1)


        """
        planet_loop:

        0,2------+       +--+
         |       |       |  |
        0,1-----2,1-----4,1-+
         |       |       |
        0,0-----2,0-----4,0
         |       |       |
        0,-1----2,-1----4,-1

        """

        self.planet_loop = Planet()

        self.planet_loop.add_path(((0,  1), Direction.EAST ), ((2,  1), Direction.WEST ), 1)
        self.planet_loop.add_path(((2,  1), Direction.EAST ), ((4,  1), Direction.WEST ), 1)

        self.planet_loop.add_path(((0,  0), Direction.EAST ), ((2,  0), Direction.WEST ), 1)
        self.planet_loop.add_path(((2,  0), Direction.EAST ), ((4,  0), Direction.WEST ), 1)

        self.planet_loop.add_path(((0, -1), Direction.EAST ), ((2, -1), Direction.WEST ), 1)
        self.planet_loop.add_path(((2, -1), Direction.EAST ), ((4, -1), Direction.WEST ), 1)

        self.planet_loop.add_path(((0, -1), Direction.NORTH), ((0,  0), Direction.SOUTH), 1)
        self.planet_loop.add_path(((2, -1), Direction.NORTH), ((2,  0), Direction.SOUTH), 1)
        self.planet_loop.add_path(((4, -1), Direction.NORTH), ((4,  0), Direction.SOUTH), 3)

        self.planet_loop.add_path(((0,  0), Direction.NORTH), ((0,  1), Direction.SOUTH), 1)
        self.planet_loop.add_path(((2,  0), Direction.NORTH), ((2,  1), Direction.SOUTH), 1)
        self.planet_loop.add_path(((4,  0), Direction.NORTH), ((4,  1), Direction.SOUTH), 1)

        self.planet_loop.add_path(((4,  1), Direction.NORTH), ((4,  1), Direction.EAST ),  1)
        self.planet_loop.add_path(((0,  1), Direction.NORTH), ((0,  2), Direction.SOUTH), -1)
        self.planet_loop.add_path(((2,  1), Direction.NORTH), ((0,  2), Direction.EAST ), -1)
    

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        
        paths = self.planet.get_paths()
        self.assertIsInstance(paths, dict)

        for node, pathdict in paths.items():

            self.assertIsInstance(node, tuple)
            self.assertIsInstance(pathdict, dict)
            self.assertIsInstance(node[0], int)
            self.assertIsInstance(node[1], int)

            for direction, path in pathdict.items():

                self.assertIsInstance(direction, Direction)

                self.assertIsInstance(path, tuple)
                self.assertIsInstance(path[0], tuple)
                self.assertIsInstance(path[0][0], int)
                self.assertIsInstance(path[0][1], int)
                self.assertIsInstance(path[1], Direction)

                # Weights are assumed to be integers due to the type hints in planet.py
                self.assertIsInstance(path[2], int)


    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        
        emptyPlanet = Planet()
        self.assertEqual(emptyPlanet.get_paths(), dict())


    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """

        shortestPath = self.planet.shortest_path((2, 0), (0, 3))
        actualShortestPath = [((2, 0), Direction.WEST), ((1, 0), Direction.NORTH), ((2, 2), Direction.NORTH)]
        self.assertEqual(shortestPath, actualShortestPath)

        shortestPath = self.planet.shortest_path((2, 0), (4, 5))
        actualShortestPath = [
                              ((2, 0), Direction.WEST), ((1, 0), Direction.NORTH), 
                              ((2, 2), Direction.EAST), ((3, 2), Direction.EAST ), 
                              ((4, 2), Direction.EAST), ((5, 2), Direction.NORTH)
                             ]
        self.assertEqual(shortestPath, actualShortestPath)

        shortestPath = self.planet.shortest_path((2, 5), (0, 3))
        actualShortestPath = [
                              ((2, 5), Direction.SOUTH), ((4, 2), Direction.WEST ), 
                              ((3, 2), Direction.WEST ), ((2, 2), Direction.NORTH)
                             ]
        self.assertEqual(shortestPath, actualShortestPath)

        shortestPath = self.planet.shortest_path((7, 2), (5, 2))
        actualShortestPath = [
                              ((7, 2), Direction.SOUTH), ((2, 0), Direction.WEST), 
                              ((1, 0), Direction.NORTH), ((2, 2), Direction.EAST),
                              ((3, 2), Direction.EAST ), ((4, 2), Direction.EAST)
                             ]
        self.assertEqual(shortestPath, actualShortestPath)

        shortestPath = self.planet.shortest_path((2, 5), (5, 2))
        actualShortestPath = [((2, 5), Direction.EAST), ((4, 5), Direction.EAST)]
        self.assertEqual(shortestPath, actualShortestPath)


    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """

        shortestPath = self.planet_not_reachable.shortest_path((0, 1), (2, 2))
        self.assertIsNone(shortestPath)

        shortestPath = self.planet_not_reachable.shortest_path((2, 2), (2, 0))
        self.assertIsNone(shortestPath)

        shortestPath = self.planet_not_reachable.shortest_path((2, 2), (5, 0))
        self.assertIsNone(shortestPath)
        

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented returns a shortest path even if there
        are multiple shortest paths with the same length.

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """

        shortestPath = self.planet.shortest_path((0, 0), (0, 3))
        actualShortestPath1 = [((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH), ((0, 2), Direction.NORTH)]
        actualShortestPath2 = [((0, 0), Direction.WEST ), ((1, 0), Direction.NORTH), ((2, 2), Direction.NORTH)]
        self.assertTrue(shortestPath == actualShortestPath1 or shortestPath == actualShortestPath2)

        shortestPath = self.planet.shortest_path((0, 1), (1, 0))
        actualShortestPath1 = [((0, 1), Direction.SOUTH), ((0, 0), Direction.EAST)]
        actualShortestPath2 = [((0, 1), Direction.WEST ), ((0, 0), Direction.EAST)]
        self.assertTrue(shortestPath == actualShortestPath1 or shortestPath == actualShortestPath2)

        shortestPath = self.planet_loop.shortest_path((4, -1), (4, 1))
        actualShortestPath1 = [((4, -1), Direction.NORTH), ((4, 0), Direction.NORTH)]
        actualShortestPath2 = [
                               ((4, -1), Direction.WEST), ((2, -1), Direction.NORTH), 
                               ((2,  0), Direction.EAST), ((4,  0), Direction.NORTH)
                              ]
        actualShortestPath3 = [
                               ((4, -1), Direction.WEST ), ((2, -1), Direction.NORTH), 
                               ((2,  0), Direction.NORTH), ((2,  1), Direction.EAST )
                              ]
        self.assertTrue(shortestPath == actualShortestPath1 or 
                        shortestPath == actualShortestPath2 or
                        shortestPath == actualShortestPath3
        )
        

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """

        shortestPath = self.planet_loop.shortest_path((0, -1), (2, 1))
        actualShortestPath1 = [((0, -1), Direction.NORTH), ((0,  0), Direction.NORTH), ((0,  1), Direction.EAST )]
        actualShortestPath2 = [((0, -1), Direction.NORTH), ((0,  0), Direction.EAST ), ((2,  0), Direction.NORTH)]
        actualShortestPath3 = [((0, -1), Direction.EAST ), ((2, -1), Direction.NORTH), ((2,  0), Direction.NORTH)]
        self.assertTrue(shortestPath == actualShortestPath1 or 
                        shortestPath == actualShortestPath2 or
                        shortestPath == actualShortestPath3
        )

        shortestPath = self.planet_loop.shortest_path((2, 0), (4, 1))
        actualShortestPath1 = [((2, 0), Direction.NORTH), ((2, 1), Direction.EAST )]
        actualShortestPath2 = [((2, 0), Direction.EAST ), ((4, 0), Direction.NORTH)]
        self.assertTrue( shortestPath == actualShortestPath1 or
                         shortestPath == actualShortestPath2
        )

        shortestPath = self.planet_loop.shortest_path((4, 1), (4, 1))
        actualShortestPath = []
        self.assertEqual(shortestPath, actualShortestPath)


    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """

        shortestPath = self.planet_not_reachable.shortest_path((0, 0), (0, 3))
        self.assertIsNone(shortestPath)

        shortestPath = self.planet_loop.shortest_path((4, -1), (0, 2))
        self.assertIsNone(shortestPath)



if __name__ == "__main__":
    unittest.main()