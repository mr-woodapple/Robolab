#!/usr/bin/env python3

import unittest.mock
import paho.mqtt.client as mqtt
import uuid

from communication import Communication


class TestRoboLabCommunication(unittest.TestCase):
    @unittest.mock.patch('logging.Logger')
    def setUp(self, mock_logger):
        """
        Instantiates the communication class
        """
        client_id = '113-' + str(uuid.uuid4())  # Replace YOURGROUPID with your group ID
        client = mqtt.Client(client_id=client_id,  # Unique Client-ID to recognize our program
                             clean_session=False,  # We want to be remembered
                             protocol=mqtt.MQTTv311  # Define MQTT protocol version
                             )

        # Initialize your data structure here
        self.communication = Communication(client, mock_logger)

    def test_message_ready(self):
        """
        This test should check the syntax of the message type "ready"
        """
        self.communication.subscribePlanet(True)  # subscribe to comtest/113
        self.communication.sendReady(True)
        self.assertEqual(self.communication.debugMessage, "Correct")
        print(self.communication.listOfErrors)

    def test_message_path(self):
        """
        This test should check the syntax of the message type "path"
        """
        self.communication.sendDiscoveredPath(0, 4, 270, 1, 5, 90, 'free', True)
        self.assertEqual(self.communication.debugMessage, "Correct")
        print(self.communication.listOfErrors)

    def test_message_path_invalid(self):
        """
        This test should check the syntax of the message type "path" with errors/invalid data
        """
        self.communication.sendDiscoveredPath(0, -1, -1, 2, '5', 80, None, True)
        self.assertEqual(self.communication.debugMessage, "Incorrect")
        print(self.communication.listOfErrors)

    def test_message_select(self):
        """
        This test should check the syntax of the message type "pathSelect"
        """
        self.communication.sendPathSelected(2, 2, 90, True)
        self.assertEqual(self.communication.debugMessage, "Correct")
        print(self.communication.listOfErrors)

    def test_message_complete(self):
        """
        This test should check the syntax of the message type "explorationCompleted" or "targetReached"
        """
        self.communication.targetReached(True)
        self.assertEqual(self.communication.debugMessage, "Correct")
        print(self.communication.listOfErrors)
        print('______________________^^^_targetReached---explorationCompleted_vvv______________________')
        self.communication.explorationCompleted(True)
        self.assertEqual(self.communication.debugMessage, "Correct")
        print(self.communication.listOfErrors)


if __name__ == "__main__":
    unittest.main()
