import socket 
import threading
from Game import Game

class GameServer(object):
    def __init__(self):

        self.HOST = "127.0.0.1"
        self.PORT = 5000

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST,self.PORT))

        self.play()

        self.socket.close()

    def play(self):
        print("UDP Server started at", self.PORT)
        g = Game()

        