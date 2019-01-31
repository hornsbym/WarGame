"""
 Author: Mitchell Hornsby
   File: Connector.py
Purpose: Creates a socket that constantly runs. It waits for players to connect 
         and then pairs them up in a new GameServer.
"""
from GameServer import GameServer
import socket 
import pickle
import os
import threading

class Connector (object):
    def __init__(self):
        """
        Starts the server.
        """
        # Socket info here:
        self.HOST = "142.93.118.50"
        self.PORT = 4999
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creates socket
        self.socket.bind((self.HOST,self.PORT))                           # Binds socket to local port

        # Keeps track of existing games here (only allow 10 for testing):
        self.activePort = 5000
        self.connected = 0

        print("CONNECTOR: listening at port", self.PORT)
        outboundData = {
            "gameServer host": None,
            "gameServer port": None
        }
        counter = 0 
        while True:
            print("CONNECTOR: Active port number is", self.activePort, "Iteration", counter)
            counter += 1

            print('CONNECTOR: Trying to recieve data...')
            inboundData = self.socket.recvfrom(1024)      # Gets bundle of data from clients
            data = inboundData[0]                         # Separates data from address

            print('CONNECTOR: Recieved data.')
            
            address = inboundData[1]                      # Separates address from data
            data = pickle.loads(data)                     # Unpickles data back into a python dict

            print("CONNECTOR:Message:", data, "From:",address)

            # Creates a new server here
            if self.connected == 0:
                print("CONNECTOR: Someone wants to play, creating a game...")
                g = GameServer(self.activePort)     # Creates game
                g.start()                           # Starts game

                # Tells the first person to start the game where it's being hosted
                outboundData["gameServer host"] = self.HOST
                outboundData["gameServer port"] = self.activePort

                # Keeps track of how many people have successfully connected
                self.connected += 1
                print("CONNECTOR: Keeping track of the number of people who have connected:", self.connected)  

            # Connects a player to an existing game if the latest game isn't full.
            # Keeps track of who needs to connect still, and which port hasn't been used yet.
            elif self.connected != 0:
                # Sends the player to the already existing game
                outboundData["gameServer host"] = self.HOST     
                outboundData["gameServer port"] = self.activePort

                # Moves to the next availible port and resets the counter for people to still be connected.
                self.activePort += 1
                self.connected = 0
                
            print('CONNECTOR: Trying to send data out...')

            # Packages up data and sends it back to the player
            out = pickle.dumps(outboundData)
            self.socket.sendto(out, address)
            print("CONNECTOR: Sent data out to", address)

Connector()