import pygame as pg

import socket 
import pickle
import time
import math
import random

from Game import Game
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

        # Game information
        self.map = None
        self.board   = None
        self.players = []

        # Begins connecting two players
        self.lobbyStage()
        self.setupStage()

        # Terminates the socket when the game is done
        self.socket.close()

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

    def lobbyStage(self):
        """Handles connecting players and setting up the game."""
        # Organizes outbound data to clients into a dict
        gameState = {
            "connection": str(self.PORT), 
            "ready":False,
            "start":False,
            "opponentPort": None,
            'testObj':''
            }

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
                
                    if data['command'] == 'start':
                        for client in self.clients:             # Tells both player views to move on
                            gameState['start'] = True           # to the next stage
                            outboundData = pickle.dumps(gameState)
                            self.socket.sendto(outboundData, client)
                        break

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

            # Check client connections here
            self.cleanClientList(time.time())

    def setupStage(self):
        """Determines dimensions of the game board, players' names, and eventually the player's army.
        Return a tuple containing (Board, Player1, Player2)."""
        print("--- Initiating setup stage")

        # Holds player map and name information here. Will be used to create objects later.
        mapVotes = []
        playerNames = {}
        colors  = ["blue","red"]

        gameState = {
            "connection":self.PORT,
            "player": None,
            "map": None,
            "board": None,
            "ready": False     
        }
        while True:
            # Gets all the events from the game window. A.k.a., do stuff here.
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            command = data['command']
            if command != None:       
                # Takes in information from both players
                if command == "SUBMIT":
                    pName = data['playerName']
                    mVote = data['mapVote']

                    mapVotes.append(mVote)
                    playerNames[str(address)] = pName
            
            # Both votes are in. Chooses a map, builds the board and player objects.
            # Keeps all of this information here on the server, but tells PlayerViews they can advance.
            if len(mapVotes) == 2:
                # Only chooses one map for both players
                if self.map == None:
                    m = random.choice(mapVotes)
                    if m == "TEST":
                        self.map = test
                    if m == "BIG":
                        self.map = big
                    if m == "BASIC":
                        self.map = basic
                
                # Builds a board and sends it to both players
                self.board = Board(self.map.dimensions[0], self.map.dimensions[1], self.map.MAP)
                p = Player(playerNames[str(address)], colors.pop(), None, self.map.tokens, address)
                self.players.append(p)
            
                # Send back player and board objects, and tell clients the game is ready
                gameState["board"] = self.board
                gameState["player"] = p
                gameState["ready"] = True

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)
        
        return 

    def placementStage(self):
        """Communicates with player objects.
           Controls player turn-taking for placement.
           Keeps track of board and player changes."""
        print("--- Entering placement stage")
        gameState = {
            "connection": str(self.PORT), 
            "ready":False,
            }
        while True:
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            # Keeps track of how often the server recieves information from each client.
            updatedTime = time.time()                     
            self.clientUpdateTimes[str(address)] = updatedTime

            if data['command'] != "":
                pass

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

            # Check client connections here
            self.cleanClientList(time.time())




GameServer()