#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import platform
import ssl
import time

# Fix: SSL certificate problem on macOS
if all(platform.mac_ver()):
    from OpenSSL import SSL


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """
    groupID = '113'
    pw = 'DK0o9PfC56'
    port = 8883
    url = 'mothership.inf.tu-dresden.de'

    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        # Add your client setup here
        self.client.username_pw_set(Communication.groupID, password=Communication.pw)  # set username and password
        self.client.connect(Communication.url, Communication.port)  # establish initial connection
        self.client.subscribe('explorer/113', qos=1)  # subscribe to mothership
        self.client.loop_start()  # start listening to incoming message
        self.planetName = ''
        self.planetMessage = None
        self.pathMessage = None
        self.correctedDirection = None
        self.pathUnveiledMessages = []
        self.targetMessage = None
        self.doneMessage = ''
        self.debugMessage = ''
        self.listOfErrors = ''

        self.logger = logger

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client (not used)
        :param data: Object (not used)
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))  # convert JSON Object to dict
        self.logger.debug(json.dumps(payload, indent=2))

        if payload['from'] == 'client':
            pass  # ignore echoing message from the robot
        elif payload['from'] == 'server':  # handle message from server differently, based on the type
            if payload['type'] == 'planet':  # message that arrived after the robot send 'ready' message
                #  save the planet name, start coordination and start direction in the list
                # ensure that malicious messages cannot alter self.planetName
                if self.planetName == '':
                    self.planetName = payload['payload']['planetName']
                self.planetMessage = list(payload['payload'].values())
            elif payload['type'] == 'path':
                self.pathMessage = list(payload['payload'].values())
            elif payload['type'] == 'pathSelect':
                self.correctedDirection = payload['payload']['startDirection']
            elif payload['type'] == 'pathUnveiled':
                self.pathUnveiledMessages.append(list(payload['payload'].values()))
            elif payload['type'] == 'target':
                self.targetMessage = list(payload['payload'].values())
            elif payload['type'] == 'done':
                self.doneMessage = payload['payload']['message']
        else:  # payload['from'] == 'debug': (only used in development phase, for testing)
            if payload['type'] == 'error':
                pass
            elif payload['type'] == 'notice':
                self.debugMessage = payload['payload']['message']
            elif payload['type'] == 'syntax':
                self.debugMessage = payload['payload']['message']
                self.listOfErrors = payload['payload']['errors']

    # getter Methods
    def getPlanetMessage(self):
        return self.planetMessage

    def getPathMessage(self):
        return self.pathMessage

    def getCorrectedDirection(self):
        return self.correctedDirection

    def getPathUnveiledMessages(self):
        return self.pathUnveiledMessages

    def getTargetMessage(self):
        return self.targetMessage

    def getDoneMessage(self):
        return self.doneMessage

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))
        message_json = json.dumps(message)  # convert message to JSON Object
        self.client.publish(topic, payload=message_json, qos=1)  # topic is here the specified channel

    def sendReady(self, unittest=False):
        """
        Sends 'ready' message to the mothership
        :param unittest: Boolean
        :return: void
        """
        ready = {"from": "client",
                 "type": "ready"}
        if not unittest:
            self.send_message('explorer/113', ready)  # send 'ready' to the mothership
        else:
            self.send_message('comtest/113', ready)  # special channel for testing
        # receive planetName from mothership, filled from on_message

    def subscribePlanet(self, unittest=False):
        if not unittest:
            self.client.subscribe('planet/' + self.planetName + '/113', qos=1)  # subscribe to the corresponding planet
        else:
            self.client.subscribe('comtest/113', qos=1)  # special channel for testing

    def sendTestPlanet(self, testPlanetName):
        """
        Sends planet name to mothership, this method only needed in the development phase
        """
        testPlanet = {"from": "client",
                      "type": "testplanet",
                      "payload": {
                          "planetName": testPlanetName}
                       }
        self.send_message('explorer/113', testPlanet)

    def sendDiscoveredPath(self, startX, startY, startDirection, endX, endY, endDirection, status, unittest=False):
        """
        Sends the discovered path to the mothership
        :param startX: Integer
        :param startY: Integer
        :param startDirection: Integer
        :param endX: Integer
        :param endY: Integer
        :param endDirection: Integer
        :param status: String
        :param unittest: Boolean
        :return: void
        """
        discoveredPath = {"from": "client",
                          "type": "path",
                          "payload": {
                             "startX": startX,
                             "startY": startY,
                             "startDirection": startDirection,
                             "endX": endX,
                             "endY": endY,
                             "endDirection": endDirection,
                             "pathStatus": status
                                      }
                           }
        if not unittest:
            self.send_message('planet/' + self.planetName + '/113', discoveredPath)
        else:
            self.send_message('comtest/113', discoveredPath)  # special channel for testing

    def sendPathSelected(self, startX, startY, startDirection, unittest=False):
        """
        Sends selected path to mothership
        :param startX: Integer
        :param startY: Integer
        :param startDirection: Integer
        :param unittest: Boolean
        :return: void
        """
        selectedPath = {"from": "client",
                        "type": "pathSelect",
                        "payload": {
                                    "startX": startX,
                                    "startY": startY,
                                    "startDirection": startDirection
                                    }
                         }
        if not unittest:
            self.send_message('planet/' + self.planetName + '/113', selectedPath)
        else:
            self.send_message('comtest/113', selectedPath)  # special channel for testing

    def targetReached(self, unittest=False):
        """
        Sends message to mothership, that the target reached
        :param unittest: Boolean:
        :return: void
        """
        targetReached = {"from": "client",
                         "type": "targetReached",
                         "payload": {
                              "message": "Target reached - I'm done with this! ✋🎤"}
                         }
        if not unittest:
            self.send_message('explorer/113', targetReached)
        else:
            self.send_message('comtest/113', targetReached)  # special channel for testing

    def explorationCompleted(self, unittest=False):
        """
        Sends message to mothership, that the whole planet has been discovered
        :param unittest: Boolean:
        :return: void
        """
        explorationCompleted = {"from": "client",
                                "type": "explorationCompleted",
                                "payload": {
                                     "message": "It's just a small step for me, but a huge for all robots: The whole planet has been discovered! 🤖"}
                                }
        if not unittest:
            self.send_message('explorer/113', explorationCompleted)
        else:
            self.send_message('comtest/113', explorationCompleted)  # special channel for testing

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise
