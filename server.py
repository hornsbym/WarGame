import socket 
import json
from Game import Game


class GameServer(object):
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 5000

        self.clients = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST,self.PORT))

        print("UDP Server started at", self.PORT)

        # Organizes outbound data into a dict
        gameState = {
            "connection":"Communicating with port "+str(self.PORT)
            }
        while True:
            data, address = self.socket.recvfrom(1024)      # Gets data from clients; will be a JSON
            inData = data.decode('utf-8')                   # Decodes data from clients
            inData = json.loads(inData)

            if address not in self.clients:
                self.clients.append(address)                # Keep track of addresses of clients

            if inData != "":
                print(inData)                               # Print out non-trivial data from clients
                if inData['command'] == "ping":
                    print("Client list:",self.clients)
                    pass
                if inData['command'] == "close":
                    break
                if inData['command']== 'test':
                    gameState['connection']= inData['message']
                    for address in self.clients:            # Loops through all clients and sends data to all of them
                        outData = json.dumps(gameState)     # Packages data as JSON
                        self.socket.sendto(outData.encode('utf-8'),address)
            
            # Packages up data and sends it back to the client
            outData = json.dumps(gameState)
            data = outData.encode('utf-8')

            self.socket.sendto(data, address)

        self.socket.close()



    # def play(self):
    #     print("UDP Server started at", self.PORT)
    #     g = Game()

GameServer()