import pygame as pg
import time
from screeninfo import get_monitors
import socket
import pickle

import _modules.pygame_textinput as pygame_textinput
from _modules.Square import Square
from _modules.Board import Board
from _modules.TroopButton import TroopButton
from _modules.CommandButton import CommandButton
from _modules.Player import Player
from _modules.Troop import Troop

def initializePygame():
    """Goes through boilerplate pygame stuff for initialization.
       Returns a tuple containing:
       [0] pygame display surface object
       [1] clock object
       [2] tuple of display dimensions"""
    # Get the screen dimensions here
    monitor = get_monitors()[0]
    width  = monitor.width-50
    height = monitor.height-200

    # Boilerplate pygame stuff:
    pg.init()
    clock = pg.time.Clock()
    displayWidth = width
    displayHeight = height
    return (pg.display.set_mode((displayWidth,displayHeight)), clock, (displayWidth, displayHeight))
    
class PlayerView(object):
    """Instantiates a server for a player. 
        Communicates with a game server to change the state of the game.
        Updates the screen to reflect changes to the game state."""
    def __init__(self):
        initialData = initializePygame()
        self.display = initialData[0]
        self.clock = initialData[1]
        self.displayWidth = initialData[2][0]
        self.displayHeight = initialData[2][1]
        self.display.fill((255,255,255))

        # Define fonts here so that they don't have to be defined in displayText function.
        self.DEFAULT_FONT   = pg.font.SysFont(None, 25)
        self.NAMEPLATE_FONT = pg.font.SysFont(None, 17)
        self.BIG_FONT       = pg.font.SysFont(None, 30)
        self.TROOPCARD_FONT = pg.font.SysFont(None, 20)

        # Socket variables
        self.HOST = '127.0.0.1'
        self.PORT = 5001
        self.SERVER = ('127.0.0.1',5000)

        # Create the socket to communicate with the game server through
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Finds an open port to bind the socket to
        while True:
            try:
                self.socket.bind((self.HOST,self.PORT))
                print("Connected to", self.HOST, "on port", self.PORT)

                # Sends the dimensions of the client's screen to the server upon first connection
                dimensions = { "dimensions":(self.displayWidth,self.displayHeight) }
                dimensions = pickle.dumps(dimensions)
                self.socket.sendto(dimensions, self.SERVER)
                break
            except:
                self.PORT += 1

        # Enters a lobby while waiting on another player
        self.lobbyStage()
        self.setupStage()

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

    def drawHealthbar(self, namePlate, currentHealth, maxHealth, coords, selected=False):
        """Accepts a string for the name and level of the troop.
        Accepts an integer representing the remaining health.
        Accepts an integer represending the total health pool.
        Accepts a tuple of form (x,y) for where the healthbar should be drawn.
        Accepts an optional boolean for whether the troop being represented is a selected troop."""
        x = coords[0]
        y = coords[1]   
        fontColor = (0,0,0)
        if selected == True:
            fontColor = (150,0,150)
            pg.draw.rect(self.display, (150,0,150), (x-3,y-15,maxHealth+6,37), 2) # Outlines selected troop
        pg.draw.rect(self.display, (200,0,0), (x,y,maxHealth,5))   # Draws the red base for the healthbar
        pg.draw.rect(self.display,(0,200,0),(x,y,currentHealth,5)) # Draws the green portion of the healthbar
        self.displayText(namePlate, (x,y-11),self.NAMEPLATE_FONT,fontColor)
        self.displayText(str(currentHealth)+" / "+str(maxHealth), (x,y+6),self.NAMEPLATE_FONT,fontColor) #Shows numbers

    def drawPlayerHealthbars(self, player, side, selectedTroop):
        """Accepts a Player object.
        Accepts a string of either "RIGHT" or "LEFT" specifying which side the troops should be located on.
        Accepts a Troop object specifying which troop is selected.
        Gets that player's Troops and displays all of their healthbars."""
        troops = player.getTroops()

        if side == "LEFT":
            # Finds the longest healthbar
            longest = 0
            for troop in troops:
                if troop.getMaxHealth() > longest:
                    longest = troop.getMaxHealth()
            x = 5
            y = 65

            self.displayText(player.getName(),(x,y-35), self.BIG_FONT)
            for troop in troops:
                name = troop.getName()
                name = name[0].upper() + name[1:]
                level = str(troop.getLevel())

                # Doesn't let the list of troops get beyond 75% of the screen height.
                if y > self.displayHeight*.75:    
                    x += longest+5
                    y = 50

                # Changes selected troop name to purple and outlines
                if troop == selectedTroop:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y),True)
                else:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y))
                y += 45

        if side == "RIGHT":
            # Finds the longest healthbar
            longest = 0
            for troop in troops:
                if troop.getMaxHealth() > longest:
                    longest = troop.getMaxHealth()

            x = self.displayWidth-(longest+5)
            y = 65

            self.displayText(player.getName(),(x,y-35), self.BIG_FONT)
            for troop in troops:
                name = troop.getName()
                name = name[0].upper() + name[1:]
                level = str(troop.getLevel())

                # Doesn't let the list of troops get beyond 75% of the screen height.
                if y > self.displayHeight*.75:    
                    x -= (longest+5)
                    y = 50
                
                # Changes selected troop name to purple and outlines
                if troop == selectedTroop:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y),True)
                else:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y))
                y += 45

    def displayTroopCard(self, troop, side):
        """Accepts a Troop object.
        Accepts a string of either "LEFT" or "RIGHT"."""
        if side == "LEFT":
            x = 5
            y = self.displayHeight * .76
        if side == "RIGHT":
            x = self.displayWidth *.78 - 5
            y = self.displayHeight * .76
        spacing = (self.displayHeight - y) * .2

        troopName = troop.getName()[0].upper()+troop.getName()[1:]

        pg.draw.rect(self.display,(0,0,0), (x,y,self.displayWidth*.22, self.displayHeight*.23),2) # Draws wireframe
        self.displayText(troopName + " - Level "+ str(troop.getLevel()) + " (" + str(troop.getCooldownCounter()) + ")", (x+10,y+5))
        self.displayText(str(troop.getHealth())+" health", (x+5,y+spacing), self.TROOPCARD_FONT)
        self.displayText(str(troop.getAttack())+" attack", (x+5,y+(2 * spacing)), self.TROOPCARD_FONT)
        self.displayText(str(troop.getRange())+" attack range", (x+5,y+(3 * spacing)), self.TROOPCARD_FONT)
        self.displayText(str(troop.getSpeed())+" speed", (x+5,y+(4 * spacing)), self.TROOPCARD_FONT)



    ### -----| Update screen during main game loops below |----- ###
    


    def lobbyStage(self):
        """Waits for two players to join."""
        command = ""

        dots    = ""
        counter = 0

        startButton = CommandButton('start', (self.displayWidth//2, self.displayHeight//2), (0,0,0))
        pingButton = CommandButton('ping', (self.displayWidth//2, self.displayHeight//3), (50,100,0))
        closeButton = CommandButton('close',(self.displayWidth//2, 2*self.displayHeight//3), (100,50,0))

        wait = True
        while (wait == True):
            # Gets all the events from the game window. A.k.a., do stuff here.
            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()

                    if pingButton.isClicked(coords):
                        command = pingButton.getValue() 
                    if closeButton.isClicked(coords):
                        command = closeButton.getValue() 
                    if startButton.isClicked(coords):
                        wait = False    # Moves on to the next stage of the game

            self.display.fill((255,255,255))
            
            if counter % 30 == 0:
                dots += "."
            if len(dots) > 3:
                dots = ""

            self.displayText(str(self.PORT),(0,0))    # Displays the port in the window

            # Packages data to send to the server here as a python dictionary
            outboundData = { "command":command }

            # Try to communicate with server here:
            try:          
                outboundData = pickle.dumps(outboundData)          # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER) # Sends Pickled data to server
                
                inData = self.socket.recvfrom(1024)      # Gets back data. Will be a Pickle object.
                inData = inData[0]                       #### For some reason it's a tuple now?
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.
                
                # Displays banner at top of window
                self.displayText("Port "+str(gameState['connection']),(self.displayWidth//2,0))
                self.displayText("You (on port %i)"%self.PORT, (self.displayWidth//5,self.displayHeight//2))

                # Allows users to interact with the server via buttons.
                try:
                    if gameState['ready'] == True:
                        startButton.showButton(self.display)
                    if gameState['opponentPort'] != None:
                        self.displayText("Other Player (on port %i)"%(gameState['opponentPort'][1]), (2*self.displayWidth//3, self.displayHeight//2))
                except:
                    pass
                pingButton.showButton(self.display)
                closeButton.showButton(self.display)


            # Keeps user in the waiting screen if they can't connect to server
            except:
                self.displayText("Waiting"+dots,(self.displayWidth//2,self.displayHeight//2))

            # Resets command empty
            command = ""
            
            # Counts the number of loops
            counter += 1

            pg.display.update()
            self.clock.tick(30)

    def setupStage(self):
        self.display.fill((255,255,255))

        while (loop = True):
            outboundData = { 'command': 'fetch' }
        



PlayerView()