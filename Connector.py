"""
 Author: Mitchell Hornsby
   File: Connector.py
Purpose: Creates a socket that constantly runs. It waits for players to connect 
         and then pairs them up in a new GameServer.
"""
import socket 
import pickle
import subprocess

from GameServer import GameServer

class Connector (object):
    def __init__(self):
        """
        Starts the server.
        """
        print("Connector 1")
        # Socket info here:
        self.HOST = "127.0.0.1"
        self.PORT = 4999
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creates socket
        self.socket.bind((self.HOST,self.PORT))                           # Binds socket to local port

        # Keeps track of existing games here (only allow 10 for testing):
        self.waitingGames = []

        print("Connector listening at port", self.PORT)
        outboundData = {
            "gameServer host": None,
            "gameServer port": None
        }
        while True:
            try:
                inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
                data = inboundData[0]                         # Separates data from address
                address = inboundData[1]                      # Separates address from data
                data = pickle.loads(data)                     # Unpickles data back into a python dict

                # Creates the first server here
                if len(self.waitingGames) == 0 and data['hello'] == 'hello':
                    print("Data:", data)
                    print("A")
                    # g = GameServer(self.HOST, self.PORT+len(self.waitingGames)+1)
                    # subprocess.run("python GameServer.py")
                    print("A")
                    # Creates and keeps track of a new game server here:
                    print("A")
                    self.waitingGames.append((self.HOST, self.PORT+len(self.waitingGames)+1))
                    print("A")

                    # Informs the player where the new game is located:
                    outboundData["gameServer host"] = self.HOST
                    outboundData["gameServer port"] = self.PORT

                else:
                    latestGame = self.waitingGames[len(self.waitingGames)]

                    # Connects a player to an existing game if the latest game isn't full
                    if latestGame.isServerFull() == False:
                        outboundData["gameServer host"] = latestGame[0]
                        outboundData["gameServer port"] = latestGame.getServerPort()[1]

                        self.waitingGames.pop(latestGame)
                    

                # Packages up data and sends it back to the player
                out = pickle.dumps(outboundData)
                self.socket.sendto(out, address)
            except:
                pass

Connector()