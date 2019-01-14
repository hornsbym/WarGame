import pygame as pg
import time
from screeninfo import get_monitors
import socket
import json

import _modules.pygame_textinput as pygame_textinput
from _modules.Square import Square
from _modules.Board import Board
from _modules.TroopButton import TroopButton
from _modules.CommandButton import CommandButton
from _modules.Player import Player
from _modules.Troop import Troop

class PlayerView(object):
    def __init__(self):
        # Get the screen dimensions here
        monitor = get_monitors()[0]
        width  = monitor.width-50
        height = monitor.height-200

        # Boilerplate pygame stuff:
        pg.init()
        self.clock = pg.time.Clock()
        self.displayWidth = width
        self.displayHeight = height
        self.display = pg.display.set_mode((self.displayWidth,self.displayHeight))
        self.display.fill((255,255,255))

        # Define fonts here so that they don't have to be defined in displayText function.
        self.DEFAULT_FONT   = pg.font.SysFont(None, 25)
        self.NAMEPLATE_FONT = pg.font.SysFont(None, 17)
        self.BIG_FONT       = pg.font.SysFont(None, 30)
        self.TROOPCARD_FONT = pg.font.SysFont(None, 20)

        # Socket stuff
        self.HOST = '127.0.0.1'
        self.PORT = 5001
        self.SERVER = ('127.0.0.1',5000)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while True:
            try:
                self.socket.bind((self.HOST,self.PORT))
                print("Connected to", self.HOST, "on port", self.PORT)
                break
            except:
                self.PORT += 1


        self.lobbyStage()

        pg.quit()
        quit()

    def displayText(self, string, tup=(0,0),font=None, fontColor=(0,0,0)):
        """Accepts a string and a tuple of x and y coordinates.
        X coordinate should be the first value in the tuple.
        Displays the string in at the designated coordinates."""
        if font == None:
            font = self.DEFAULT_FONT
        text = font.render(string, True, fontColor)
        self.display.blit(text, tup)

    def lobbyStage(self):
        """Waits for two players to join."""
        command = ""
        message = ""

        dots    = ""
        counter = 0

        messageButton = CommandButton("test",(self.displayWidth//2, self.displayHeight//2),(0,0,0))
        pingButton = CommandButton('ping', (self.displayWidth//2, self.displayHeight//3), (50,100,0))
        closeButton = CommandButton('close',(self.displayWidth//2, 2*self.displayHeight//3), (100,50,0))

        loop = True
        while (loop == True):
            # Gets all the events from the game window. A.k.a., do stuff here.

            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()

                    if messageButton.isClicked(coords):
                        command = messageButton.getValue() 
                    if pingButton.isClicked(coords):
                        command = pingButton.getValue() 
                    if closeButton.isClicked(coords):
                        command = closeButton.getValue() 

            self.display.fill((255,255,255))
            
            if counter % 30 == 0:
                dots += "."
            if len(dots) > 3:
                dots = ""
            
            if command == "close":
                message = "close"
            if command == "test":
                message = "Hello from port " + str(self.PORT)
            if command == "ping":
                message = "ping"

            self.displayText(str(self.PORT),(0,0))    # Displays the port in the window

            # Packages data to send to the server here as a python dictionary
            outData = {
                "command":command,"message":message
                }

            # Try to communicate with server here:
            try:          
                outData = json.dumps(outData)    # Packages outbound data into JSON
                self.socket.sendto(outData.encode('utf-8'), self.SERVER)
                
                inData = self.socket.recvfrom(1024)      # Gets back data. Will be a JSON object.
                inData = inData[0].decode('utf-8')                  # Decode data back into JSON.
                data = json.loads(inData)                         # Turn JSON back into dictionary.
                self.displayText(str(data['connection']),(self.displayWidth//2,0))


                # Allows users to interact with the server.
                messageButton.showButton(self.display)
                pingButton.showButton(self.display)
                closeButton.showButton(self.display)
            except:
                print("E")
                self.displayText("Waiting"+dots,(self.displayWidth//2,self.displayHeight//2))

            message = ""
            command = ""

            counter += 1

            pg.display.update()
            self.clock.tick(30)

PlayerView()