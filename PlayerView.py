import pygame as pg
import time
from screeninfo import get_monitors
import socket
import pickle

import _modules.pygame_textinput as pygame_textinput
from Game import Game
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
        # Pygame info
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

        ## Load images here so each square doesn't have to.
        self.IMAGES = {
            "barricade":pg.image.load("./_sprites/barricade.png").convert(),
            "bluehealer":pg.image.load("./_sprites/bluehealer.png").convert(),
            "blueknight":pg.image.load("./_sprites/blueknight.png").convert(),
            "bluerifleman":pg.image.load("./_sprites/bluerifleman.png").convert(),
            "blueshield":pg.image.load("./_sprites/blueshield.png").convert(),
            "bluesquare":pg.image.load("./_sprites/bluesquare.png").convert(),
            "bluetroop":pg.image.load("./_sprites/bluetroop.png").convert(),
            "healer":pg.image.load("./_sprites/healer.png").convert(),
            "knight":pg.image.load("./_sprites/knight.png").convert(),
            "redhealer":pg.image.load("./_sprites/redhealer.png").convert(),
            "redknight":pg.image.load("./_sprites/redknight.png").convert(),
            "redrifleman":pg.image.load("./_sprites/redrifleman.png").convert(),
            "redshield":pg.image.load("./_sprites/redshield.png").convert(),
            "redsquare":pg.image.load("./_sprites/redsquare.png").convert(),
            "redtroop":pg.image.load("./_sprites/redtroop.png").convert(),
            "rifleman":pg.image.load("./_sprites/rifleman.png").convert(),
            "shield":pg.image.load("./_sprites/shield.png").convert(),
            "square":pg.image.load("./_sprites/square.png").convert(),
            "troop":pg.image.load("./_sprites/troop.png").convert(),
            "wall":pg.image.load("./_sprites/wall.png").convert(),
        }

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
        
        # Contains the Game object, which has all important Game information
        # Game Object should never be changed, only looked at.
        self.GAME = None
        self.PLAYERNAME = None

        # Enters a lobby while waiting on another player
        self.lobbyStage()
        self.setupStage()
        self.placementStage()

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

    def canUpgrade(self, player ,troop):
        """Accepts a Player object.
        Accepts a Troop object.
        Checks to see if the player object has enough tokens to purchase a given troop. """
        player = self.playerObject
        tokens = player.getTokens()
        cost   = troop.getCost()
        if cost > tokens:
            return False
        else: 
            return True

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
                        command = startButton.getValue()    # Moves on to the next stage of the game

            self.display.fill((255,255,255))

            self.displayText("Lobby Stage",(0, self.displayHeight-40))
            
            if counter % 30 == 0:
                dots += "."
            if len(dots) > 3:
                dots = ""

            self.displayText(str(self.PORT),(0,0))    # Displays the port in the window

            # Packages data to send to the server here as a python dictionary
            outboundData = { "command": command }

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
                    if gameState['start'] == True:
                        break
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
        """Determines dimensions of the game board, players' names, and eventually the player's army.
        Return a tuple containing (Board, Player1, Player2)."""
        print("---- Initiating setup stage...")
        nameInput = pygame_textinput.TextInput("Player "+ str(self.PORT))

        name = nameInput.get_text()
        mapVote = None

        redButton     = CommandButton(("RED"), (3*self.displayWidth//7, self.displayHeight//5), (200, 50, 50))
        blueButton    = CommandButton(("BLUE"), (4*self.displayWidth//7, self.displayHeight//5), (50, 50, 200))

        testMap       = CommandButton("TEST",(2*self.displayWidth//5,self.displayHeight//2), (0,0,0))
        baseMap       = CommandButton("BASIC",(3*self.displayWidth//5, self.displayHeight//2), (0,0,0))
        bigMap        = CommandButton("BIG",(4*self.displayWidth//5, self.displayHeight//2), (0,0,0))

        changeNameButton = CommandButton("Change name",(self.displayWidth//2,35), (100,100,100))
        submitButton = CommandButton("SUBMIT", (self.displayWidth//2,self.displayHeight-40), (200,100,100))
        
        command = None
        while True:

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()

                    if changeNameButton.isClicked(coords):
                        name = nameInput.get_text()
                    if submitButton.isClicked(coords):
                        if mapVote != None:     # Only lets you submit once you've voted
                            command = submitButton.getValue()
                            self.PLAYERNAME = name
                    
                    if testMap.isClicked(coords):
                        mapVote = testMap.getValue()
                    if bigMap.isClicked(coords):
                        mapVote = bigMap.getValue()
                    if baseMap.isClicked(coords):
                        mapVote = baseMap.getValue()
                    

            self.display.fill((255,255,255))

            self.displayText("Setup Stage", (0, self.displayHeight-40))

            self.displayText("Name: "+name,(0,0))
            self.displayText("Map: "+str(mapVote), (0,30))

            redButton.showButton(self.display)
            blueButton.showButton(self.display)

            testMap.showButton(self.display)
            baseMap.showButton(self.display)
            bigMap.showButton(self.display)

            nameInput.update(events)
            self.display.blit(nameInput.get_surface(), (self.displayWidth//2,0))
            changeNameButton.showButton(self.display)

            submitButton.showButton(self.display)

            outboundData = { 
                'stage': 'setup',
                'command': command,
                'mapVote': mapVote,
                'playerName': name
                }
            # Try to communicate with server here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                # SOCKET MUST BE BIG SO THAT THE GAME OBJECT CAN FIT
                inData = self.socket.recvfrom(12000)      # Gets back data. Will be a Pickle object.
                inData = inData[0]                       # (<data>, <address>)
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.
                
                # Gets the set-up Game object back from the server
                if gameState['ready'] == True:
                    self.GAME = gameState['game']
                    self.GAME.getBoard().setCenterCoords((self.displayWidth//2, self.displayHeight//2))
                    break       # Advances to next stage of the game.
            except:
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))

            command = None

            pg.display.update()
            self.clock.tick(30)

    def placementStage(self):
        """Allows the player to place pieces on the game board."""
        print("--- Entering placement stage.")

        # Defines board here for simplification
        board = self.GAME.getBoard()
        board.setCenterCoords((self.displayWidth//2, self.displayHeight//2))

        # Static game widgets for player to interact with
        startButton   = CommandButton("start",(self.displayWidth-70, self.displayHeight-30), (0,0,0))

        addButton     = CommandButton("add", (board.getCoords()[0] + ((board.getWidth()* 32)/2) + 32, 2*self.displayHeight//6), (150,0,150))
        upgradeButton = CommandButton("upgrade",(board.getCoords()[0] + ((board.getWidth()* 32)/2) + 32, 3*self.displayHeight//6), (200,150,0))
        switchButton  = CommandButton("switch",(board.getCoords()[0] + ((board.getWidth()* 32)/2) + 32, 4*self.displayHeight//6), (0,0,0))

        tb = TroopButton(("troop",1,1,25,1,100,(1,1),1,1), (board.getCoords()[0] - (board.getWidth()//2 * 32)-150, 2*self.displayHeight//6))
        rb = TroopButton(("rifleman",1,3,50,1,80,(1,1),2,2), (board.getCoords()[0] - (board.getWidth()//2 * 32)-100, 2*self.displayHeight//6))
        hb = TroopButton(("healer",1,1,-30,1,70,(1,1),2,2), (board.getCoords()[0] - (board.getWidth()//2 * 32)-150, 3*self.displayHeight//6))    
        kb = TroopButton(("knight",1,1,30,2,120,(1,1),1,2), (board.getCoords()[0] - (board.getWidth()//2 * 32)-100, 3*self.displayHeight//6))
        sb = TroopButton(("shield",1,1,10,1,175,(1,1),1,2), (board.getCoords()[0] - (board.getWidth()//2 * 32)-100, 4*self.displayHeight//6))

        newTroop = None
        previewTroop = None
        command  = None
        square   = None    # Is just a tuple of (x,y)

        canSwitch = False
        switchPlayer   = False

        active = False

        command = None
        while True:
            # Define the game board here... Just to simplify things.
            board = self.GAME.getBoard()

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()               # Uncomment for finished game...
                    if board.isClicked(coords) == True:
                        square = board.getSquareCoords(coords)
                    else:
                        square = None
                        newTroop = None

                    # Checks the troop placement buttons
                    if tb.isClicked(coords) == True:
                        newTroop = Troop(tb.getValue())
                    if rb.isClicked(coords) == True:
                        newTroop = Troop(rb.getValue())
                    if sb.isClicked(coords) == True:
                        newTroop = Troop(sb.getValue())
                    if kb.isClicked(coords) == True:
                        newTroop = Troop(kb.getValue())
                    if hb.isClicked(coords) == True:
                        newTroop = Troop(hb.getValue())
                    
                    if addButton.isClicked(coords) == True:
                        command = addButton.getValue()
                    if upgradeButton.isClicked(coords) == True:
                        command = upgradeButton.getValue()
                    if switchButton.isClicked(coords) == True:
                        command = switchButton.getValue()

                # Allows users the option to choose troops and actions via keystrokes.
                if event.type == pg.KEYDOWN:
                    key = pg.key.get_pressed()
                    
                    # Troops
                    if key[pg.K_a]:
                        newTroop = Troop(tb.getValue())
                    if key[pg.K_r]:
                        newTroop = Troop(rb.getValue())
                    if key[pg.K_w]:
                        newTroop = Troop(sb.getValue())
                    if key[pg.K_e]:
                        newTroop = Troop(kb.getValue())
                    if key[pg.K_q]:
                        newTroop = Troop(hb.getValue())

                    # Actions
                    if key[pg.K_1]:
                        command = addButton.getValue()
                    if key[pg.K_2]:
                        command = upgradeButton.getValue()
                    if key[pg.K_0]:
                        command = switchButton.getValue()

            # Clear previous screen, so it can be updated again.
            self.display.fill((255,255,255))

            self.displayText(self.PLAYERNAME, (self.displayWidth//2, 0))
            self.displayText("Placement Stage", (0, self.displayHeight-40))

            board.showBoard(self.display, self.IMAGES)

            tb.showButton(self.display)
            rb.showButton(self.display)
            kb.showButton(self.display)
            sb.showButton(self.display)
            hb.showButton(self.display)

            addButton.showButton(self.display)
            upgradeButton.showButton(self.display)
            switchButton.showButton(self.display)

            # Sends blank data to server if it's not the player's turn
            if active == False:
                newTroop = None
                command = None
                square = None

            outboundData = { 
                "stage": 'placement',
                "newTroop": newTroop,
                "command": command,
                "square": square
                }
            # Try to communicate with server here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                # SOCKET MUST BE BIG SO THAT THE GAME OBJECT CAN FIT
                inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                inData = inData[0]                       # (<data>, <address>)
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.

                self.GAME = gameState['game']
                board = self.GAME.getBoard()
                board.setCenterCoords((self.displayWidth//2,self.displayHeight//2))

                # Decides whether the player can send data to the server.
                if self.GAME.getActivePlayer() != self.PLAYERNAME:
                    active = False
                    self.displayText("Waiting for opponent's turn to end...", (self.displayWidth//2, self.displayHeight-40))
                else:
                    active = True
            except:
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))

            pg.display.update()
            self.clock.tick(30)

        
PlayerView()