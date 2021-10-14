#!/usr/bin/env python3

import unittest.mock
import paho.mqtt.client as mqtt
import uuid

from communication import Communication
from explorer import Explorer
from planet import Direction

class TestDiscovery(unittest.TestCase):


    def setUp(self):

        """
        the planet to explore:

         +-----2,1-----+
         |             |
        0,0           4,0     
         |             |
        0,-1          4,-1
         |             |
        0,-2----------4,-2
        
        """

        self.setUpCommunication()
        explorer = Explorer(self.communication)

        pathlist = [

            (((2,  1), Direction.EAST ), ((4,  0), Direction.NORTH), 1),
            (((2,  1), Direction.WEST ), ((0,  0), Direction.NORTH), 1),
            (((0, -2), Direction.EAST ), ((4, -2), Direction.WEST ), 1),

            (((0,  0), Direction.SOUTH), ((0, -1), Direction.NORTH), 1),
            (((0, -1), Direction.SOUTH), ((0, -2), Direction.NORTH), 1),
            (((4,  0), Direction.SOUTH), ((4, -1), Direction.NORTH), 1),
            (((4, -1), Direction.SOUTH), ((4, -2), Direction.NORTH), 1),

        ]

        for path in pathlist:
            explorer.planet.add_path(*path)


    @unittest.mock.patch('logging.Logger')
    def setUpCommunication(self, mock_logger):

        client_id = '113-' + str(uuid.uuid4())
        client = mqtt.Client(client_id = client_id, clean_session = False, protocol = mqtt.MQTTv311)
        self.communication = Communication(client, mock_logger)


    def testTarget(self):

        self.communication.sendReady(True)



if __name__ == "__main__":
    unittest.main()