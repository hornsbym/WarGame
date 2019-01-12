import socket
import pygame as pg

class Client(object):
    def __init__(self):
        pg.init()
        self.HOST = '127.0.0.1'
        self.PORT = 5001
        self.SERVER = ('127.0.0.1',5000)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.HOST,self.PORT))

        print("Connecting to port", self.PORT)
        while True:
            # Get information from server here.
            data, address = self.s.recvfrom(1024)
            

        self.s.close()

    
