import socket 
import os
from threading import Thread
import pickle
import time
import math
import random

from Game import Game
from _modules.Board import Board
from _modules.Player import Player

import _maps.basic_map as basic
import _maps.test_map as test
import _maps.big_map as big

class GameServer(Thread):
    def __init__(self, args=(), kwargs=None):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.STARTTIME = math.floor(time.time())
        self.lastUpdate = self.STARTTIME

        self.HOST = "142.93.118.50"
        self.PORT = self.args

        # Saves the print statements to a local text file:
        self.filepath = os.getcwd()
        self.logs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")
        print("\n*****NEW SERVER SESSION*****", file=self.logs)

        self.clients = []
        self.clientScreenDimensions = {}
        self.clientUpdateTimes = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creats socket

        while True:
            try:
                self.socket.bind((self.HOST,self.PORT))     # Tries to bind socket to port
                print("UDP Server started at ("+self.HOST+", "+ str(self.PORT) +")", file=self.logs)
                break                                       # Has bound to a port, exits the while loop
            except:
                self.PORT += 1      # If port is taken, tries the next port up

        # Game information
        self.map     = None
        self.board   = None
        self.players = []

        # GAME FUNCTIONS HERE:
        self.lobbyStage()
        self.setupStage()
        self.placementStage()
        self.battleStage()

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
            print("Removing:", client, file=self.logs)
            self.clients.remove(client)

    def lobbyStage(self):
        """Handles connecting players and setting up the game."""
        # Organizes outbound data to clients into a dict
        print("(" + str(self.HOST) + ", " + str(self.PORT) +"):: Starting lobby stage.", file=self.logs)
        gameState = {
            "connection": str(self.PORT), 
            "ready":False,
            "start":False,
            "opponentPort": None,
            'testObj':''
            }

        counter = None
        while True:
            try:
                inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
                data = inboundData[0]                         # Separates data from address
                address = inboundData[1]                      # Separates address from data
                data = pickle.loads(data)                     # Unpickles data back into a python dict
                counter = data["counter"]
            except TimeoutError as t:
                print(t, file=self.logs)
            except Exception as e:
                print(e, file=self.logs)

            # Keeps track of how often the server recieves information from each client.
            updatedTime = time.time()                     
            self.clientUpdateTimes[str(address)] = updatedTime

            # If a new address connects, add it  to the list of clients
            if address not in self.clients:
                self.clients.append(address)
                print(str(address)+ ":: New connection.", file=self.logs)
            
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
                    print("(" + str(address) +")::", data, file=self.logs)   # Only prints out non-trivial data from clients                            
                    
                    # Handle commands from other servers
                    if data['command'] == "close":              # Ends the server
                        break

                    if data['command'] == 'ping':               # Confirms connection to client servers
                        print("(" + str(address) +")::", self.clients, file=self.logs)
                
                    if data['command'] == 'start':
                        for client in self.clients:             # Tells both player views to move on
                            gameState['start'] = True           # to the next stage
                            outboundData = pickle.dumps(gameState)
                            self.socket.sendto(outboundData, client)
                        break

            # Packages up data and sends it back to the client
            try:
                outboundData = pickle.dumps(gameState)
                self.socket.sendto(outboundData, address)
            except TimeoutError as t:
                print(t, file=self.logs)
            except Exception as e:
                print(e, file=self.logs)
                


            # Continuously saves logging information to a text file:
            self.logs.close()
            self.logs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")

            # counter += 1

            # Check client connections here
            # self.cleanClientList(time.time())

    def setupStage(self):
        """Determines dimensions of the game board, players' names, and eventually the player's army.
        Return a tuple containing (Board, Player1, Player2)."""
        print("(" + str(self.HOST) + ", " + str(self.PORT) +"):: Initiating setup stage", file=self.logs)

        # Holds player map and name information here. Will be used to create objects later.
        mapVotes = []
        playerNames = {}
        colors  = ["red", "blue"]

        gameState = {
            "connection":self.PORT,
            "ready": False,
            "game": None     
        }
        while True:
            # Continuously saves logging information to a text file:
            self.logs.close()
            self.logs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")

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
            
            # Both votes are in. Chooses a map, builds the Board object.
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

                    # Builds the game board
                    self.board = Board(self.map.dimensions[0], self.map.dimensions[1], self.map.MAP)

            # Both players' names have been entered, creates Player objects.\
            # Appends player objects to state variable. 
            if len(playerNames) == 2 and len(colors) > 0:
                p = Player(playerNames[str(address)], colors.pop(), None, self.map.tokens, address)
                self.players.append(p)
                
            # Player objects and Board object have both been created.
            # Builds the Game object, stores it, then tells the PlayerViews its ready.
            if len(self.players) == 2 and self.board != None:
                self.game = Game(self.board, self.players[0], self.players[1])
                gameState['game'] = self.game
                gameState['ready'] = True

                # Sends data to both players simultaneously
                for client in self.clients:
                    outboundData = pickle.dumps(gameState)
                    self.socket.sendto(outboundData, client)
                break

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

    def placementStage(self):
        """Communicates with player objects.
           Controls player turn-taking for placement.
           Keeps track of board and player changes."""
        print("(" + str(self.HOST) + ", " + str(self.PORT) +"):: Entering placement stage", file=self.logs)

        activePlayer = self.players[0]
        readyPlayers = set()

        gameState = {
            "connection": str(self.PORT), 
            "active": activePlayer.getName(),
            "game": self.game,
            "ready": False,
            "start": False
            }
        while True:
            # Continuously saves logging information to a text file:
            self.logs.close()
            self.logs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")

            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict


            # Keeps track of how often the server recieves information from each client.
            updatedTime = time.time()                     
            self.clientUpdateTimes[str(address)] = updatedTime

            if data['stage'] == 'placement':
                # Interacts with the game object, then sends the updated game back
                self.game.placementActions(data['command'], data['square'], data['newTroop'], data['upgrades'])
                gameState['game'] = self.game

                # Advances to battle stage of the game, and tells the players to do the same
                if data['start'] == True:
                    readyPlayers.add(address)
                if len(readyPlayers) == 2:
                    for address in readyPlayers:
                        gameState['start'] = True
                        outboundData = pickle.dumps(gameState)
                        self.socket.sendto(outboundData, address)
                    break

                ready = 0
                for player in self.game.getPlayers():
                    if player.getTokens() == 0:
                        ready += 1

                if ready == 2:
                    gameState['ready'] = True

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

            # Check client connections here
            # self.cleanClientList(time.time())

    def battleStage(self):
        """Communicates with player objects.
           Controls player turn-taking for placement.
           Keeps track of board and player changes."""
        # Continuously saves logging information to a text file:
        self.logs.close()
        self.logs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")

        print("(" + str(self.HOST) + ", " + str(self.PORT) +"):: Entering battle stage", file=self.logs)

        # Prepare the board for play; removes red and blue squares from the board
        self.game.normalizeBoard()
        
        # Sets players' moves per turn
        self.game.setPlayerMoves()

        # Keeps track of who can edit the board.
        activePlayer = self.players[0]

        gameState = {
            "connection": str(self.PORT), 
            "active": activePlayer.getName(),
            "game": self.game
            }
        while True:
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            # Keeps track of how often the server recieves information from each client.
            updatedTime = time.time()                     
            self.clientUpdateTimes[str(address)] = updatedTime

            if data['stage'] == 'battle':
                # Interacts with the game object, then sends the updated game back
                if data['command'] != None:        # Only sends relevante data
                    self.game.battleActions(data['command'], data['square'], data['moveSquare'])
                    gameState['game'] = self.game

            # Packages up data and sends it back to the client
            outboundData = pickle.dumps(gameState)
            self.socket.sendto(outboundData, address)

            # Check client connections here
            # self.cleanClientList(time.time())
