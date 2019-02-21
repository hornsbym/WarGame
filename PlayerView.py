import pygame as pg
import time
from screeninfo import get_monitors
import socket
import pickle
import random

import _modules.pygame_textinput as pygame_textinput
from _modules.Game import Game
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
    return (pg.display.set_mode((displayWidth,displayHeight), pg.RESIZABLE), clock, (displayWidth, displayHeight))
    
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

        # # Saves the print statements to a local text file:
        # self.filepath = os.getcwd()
        # self.errorLogs = open(str(self.filepath)+"/_logs/"+ str(self.PORT) + ".txt", "a+")

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
            "wall":pg.image.load("./_sprites/wall.png").convert()}

        # Client socket variables
        self.HOST = None
        self.PORT = None

        # Connector socket variable
        # self.CONNECTOR = ('142.93.118.50', 4999)    # For the server
        self.CONNECTOR = ('127.0.0.1', 4999)    # For testing

        # Create the local socket to communicate with the game server through
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Finds an open port on the local machine to bind the socket to
        self.socket.bind(("",0))
        self.socket.settimeout(.75)
    
        self.HOST = self.socket.getsockname()[0]
        self.PORT = self.socket.getsockname()[1]
        print("Bound to", self.HOST, "on port", self.PORT)


        # Found a socket to establish on local machine, now connect to the server
        self.connect()

        # Makes first contact with the server.
        print("Sending initial message to server.")
        data = pickle.dumps({"command":""})
        self.socket.sendto(data, self.SERVER)
        print("Initial message recieved by server.")
        
        # Contains the Game object, which has all important Game information
        # Game Object should never be mutated, only accessed.
        self.GAME = None
        self.PLAYERNAME = None
        self.PLAYEROBJECT = None

        self.lobbyStage()       # Enters a lobby while waiting on another player
        self.setupStage()
        self.placementStage()
        self.battleStage()

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
        pg.draw.rect(self.display, (200,0,0), (x,y,self.displayWidth*.15,5))   # Draws the red base for the healthbar
        pg.draw.rect(self.display,(0,200,0),(x,y,(self.displayWidth*.15)*(currentHealth/maxHealth),5)) # Draws the green portion of the healthbar
        self.displayText(namePlate, (x,y-11),self.NAMEPLATE_FONT,fontColor)
        self.displayText(str(currentHealth)+" / "+str(maxHealth), (x,y+6),self.NAMEPLATE_FONT,fontColor) #Shows numbers

    def drawPlayerHealthbars(self, player, side, selectedTroop):
        """Accepts a Player object.
        Accepts a string of either "RIGHT" or "LEFT" specifying which side the troops should be located on.
        Accepts a Troop object specifying which troop is selected.
        Gets that player's Troops and displays all of their healthbars."""
        troops = player.getTroops()
        side = side.upper()

        if side == "LEFT":
            # Finds the longest healthbar
            longest = 0
            for troop in troops:
                if troop.getMaxHealth() > longest:
                    longest = troop.getMaxHealth()
            x = 5
            y = 65

            self.displayText(player.getName(),(5,5), self.BIG_FONT)
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
        side = side.upper()
        if side == "LEFT":
            x = 5
            y = self.displayHeight * .75
        if side == "RIGHT":
            x = self.displayWidth *.8 + 5
            y = self.displayHeight * .75
        spacing = (self.displayHeight - y) * .2

        troopName = troop.getName()[0].upper()+troop.getName()[1:]

        pg.draw.rect(self.display,(0,0,0), (x,y,self.displayWidth*.19, self.displayHeight*.24),2) # Draws wireframe
        self.displayText(troopName + " - Level "+ str(troop.getLevel()) + " (" + str(troop.getCooldownCounter()) + ")", (x+10,y+5))
        self.displayText(str(troop.getHealth())+" health", (x+5,y+spacing), self.TROOPCARD_FONT)
        self.displayText(str(troop.getAttack())+" attack", (x+5,y+(2 * spacing)), self.TROOPCARD_FONT)
        self.displayText(str(troop.getRange())+" attack range", (x+5,y+(3 * spacing)), self.TROOPCARD_FONT)
        self.displayText(str(troop.getSpeed())+" speed", (x+5,y+(4 * spacing)), self.TROOPCARD_FONT)

    def canUpgrade(self,troop):
        """Accepts a Troop object.
           Checks to see if the player object has enough tokens to purchase a given troop. """
        tokens = self.PLAYEROBJECT.getTokens()
        cost   = troop.getCost()
        if cost > tokens:
            return False
        else: 
            return True

    def getUpgradeStats(self, troop, tokens):
        """Accepts a Troop object to be upgraded.
           Accepts an Integer representing the player's tokens.
           Does not directly upgrade Troop. 
           Opens a new section of the screen to gather information about the upgrade.
           Aborts changes on "cancel", accepts on "accept".
           Returns a Tuple of Ints: (range, attack, speed, health)"""
        # Create add/subtract buttons
        rPlus  = CommandButton("+",(25, 140), (0,225,75), self.DEFAULT_FONT)
        rMinus = CommandButton(" -",(10, 140), (225,0,75), self.DEFAULT_FONT)
        aPlus  = CommandButton("+",(25, 180), (0,225,75), self.DEFAULT_FONT)
        aMinus = CommandButton(" -",(10, 180), (225,0,75), self.DEFAULT_FONT)
        sPlus  = CommandButton("+",(25, 220), (0,225,75), self.DEFAULT_FONT)
        sMinus = CommandButton(" -",(10, 220), (225,0,75), self.DEFAULT_FONT)
        hPlus  = CommandButton("+",(25, 260), (0,225,75), self.DEFAULT_FONT)
        hMinus = CommandButton(" -",(10, 260), (225,0,75), self.DEFAULT_FONT)

        apply  = CommandButton("Apply",(100,300),(0,0,0), self.DEFAULT_FONT)
        cancel = CommandButton("Cancel",(10,300), (255, 75,75), self.DEFAULT_FONT)

        # Gets troop's level
        level = troop.getLevel()

        # Keep track of upgrades
        r = 0
        a = 0
        s = 0
        h = 0
        total = 0

        upgradeRect = pg.Rect(0, 0, self.displayWidth//4, self.displayHeight)

        loop = True
        while (loop == True):
            # Gets all the events from the game window. A.k.a., do stuff here.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()
                    if cancel.isClicked(coords) == True:
                        loop = False
                        return (0,0,0,0)    # Sends back empty tuple upon cancelation 

                    # Only allows upgrades if the troop isn't maxed out (MAX LEVEL CURRENTLY 6):
                    if (total + level) <= 5:
                        # Adds/subtracts tokens
                        if rPlus.isClicked(coords) == True and tokens > 0:
                            tokens -= 1
                            r += 1
                        if rMinus.isClicked(coords) == True and r > 0:
                            tokens += 1
                            r -= 1
                        if aPlus.isClicked(coords) == True and tokens > 0:
                            tokens -= 1
                            a += 1
                        if aMinus.isClicked(coords) == True and a > 0:
                            tokens += 1
                            a -= 1
                        if sPlus.isClicked(coords) == True and tokens > 0:
                            tokens -= 1
                            s += 1
                        if sMinus.isClicked(coords) == True and s > 0:
                            tokens += 1
                            s -= 1
                        if hPlus.isClicked(coords) == True and tokens > 0:
                            tokens -= 1
                            h += 1
                        if hMinus.isClicked(coords) == True and h > 0:
                            tokens += 1
                            h -= 1
                    
                    if apply.isClicked(coords) == True:
                        return (r,a,s,h)
                
            self.display.fill((255,255,255))

            self.displayText(troop.getName()+" - "+str(tokens)+" tokens",(15,85))

            # Create text labels
            self.displayText("Range: "+str(troop.previewUpgrade("r",r)),(50,140))
            self.displayText("Attack: "+str(troop.previewUpgrade("a",a)),(50,180))
            self.displayText("Speed: "+str(troop.previewUpgrade("s",s)),(50,220))
            self.displayText("Health: "+str(troop.previewUpgrade("h",h)),(50,260))

            # Show add/subtract buttons
            rPlus.showButton(self.display)
            rMinus.showButton(self.display)
            aPlus.showButton(self.display)
            aMinus.showButton(self.display)
            sPlus.showButton(self.display)
            sMinus.showButton(self.display)
            hPlus.showButton(self.display)
            hMinus.showButton(self.display)    

            apply.showButton(self.display)
            cancel.showButton(self.display)

            total = r+a+s+h

            pg.display.update(upgradeRect)
            self.clock.tick(20)

    def showBoard(self, board):
        """Accepts a Board object.
           Blits the board and its squares onto the screen."""
        def showSquare(square):
            """Accepts a pygame Display object as an argument.
               Shows the square in that display.
               Handles rotations.
              Also sets the state coordinates of the square."""
            display = self.display
            img = self.IMAGES[square.getIcon()]
            coords = square.getCoords()

            # Handles rotations
            if square.getTroop() != None:
                orientation = square.getTroop().getOrientation()
                if orientation == (1,1):
                    img = pg.transform.rotate(img, 0)
                if orientation == (1,-1):
                    img = pg.transform.rotate(img, 90)
                if orientation == (-1,1):
                    img = pg.transform.rotate(img, -90)
                if orientation == (-1,-1):
                    img = pg.transform.rotate(img, 180)

            display.blit(img, (coords[0] + (square.getX() * 32), coords[1] + (square.getY() * 32)))
        
        squares = board.getSquares()

        for x in range(len(squares)):
            for y in range(len(squares[x])):
                square = squares[x][y]
                
                # Tells square what to look like and where to draw image
                showSquare(square)

    def animateMove(self, board, troop, previousSquare, orientation):
        """Accepts a Board object, a Troop object, a tuple of square values, and a tuple for the troop's orientation.
           Animate's the Troop's movement to the new square.
           Returns nothing."""
        # Tells the loop when to break:
        counter = 0   

        # Holds info relevent for animating here:
        troopID = troop.getID()
        troopSquare = self.findTroopSquareByID(board, troopID)
        display = self.display
        prevSquare = board.getSquares()[previousSquare[0]][previousSquare[1]]

        img = self.IMAGES[troopSquare.getIcon()]
        troopOrientation = orientation
        # Handles rotations
        if troopOrientation == (1,1):
            img = pg.transform.rotate(img, 0)
        if troopOrientation == (1,-1):
            img = pg.transform.rotate(img, 90)
        if troopOrientation == (-1,1):
            img = pg.transform.rotate(img, -90)
        if troopOrientation == (-1,-1):
            img = pg.transform.rotate(img, 180)

        prevSquareCoords = (prevSquare.getCoords()[0] + (prevSquare.getX() * 32), prevSquare.getCoords()[1] + (prevSquare.getY() * 32))
        troopSquareCoords = (troopSquare.getCoords()[0] + (troopSquare.getX() * 32), troopSquare.getCoords()[1] + (troopSquare.getY() * 32))

        xOffset = 0
        yOffset = 0
        animationFactor = .25

        # Hides the troop on the temporary animation board:
        troopSquare.hideIcon()

        
        while True:
            # Gets all the events from the game window. A.k.a., do stuff here.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
            if counter >= 15:
                break

            display.fill((255,255,255))
            
            self.showBoard(board)

            # Horizontal animation:
            if troopSquareCoords[0] != prevSquareCoords[0]:
                xDiff = troopSquareCoords[0] - (prevSquareCoords[0] + xOffset)
                xAnim = xDiff * animationFactor
                display.blit(img, (prevSquareCoords[0] + (xOffset + xAnim), troopSquareCoords[1]))
                xOffset += (xDiff * animationFactor)
            
            # Horizontal animation:
            if troopSquareCoords[1] != prevSquareCoords[1]:
                yDiff = troopSquareCoords[1] - (prevSquareCoords[1] + yOffset)
                yAnim = yDiff * animationFactor
                display.blit(img, (troopSquareCoords[0], prevSquareCoords[1] + (yOffset + yAnim)))
                yOffset += (yDiff * animationFactor)

            pg.display.update()
            self.clock.tick(35)

            counter += 1

    def findTroopSquareByID(self, board, troopID):
        """ Accepts a Board object.
            Accepts a Troop object's ID value (string).
            Iterates through the board's squares and finds the square that contains a troop 
            with the ID that matches the given ID.
            Returns a Square object.
        """
        for row in range(len(board.getSquares())):
            for column in range(len(board.getSquares()[row])):
                square = board.getSquares()[row][column]
                troop = square.getTroop()
                if troop != None:
                    if troop.getID() == troopID:
                        return square

    def connect(self):
        """Connects to the Connector, which then tells the view which port the game is on."""
        # Packages data to send to the server here as a python dictionary
        outboundData = { 
            "hello": "hello" 
            }
        print("Connected to connector server.")
        # Try to communicate with server here:
        outboundData = pickle.dumps(outboundData)          # Packages outbound data into Pickle
        self.socket.sendto(outboundData, self.CONNECTOR)   # Sends Pickled data to server
        
        inData = self.socket.recvfrom(1024)      # Gets back data. Will be a Pickle object.
        inData = inData[0]                       #### For some reason it's a tuple now?
        serverLocation = pickle.loads(inData)         # Turn Pickle back into dictionary.


        self.SERVER = (serverLocation["gameServer host"], serverLocation["gameServer port"])
        print("Connector pointed to", self.SERVER)

    ### -----| Update screen during main game loops below |----- ###

    def lobbyStage(self):
        """Waits for two players to join."""
        print("Starting lobby stage.")

        command = ""

        dots    = ""
        counter = 0

        startButton = CommandButton('start', (self.displayWidth//2, self.displayHeight//2), (0,0,0), self.DEFAULT_FONT)
        pingButton = CommandButton('ping', (self.displayWidth//2, self.displayHeight//3), (50,100,0), self.DEFAULT_FONT)
        closeButton = CommandButton('close',(self.displayWidth//2, 2*self.displayHeight//3), (100,50,0), self.DEFAULT_FONT)

        gameState = None

        wait = True
        while (wait == True):
            counter += 1
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
            outboundData = { 
                "stage": "lobby",
                "command": command
                }
            # Try to send data to the GameServer here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                pass

            # Try to recieve data from the GameServer here:
            try:
                inData = self.socket.recvfrom(1024)      # Gets back data. Will be a Pickle object.
                inData = inData[0]                       #### For some reason it's a tuple now?
                address = inData[1]
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.
            except TimeoutError as t:
                print(t)
                pass
            # Keeps user in the waiting screen if they can't connect to server
            except Exception as e:
                print(e)
                pass
                # self.displayText("Waiting"+dots,(self.displayWidth//2,self.displayHeight//2))

            if gameState != None:
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

        # Keeps track of player's information here:
        name = nameInput.get_text()
        mapVote = None
        submitted = False

        # Makes buttons here:
        redButton     = CommandButton(("RED"), (3*self.displayWidth//7, self.displayHeight//5), (200, 50, 50), self.DEFAULT_FONT)
        blueButton    = CommandButton(("BLUE"), (4*self.displayWidth//7, self.displayHeight//5), (50, 50, 200), self.DEFAULT_FONT)

        testMap       = CommandButton("TEST",(2*self.displayWidth//5,self.displayHeight//2), (0,0,0), self.DEFAULT_FONT)
        baseMap       = CommandButton("BASIC",(3*self.displayWidth//5, self.displayHeight//2), (0,0,0), self.DEFAULT_FONT)
        bigMap        = CommandButton("BIG",(4*self.displayWidth//5, self.displayHeight//2), (0,0,0), self.DEFAULT_FONT)
        hugeMap       = CommandButton("HUGE",(3*self.displayWidth//5, self.displayHeight//3), (0,0,0), self.DEFAULT_FONT)


        changeNameButton = CommandButton("Change name",(self.displayWidth//2,35), (100,100,100), self.DEFAULT_FONT)
        submitButton = CommandButton("SUBMIT", (self.displayWidth//2,self.displayHeight-40), (200,100,100), self.DEFAULT_FONT)
        
        reset = False
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
                            name = nameInput.get_text()
                            submitButton.deactivate()
                            self.PLAYERNAME = name
                            submitted = True
                    
                    ### Map button clicks here:
                    if testMap.isClicked(coords):
                        mapVote = testMap.getValue()
                    if bigMap.isClicked(coords):
                        mapVote = bigMap.getValue()
                    if baseMap.isClicked(coords):
                        mapVote = baseMap.getValue()
                    if hugeMap.isClicked(coords):
                        mapVote = hugeMap.getValue()
                    

            self.display.fill((255,255,255))
            
            # Draws buttons for interacting with the server
            redButton.showButton(self.display)
            blueButton.showButton(self.display)
            testMap.showButton(self.display)
            baseMap.showButton(self.display)
            bigMap.showButton(self.display)
            hugeMap.showButton(self.display)
            changeNameButton.showButton(self.display)
            if submitted == False:
                submitButton.showButton(self.display)

            # Draws information about the stage/player
            self.displayText("Setup Stage", (0, self.displayHeight-40))
            self.displayText("Name: "+name,(0,0))
            self.displayText("Map: "+str(mapVote), (0,30))

            # Draws input area
            nameInput.update(events)
            self.display.blit(nameInput.get_surface(), (self.displayWidth//2,0))

            outboundData = { 
                'stage': 'setup',
                'command': command,
                'mapVote': mapVote,
                'playerName': name
                }
            # Try to send data to GameServer here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server
                if command != None:
                    reset = True
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass    

            try:
                # SOCKET MUST BE BIG ENOUGH SO THAT THE GAME OBJECT CAN FIT
                inData = self.socket.recvfrom(12000)      # Gets back data. Will be a Pickle object.
                inData = inData[0]                        # (<data>, <address>)
                gameState = pickle.loads(inData)          # Turn Pickle back into dictionary.
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass
                

            if gameState['ready'] == True:
                self.GAME = gameState['game']
                self.GAME.getBoard().setCenterCoords((self.displayWidth//2, self.displayHeight//2))
                self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)
                break       # Advances to next stage of the game.
    
            if reset == True:
                command = None
                name = ""
                mapVote = None

            pg.display.update()
            self.clock.tick(30)
        self.display.fill((255,255,255))

    def placementStage(self):
        """Allows the player to place pieces on the game board."""
        print("--- Entering placement stage.")

        # Keep track of board view changes here:
        mapX_Value = self.displayWidth//2
        mapY_Value = self.displayHeight//2

        # Defines board here for simplification
        board = self.GAME.getBoard()
        board.setCenterCoords((mapX_Value, mapY_Value))

        # Define the global player object here
        self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)

        # Static game widgets for player to interact with
        startButton   = CommandButton("start",(self.displayWidth*.85, self.displayHeight-30), (0,0,0), self.DEFAULT_FONT, False)
        addButton     = CommandButton("add", (self.displayWidth*.85, 2*self.displayHeight//6), (150,0,150), self.DEFAULT_FONT)
        upgradeButton = CommandButton("upgrade",(self.displayWidth*.85, 3*self.displayHeight//6), (200,150,0), self.DEFAULT_FONT)
        switchButton  = CommandButton("switch",(self.displayWidth*.85, 4*self.displayHeight//6), (0,0,0), self.DEFAULT_FONT)

        upgradeTroop = None

        # Holds stuff to send to the server here
        newTroop     = None
        previewTroop = None
        command      = None
        square       = None    # Is just a tuple of (x,y)
        upgrades     = (0,0,0,0)
        start        = False
        
        # Makes sure all troops are unique:
        lastSelectedTroop = None
        
        # Indicates whether the above information should be reset.
        reset = False

        # Creates info pane sections here:
        troopPane = pg.Rect(0, 0, self.displayWidth*.2, self.displayHeight)
        bannerPane = pg.Rect(self.displayWidth*.2, 0, self.displayWidth*.6, self.displayHeight*.15)
        opponentPane = pg.Rect(self.displayWidth*.8, 0, self.displayWidth*.2, self.displayHeight)
        buttonPane = pg.Rect(self.displayWidth*.2, self.displayHeight*.85, self.displayWidth*.6, self.displayHeight*.15)

        # Keeps track of when the user can interact with server
        active = False
        while True:
            ##### Handles any changes to screen size here: 
            ##### NEED TO DEFINE WIDGET POSITIONS WITHIN WHILE LOOP
            # print("Resizing from (%i, %i)..." % (self.displayWidth, self.displayHeight))
            # self.displayWidth, self.displayHeight = pg.display.get_surface().get_size()
            # print("...to (%i, %i)" % (self.displayWidth, self.displayHeight))

            # Define the game board here... Just to simplify things.
            board = self.GAME.getBoard()
            player = self.GAME.getPlayerByName(self.PLAYERNAME)

            # Gives each troop a random ID number:
            randomID = random.randint(0,999999)
            tb = TroopButton(("troop",1,1,25,1,100,(1,1),1,1,"t-%0.6d" % randomID), (self.displayWidth*.2 + (self.displayWidth*.6//6) , self.displayHeight*.9) )
            rb = TroopButton(("rifleman",1,3,50,1,80,(1,1),2,2,"r-%0.6d" % randomID), (self.displayWidth*.2 + 2*(self.displayWidth*.6//6) , self.displayHeight*.9) )
            hb = TroopButton(("healer",1,1,-30,1,70,(1,1),2,2,"h-%0.6d" % randomID), (self.displayWidth*.2 + 3*(self.displayWidth*.6//6) , self.displayHeight*.9) )    
            kb = TroopButton(("knight",1,1,30,2,120,(1,1),1,2,"k-%0.6d" % randomID), (self.displayWidth*.2 + 4*(self.displayWidth*.6//6) , self.displayHeight*.9))
            sb = TroopButton(("shield",1,1,10,1,175,(1,1),1,2,"s-%0.6d" % randomID), (self.displayWidth*.2 + 5*(self.displayWidth*.6//6) , self.displayHeight*.9))

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
                        lastSelectedTroop = None

                    # Checks the troop placement buttons
                    if tb.isClicked(coords) == True or lastSelectedTroop == "troop":
                        newTroop = Troop(tb.getValue())
                        lastSelectedTroop = "troop"
                        
                    if rb.isClicked(coords) == True or lastSelectedTroop == "rifleman":
                        newTroop = Troop(rb.getValue())
                        lastSelectedTroop = "rifleman"
                    if sb.isClicked(coords) == True or lastSelectedTroop == "shield":
                        newTroop = Troop(sb.getValue())
                        lastSelectedTroop = "shield"
                    if kb.isClicked(coords) == True or lastSelectedTroop == "knight":
                        newTroop = Troop(kb.getValue())
                        lastSelectedTroop = "knight"
                    if hb.isClicked(coords) == True or lastSelectedTroop == "healer":
                        newTroop = Troop(hb.getValue())
                        lastSelectedTroop = "healer"

                    if addButton.isClicked(coords) == True:
                        command = addButton.getValue()
                    if upgradeButton.isClicked(coords) == True:
                        command = upgradeButton.getValue()
                    if switchButton.isClicked(coords) == True:
                        command = switchButton.getValue()
                    if startButton.isClicked(coords) == True:
                        startButton.deactivate()
                        start = True

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

                    # Actions:
                    if key[pg.K_1]:
                        command = addButton.getValue()
                    if key[pg.K_2]:
                        command = upgradeButton.getValue()
                    if key[pg.K_0]:
                        command = switchButton.getValue()

                    # Changes map view:
                    if key[pg.K_LEFT]:
                        mapX_Value -= 25
                    if key[pg.K_RIGHT]:
                        mapX_Value += 25
                    if key[pg.K_UP]:
                        mapY_Value -= 25
                    if key[pg.K_DOWN]:
                        mapY_Value += 25


            # Clear previous screen, so it can be updated again.
            self.display.fill((160,160,160))

            # Draws the game board 
            ### MUST BE BEFORE THE PANES
            self.showBoard(board)

            # Draws the info panes on the board here:
            pg.draw.rect(self.display, (255,255,255), troopPane)
            pg.draw.rect(self.display, (255,255,255), bannerPane)
            pg.draw.rect(self.display, (255,255,255), opponentPane)
            pg.draw.rect(self.display, (255,255,255), buttonPane)

            ## Deactivates buttons if it's not the player's turn.
            if active == False or start == True:
                tb.deactivate()
                rb.deactivate()
                kb.deactivate()
                sb.deactivate()
                hb.deactivate()
                addButton.deactivate()
                upgradeButton.deactivate()
                switchButton.deactivate()

            # Draws buttons for interacting with the game if it's the player's turn
            # Activates visible buttons
            if active == True and start == False:
                tb.showButton(self.display)
                rb.showButton(self.display)
                kb.showButton(self.display)
                sb.showButton(self.display)
                hb.showButton(self.display)
                addButton.showButton(self.display)
                upgradeButton.showButton(self.display)
                switchButton.showButton(self.display)

                tb.activate()
                rb.activate()
                kb.activate()
                sb.activate()
                hb.activate()
                addButton.activate()
                upgradeButton.activate()
                switchButton.activate()


            # bannerPane = pg.Rect(self.displayWidth*.2, 0, self.displayWidth*.6, self.displayHeight*.15)
            # Draws information about the player/stage
            self.displayText("Placement Stage", (self.displayWidth*.2,0), font=self.NAMEPLATE_FONT)
            self.displayText(command, (self.displayWidth*.2, self.displayHeight*.15 - 25))
            self.displayText(player.getColor() + " team", (self.displayWidth*.2, 25))
            if active == True:
                self.displayText(str(player.getTokens()) + " tokens left", (self.displayWidth//2, 25))
            if previewTroop != None:
                self.displayTroopCard(previewTroop, "right")


            # Displays the selected troop's info, if its present
            if newTroop != None:
                self.displayTroopCard(newTroop, "left")
            self.drawPlayerHealthbars(player, "left", None)


            # Gathers one of the other team's troops info
            if square != None:
                troop = board.getSquareValue(square)
                if troop != None:
                    if troop.getTeam() != player:
                        previewTroop = troop
            
                
            if command == "upgrade":
                if square != None:
                    upgradeTroop = board.getSquareValue(square)   
                    upgrades = self.getUpgradeStats(upgradeTroop, player.getTokens())

            # Sends blank data to server if it's not the player's turn
            if active == False:
                newTroop = None
                command = None

            outboundData = { 
                "stage": 'placement',
                "newTroop": newTroop,
                "command": command,
                "square": square,
                "upgrades": upgrades,
                "start": start
                }
            # Try to communicate with server here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                if command == 'switch':
                    reset = True

            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass
            
            try:
                # SOCKET MUST BE BIG SO THAT THE GAME OBJECT CAN FIT
                inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                inData = inData[0]                       # (<data>, <address>)
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.

                # Gets and sets up the board here
                self.GAME = gameState['game']
                board = self.GAME.getBoard()
                board.setCenterCoords((mapX_Value, mapY_Value))

                self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass

            # When the server sends the signal, progresses to next stage
            if gameState['start'] == True:
                break

            if gameState['ready'] == True and start == False:
                startButton.showButton(self.display)
                startButton.activate()

            # try:
            # Decides whether the player can send data to the server.
            if self.GAME.getActivePlayer() != self.PLAYERNAME:
                active = False
                if self.PLAYEROBJECT.getTokens() > 0:
                    self.displayText("Waiting for opponent's turn to end...", (self.displayWidth//2, self.displayHeight-40))
            else:
                active = True

            if active == True:
                upgrades = (0,0,0,0)
                square = None

            pg.display.update()
            self.clock.tick(30)

    def battleStage(self):
        """Allows the player to place pieces on the game board."""
        print("-- Entering battle stage.")
        # Keep track of board view changes here:
        mapX_Value = self.displayWidth//2
        mapY_Value = self.displayHeight//2

        # Defines board here for simplification
        board = self.GAME.getBoard()
        board.setCenterCoords((mapX_Value, mapY_Value))

        # Define the global player object here
        self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)

        # Creates info pane sections here:
        troopPane = pg.Rect(0, 0, self.displayWidth*.2, self.displayHeight)
        bannerPane = pg.Rect(self.displayWidth*.2, 0, self.displayWidth*.6, self.displayHeight*.15)
        opponentPane = pg.Rect(self.displayWidth*.8, 0, self.displayWidth*.2, self.displayHeight)
        bufferPane = pg.Rect(self.displayWidth*.2, self.displayHeight*.85, self.displayWidth*.6, self.displayHeight*.15)

        # Static game widgets for player to interact with
        attackButton = CommandButton("attack", (self.displayWidth*.85, 2*self.displayHeight//8), (0,50,200), self.DEFAULT_FONT)
        moveButton = CommandButton("move", (self.displayWidth*.85, 3*self.displayHeight//8), (50,150,0), self.DEFAULT_FONT)
        rotateButton = CommandButton("rotate", (self.displayWidth*.85, 4*self.displayHeight//8), (200,100,0), self.DEFAULT_FONT)
        passButton = CommandButton("pass", (self.displayWidth*.85, 5*self.displayHeight//8), (200,50,250), self.DEFAULT_FONT)
        
        # Holds stuff to display on the player's screen here
        previewTroop = None
        selectedTroop = None

        # For animating troop movements:
        troopPreviousSquare = None

        # Holds stuff to send to the server here
        command    = None
        square     = None    # Is just a tuple of (x,y)
        moveSquare = None

        # Keeps track of when the user can interact with server
        active = False

        while True:
            # Define the game board here... Just to simplify things.
            board = self.GAME.getBoard()
            player = self.GAME.getPlayerByName(self.PLAYERNAME)

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()               # Uncomment for finished game...
                    if board.isClicked(coords) == True:
                        if command == "move" and square != None:
                            moveSquare = board.getSquareCoords(coords)   # Saves the coords of the second click for moves
                        else:
                            square = board.getSquareCoords(coords)
                    else:
                        selectedTroop = None
                        previewTroop  = None
                        square        = None

                    if attackButton.isClicked(coords) == True:
                        command = attackButton.getValue()
                    elif moveButton.isClicked(coords) == True:
                        command = moveButton.getValue()
                    elif rotateButton.isClicked(coords) == True:
                        command = rotateButton.getValue()
                    elif passButton.isClicked(coords) == True:
                        command = passButton.getValue()
                    else:
                        if board.isClicked(coords) == False:
                            command = None

                # Allows users the option to choose troops and actions via keystrokes.
                if event.type == pg.KEYDOWN:
                    key = pg.key.get_pressed()
                    
                    # Changes map view:
                    if key[pg.K_LEFT]:
                        mapX_Value -= 25
                    if key[pg.K_RIGHT]:
                        mapX_Value += 25
                    if key[pg.K_UP]:
                        mapY_Value -= 25
                    if key[pg.K_DOWN]:
                        mapY_Value += 25


            # Clear previous screen, so it can be updated again.
            self.display.fill((160,160,160))

            # Draws the game board
            self.showBoard(board)

            # Draws the info panes on the board here:
            pg.draw.rect(self.display, (255,255,255), troopPane)
            pg.draw.rect(self.display, (255,255,255), bannerPane)
            pg.draw.rect(self.display, (255,255,255), opponentPane)
            pg.draw.rect(self.display, (255,255,255), bufferPane)

            # Draws buttons for interacting with the game
            attackButton.showButton(self.display)
            moveButton.showButton(self.display)
            rotateButton.showButton(self.display)
            passButton.showButton(self.display)

            # Draws information about the player/stage
            self.displayText("Battle Stage", (self.displayWidth*.2,0), font=self.NAMEPLATE_FONT)
            self.displayText(player.getColor() + " team", (self.displayWidth*.2, 25))
            self.displayText(command, (self.displayWidth*.2, self.displayHeight*.15 - 25))
            if active == True:
                self.displayText(str(player.getMoves()) + " moves left", (self.displayWidth//2, 25))
            if previewTroop != None:
                self.displayTroopCard(previewTroop, "right")
            if selectedTroop != None:
                self.displayTroopCard(selectedTroop, "left")
            if square != None:
                self.displayText(str(square),(self.displayWidth-50, 0))

            # Displays the selected troop's info, if its present
            self.drawPlayerHealthbars(player, "left", None)

            # Gathers one of the other team's troops info
            if square != None:
                troop = board.getSquareValue(square)
                if troop != None:
                    troopPreviousSquare = square
                    if troop.getTeam() != player:
                        previewTroop = troop
                    if troop.getTeam() == player:
                        selectedTroop = troop
            
            # Sends blank data to server if it's not the player's turn
            if active == False:
                command = None
                square = None

            outboundData = { 
                "stage": 'battle',
                "command": command,
                "square": square,
                "moveSquare": moveSquare
                }
            # Try to send data to the GameServer here:
            try:          
                outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass

            try:
                # SOCKET MUST BE BIG ENOUGH FOR THE GAME OBJECT TO FIT
                inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                inData = inData[0]                       # (<data>, <address>)
                gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.

                # Gets and sets up the board here
                self.GAME = gameState['game']
                board = self.GAME.getBoard()
                board.setCenterCoords((mapX_Value, mapY_Value))

                self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)
            except TimeoutError as t:
                print(t)
                pass
            except Exception as e:
                print(e)
                self.displayText('Not connected', (self.displayWidth//2, self.displayHeight//2))
                pass

            # Decides whether the player can send data to the server.
            if self.GAME.getActivePlayer() != self.PLAYERNAME:
                active = False
                self.displayText("Waiting for opponent's turn to end...", (self.displayWidth//2, self.displayHeight-40))
            else:
                active = True

            # Checks whether animation is necessary:
            if selectedTroop != None and command == "move":
                currentTroopSquare = self.findTroopSquareByID(board, selectedTroop.getID())
                currentTroopLocation = (currentTroopSquare.getX(), currentTroopSquare.getY())

                if currentTroopLocation != troopPreviousSquare:
                    troopOrientation = self.findTroopSquareByID(board, selectedTroop.getID()).getTroop().getOrientation()
                    self.animateMove(board, selectedTroop, troopPreviousSquare, troopOrientation)
                    troopPreviousSquare = currentTroopLocation
                

            if active == True:
                if command != "move":       # Doesn't override 'square' on moves because  
                    square = None           # you need to send two squares at the same time.
                if command == "move" and moveSquare != None:
                    moveSquare = None
                    square = None
                
            if command == "pass":
                command = None
                        
            pg.display.update()
            self.clock.tick(30)

PlayerView()