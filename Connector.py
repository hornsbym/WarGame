"""
 Author: Mitchell Hornsby
   File: Connector.py
Purpose: Creates a socket that constantly runs. It waits for players to connect 
         and then pairs them up in a new GameServer.
"""
from GameServer import GameServer
import socket 
import pickle

class Connector (object):
    def __init__(self):
        """
        Starts the server.
        """
        # Socket info here:
        # self.HOST = "142.93.118.50"     # On the server
        self.HOST = "127.0.0.1"     # For testing
        self.PORT = 4999
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creates socket
        self.socket.bind((self.HOST,self.PORT))                           # Binds socket to local port
        print("CONNECTOR: listening at port", self.PORT)

        # Keeps track of existing games here (only allow 10 for testing):
        self.activePort = 5000
        self.connected = 0

        self.waitingList = []
        self.activeGames = []

        self.start()

    def start(self):
        """ Begins the primary loop for the server."""
        outboundData = {
            "gameServer host": None,
            "gameServer port": None
        }

        counter = 0 
        while True:
            # Each time a person joins, iterates over the current list of active games.
            # If any of the games has finished, removes that game and re-opens the port.
            for thread in self.activeGames:
                if thread.isAlive() == False:
                    self.activeGames.remove(thread)
                    
            print("CONNECTOR: Active port number is", self.activePort, "Iteration", counter)
            counter += 1

            print('CONNECTOR: Trying to recieve data...')
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address            
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            print("CONNECTOR: Message:", data, "From:",address)

            self.waitingList.append(address)

            # Creates a new Game server here
            if len(self.waitingList) >= 2:
                print("CONNECTOR: Someone wants to play, creating a game...")
                g = GameServer(self.activePort)     # Creates game
                print(g.start())                           # Starts game
                self.activeGames.append(g)          # Adds the game a list

                # Tells the first person to start the game where it's being hosted
                outboundData["gameServer host"] = self.HOST
                outboundData["gameServer port"] = self.activePort

                # Keeps track of how many people have successfully connected
                self.connected += 1
                print("CONNECTOR: Keeping track of the number of people who have connected:", self.connected)  

                # Connects players to the new game
                for x in range(2):
                    address = self.waitingList[x]
                    # Packages up data and sends it back to the player
                    out = pickle.dumps(outboundData)
                    self.socket.sendto(out, address)
                    print("CONNECTOR: Sent data out to", address)
                
                self.waitingList = self.waitingList[2:]     # Removes players from waiting list once they're in a game

Connector()