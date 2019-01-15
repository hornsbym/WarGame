import socket 
import pickle
import time
import math
import pygame as pg
from _modules.TroopButton import TroopButton
from Game import Game

import _modules.pygame_textinput as pygame_textinput
from _modules.Square import Square
from _modules.Board import Board
from _modules.TroopButton import TroopButton
from _modules.CommandButton import CommandButton
from _modules.Player import Player
from _modules.Troop import Troop

import _maps.basic_map as basic
import _maps.test_map as test
import _maps.big_map as big


class GameServer(object):
    def __init__(self):
        self.STARTTIME = math.floor(time.time())
        self.lastUpdate = self.STARTTIME

        self.HOST = "127.0.0.1"
        self.PORT = 5000

        self.clients = []
        self.clientScreenDimensions = {}
        self.clientUpdateTimes = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creats socket
        self.socket.bind((self.HOST,self.PORT))                           # Binds socket to local port
        print("UDP Server started at", self.PORT)


        # Begins connecting two players
        self.lobbyStage()

        # Terminates the socket when the game is done
        self.socket.close()

    def lobbyStage(self):
        """Handles connecting players and setting up the game."""
        # Organizes outbound data to clients into a dict
        gameState = {
            "connection": str(self.PORT), 
            "ready":False,
            "opponentPort": None,
            'testObj':''}

        while True:
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            # Keeps track of how often the server recieves information from each client.
            updatedTime = time.time()                     
            self.clientUpdateTimes[str(address)] = updatedTime

            # If a new address connects, add it  to the list of clients
            if address not in self.clients:
                self.clients.append(address)
            
            # If there are two players, the game is ready to start.
            if len(self.clients) == 2:
                gameState['ready'] = True  
                for client in self.clients:
                    if client != address:
                        gameState['opponentPort'] = client  
            
            if len(self.clients) == 1:
                gameState['ready'] = False
                gameState['opponentPort'] = None

            # Maintains dictionary of each clients' screen resolutions.
            # Only on the first connection of a new client.
            if 'dimensions' in data:
                dimensions = data['dimensions']
                self.clientScreenDimensions[str(address)] = dimensions
            else:
                if data['command'] != "":
                    print(data)   # Only prints out non-trivial data from clients                            
                    
                    # Handle commands from other servers
                    if data['command'] == "close":              # Ends the server
                        break

                    if data['command'] == 'ping':               # Confirms connection to client servers
                        print(self.clients)

                    if data['command'] == 'state':                # Sends back Pickled game objects
                        dimensions = self.clientScreenDimensions[str(address)]
                        x = dimensions[0]
                        y = dimensions[1]
                        sampleObj = TroopButton(("troop",1,1,25,1,100,(1,1),1,1), (x//2, y-100))

                        gameState['testObj'] = sampleObj
                
            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

            # Check client connections here
            self.cleanClientList(time.time())

    def setupStage(self):
        """Determines dimensions of the game board, players' names, and eventually the player's army.
        Return a tuple containing (Board, Player1, Player2)."""
        b = None
        m  = None

        gameState = {
            "stage":"setup",
            "objectList":[]
        }
        loop = True
        while (loop == True):
            # Gets all the events from the game window. A.k.a., do stuff here.
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            command = data['command']
            if command != "":       
                nameInput = pygame_textinput.TextInput("Player "+ str(self.PORT))
                
                testMap       = CommandButton("TEST",(self.clientScreenDimensions[str(address)][0]*.25-35,self.clientScreenDimensions[str(address)][1]//2), (0,0,0))
                baseMap       = CommandButton("BASIC",(self.clientScreenDimensions[str(address)][0]*.5-35, self.clientScreenDimensions[str(address)][1]//2), (0,0,0))
                bigMap        = CommandButton("BIG",(self.clientScreenDimensions[str(address)][0]*.75-35, self.clientScreenDimensions[str(address)][1]//2), (0,0,0))

                changeNameButton = CommandButton("PLAYER 1",(self.clientScreenDimensions[str(address)][0]//2,self.clientScreenDimensions[str(address)][1]//2), (100,100,100))

                gameState["objectList"].append(testMap)
                gameState["objectList"].append(baseMap)
                gameState["objectList"].append(bigMap)
                gameState["objectList"].append(changeNameButton)

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)




        
        p = Player(nameInput.get_text(),"blue",None,m.tokens)
        
        return (b,p)

    def cleanClientList(self, time):
        """Takes in a time value.
           Checks the players in the game's last update time against this new current time.
           Removes disconnected players from the game."""
        removeList = []
        for client in self.clients:
            diff = time - self.clientUpdateTimes[str(client)]
            if diff > 1:
                removeList.append(client)
        for client in removeList:
            print("Removing:", client)
            self.clients.remove(client)



GameServer()