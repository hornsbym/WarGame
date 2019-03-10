import pygame as pg
import time
from screeninfo import get_monitors
import socket
import pickle
import random

import _modules.pygame_textinput as pygame_textinput
from _modules.Label import Label
from _modules.Panel import Panel
from _modules.Button import Button
from _modules.ImageButton import ImageButton
from _modules.Game import Game
from _modules.Square import Square
from _modules.Board import Board
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

        # Define fonts here so that they don't have to be defined in text labels.
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

        try:
            self.lobbyStage()       # Enters a lobby while waiting on another player
            self.setupStage()
            self.placementStage()
            self.battleStage()
        except:
            print("Closing socket...")
            self.socket.close()

        pg.quit()
        quit()
        self.socket.close()

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

        nameLabel = Label(namePlate, (x,y), self.NAMEPLATE_FONT, fontColor=fontColor)

        pg.draw.rect(self.display, (200,0,0), (x, y+nameLabel.getHeight(), self.displayWidth*.15, 5))   # Draws the red base for the healthbar
        pg.draw.rect(self.display,(0,200,0),(x, y+nameLabel.getHeight(), (self.displayWidth*.15)*(currentHealth/maxHealth), 5)) # Draws the green portion of the healthbar

        numberLabel = Label(str(currentHealth)+" / "+str(maxHealth), (x,y + nameLabel.getHeight() + 5), self.NAMEPLATE_FONT, fontColor=fontColor)

        nameLabel.show(self.display)
        numberLabel.show(self.display)

    def drawPlayerHealthbars(self, player, side, selectedTroop):
        """Accepts a Player object.
        Accepts a string of either "RIGHT" or "LEFT" specifying which side the troops should be located on.
        Accepts a Troop object specifying which troop is selected.
        Gets that player's Troops and displays all of their healthbars."""
        troops = player.getTroops()
        side = side.upper()

        if side == "LEFT":
            playerNameLabel = Label(player.getName(), (0,0), self.BIG_FONT)
            playerNameLabel.show(self.display)

            x = 5
            y = playerNameLabel.getHeight()+5

            for troop in troops:
                name = troop.getName()
                name = name[0].upper() + name[1:]
                level = str(troop.getLevel())

                # Changes selected troop name to purple and outlines
                if troop == selectedTroop:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y),True)
                else:
                    self.drawHealthbar("Lvl. "+level+" "+name,troop.getHealth(),troop.getMaxHealth(),(x,y))
                y += 45

        if side == "RIGHT":
            opponentNameLabel = Label(player.getName(), (self.displayWidth*.81, 0), self.BIG_FONT)
            opponentNameLabel.show(self.display)

            x = self.displayWidth*.81
            y = opponentNameLabel.getHeight()
            for troop in troops:
                name = troop.getName()
                name = name[0].upper() + name[1:]
                level = str(troop.getLevel())
                
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

        troopName = troop.getName()[0].upper()+troop.getName()[1:]

        # Create labels here:
        nameLabel = Label(troopName + " - Level "+ str(troop.getLevel()) + " (" + str(troop.getCooldownCounter()) + ")", (x+10,y+5), self.DEFAULT_FONT)
        healthLabel = Label(str(troop.getHealth())+" health", (x+5, y + nameLabel.getHeight() + 5), self.TROOPCARD_FONT)
        attackLabel = Label(str(troop.getAttack())+" attack", (x+5, y + nameLabel.getHeight() + healthLabel.getHeight() + 7), self.TROOPCARD_FONT)
        rangeLabel = Label(str(troop.getRange())+" attack range", (x+5, y + nameLabel.getHeight() + healthLabel.getHeight() + attackLabel.getHeight() + 9), self.TROOPCARD_FONT)
        speedLabel = Label(str(troop.getSpeed())+" speed", (x+5, y +  nameLabel.getHeight() + healthLabel.getHeight() + attackLabel.getHeight() + rangeLabel.getHeight() + 11), self.TROOPCARD_FONT)

        # Draws wireframe here:
        pg.draw.rect(self.display,(0,0,0), (x,y,self.displayWidth*.19, self.displayHeight*.24),2) 

        # Show labels here:
        nameLabel.show(self.display)
        healthLabel.show(self.display)
        attackLabel.show(self.display)
        rangeLabel.show(self.display)
        speedLabel.show(self.display)

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
        # Create subtract buttons here:
        rMinus = Button(" -", None, (10, 140), self.DEFAULT_FONT, bgColor=(225,0,75))
        aMinus = Button(" -", None, (10, 180), self.DEFAULT_FONT, bgColor=(225,0,75))
        sMinus = Button(" -", None, (10, 220), self.DEFAULT_FONT, bgColor=(225,0,75))
        hMinus = Button(" -", None, (10, 260), self.DEFAULT_FONT, bgColor=(225,0,75))

        # Create add buttons here:
        rPlus  = Button("+", None, (10 + rMinus.getWidth()+1, 140), self.DEFAULT_FONT, bgColor=(0,225,75))
        aPlus  = Button("+", None, (10 + aMinus.getWidth()+1, 180), self.DEFAULT_FONT, bgColor=(0,225,75))
        sPlus  = Button("+", None, (10 + sMinus.getWidth()+1, 220), self.DEFAULT_FONT, bgColor=(0,225,75))
        hPlus  = Button("+", None, (10 + hMinus.getWidth()+1, 260), self.DEFAULT_FONT, bgColor=(0,225,75))

        # Create cancel/apply buttons here:
        cancel = Button("Cancel", None, (10,300), self.DEFAULT_FONT, bgColor=(255, 75,75))
        apply  = Button("Apply", None, (10 + cancel.getWidth()+1,300), self.DEFAULT_FONT)

        # Gets troop's level
        level = troop.getLevel()

        # Keep track of upgrades
        r = 0
        a = 0
        s = 0
        h = 0
        total = 0

        upgradeRect = pg.Rect(0, 0, self.displayWidth*.2, self.displayHeight)

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


            # Create text labels here: 
            nameLabel = Label(troop.getName()[0].upper() + troop.getName()[1:] +" - "+str(tokens)+" tokens", (5, 85), self.DEFAULT_FONT)
            rangeLabel = Label("Range: "+str(troop.previewUpgrade("r",r)), (10 + rMinus.getWidth() + rPlus.getWidth() + 10, 140), self.DEFAULT_FONT)
            attackLabel = Label("Attack: "+str(troop.previewUpgrade("a",a)), (10 + aMinus.getWidth() + aPlus.getWidth() + 10, 180), self.DEFAULT_FONT)
            speedLabel = Label("Speed: "+str(troop.previewUpgrade("s",s)), (10 + sMinus.getWidth() + sPlus.getWidth() + 10, 220), self.DEFAULT_FONT)
            healthLabel = Label("Health: "+str(troop.previewUpgrade("h",h)), (10 + hMinus.getWidth() + hPlus.getWidth() + 10, 260), self.DEFAULT_FONT)

            # Show labels here:
            nameLabel.show(self.display)
            rangeLabel.show(self.display)
            attackLabel.show(self.display)
            speedLabel.show(self.display)
            healthLabel.show(self.display)

            # Show add/subtract buttons
            rPlus.show(self.display)
            rMinus.show(self.display)
            aPlus.show(self.display)
            aMinus.show(self.display)
            sPlus.show(self.display)
            sMinus.show(self.display)
            hPlus.show(self.display)
            hMinus.show(self.display)    

            # Show cancel/apply buttons here:
            apply.show(self.display)
            cancel.show(self.display)

            # Sum up upgrades here:
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
        waitingLabel = Label("Waiting for an opponent...",(self.displayWidth//2, self.displayHeight//2), self.DEFAULT_FONT)

        # Packages data to send to the server here as a python dictionary
        outboundData = { 
            "hello": "hello" 
            }
        print("Connected to connector.")
        # Try to communicate with server here:
        outboundData = pickle.dumps(outboundData)          # Packages outbound data into Pickle
        self.socket.sendto(outboundData, self.CONNECTOR)   # Sends Pickled data to connector
        
        while (True):
            try:
                inData = self.socket.recvfrom(1024)      # Gets back data. Will be a Pickle object.
                inData = inData[0]                       #### For some reason it's a tuple now?
                serverLocation = pickle.loads(inData)    # Turn Pickle back into dictionary.
                break
            except:
                self.display.fill((255,255,255))

                waitingLabel.show(self.display)
                pg.display.update()

                self.clock.tick(30)
                pass
        
        self.SERVER = (serverLocation["gameServer host"], serverLocation["gameServer port"])
        print("Connector pointed to", self.SERVER)

    ### -----| Update screen during main game loops below |----- ###

    def lobbyStage(self):
        """Waits for two players to join."""
        print("Starting lobby stage.")
        # Create buttons here:
        startButton = Button('start', 'start', (self.displayWidth//2, self.displayHeight//2), self.DEFAULT_FONT, bgColor=(0,0,0))
        pingButton = Button('ping', 'ping', (self.displayWidth//2, self.displayHeight//3), self.DEFAULT_FONT, (255,255,255), (50,100,0))
        closeButton = Button('close', 'close', (self.displayWidth//2, 2*self.displayHeight//3), self.DEFAULT_FONT, bgColor=(100,50,0))

        # Create labels here:
        stageLabel = Label("Lobby Stage", (0, self.displayHeight-40), self.DEFAULT_FONT, fontColor=(255,255,255), bgColor=(0,0,0))
        localPortLabel = Label(str(self.PORT), (0,0), self.DEFAULT_FONT, transparent=True)

        gameState = None

        command = ""
        while True:
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

            # Show labels here:
            stageLabel.show(self.display)
            localPortLabel.show(self.display)    # Displays the port in the window
            if gameState != None:
                # Displays banner at top of window:
                serverPortLabel = Label("Port "+str(gameState['connection']), (self.displayWidth//2,0), self.DEFAULT_FONT)
                serverPortLabel.move(((self.displayWidth//2)-(serverPortLabel.getWidth()//2), 0))
                serverPortLabel.show(self.display)

                # Represents player:
                playerLabel = Label("You (on port %i)"%self.PORT, (self.displayWidth//5,self.displayHeight//2), self.DEFAULT_FONT)
                playerLabel.move(((self.displayWidth//5)-(playerLabel.getWidth()//2), self.displayHeight//2))
                playerLabel.show(self.display)

                # Represents opponent:
                if gameState['opponentPort'] != None:
                    opponentLabel = Label("Other Player (on port %i)" % (gameState['opponentPort'][1]), (2*self.displayWidth//3, self.displayHeight//2), self.DEFAULT_FONT)
                    opponentLabel.show(self.display)

            # Show buttons here:
            pingButton.show(self.display)
            closeButton.show(self.display)
            if gameState != None:
                if gameState['ready'] == True:
                    startButton.show(self.display)

            # Packages data to be sent to the server as a python dictionary:
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
            # Keeps user in the waiting screen if they can't connect to server
            except Exception as e:
                print(e)

            # Allows users to interact with the server via buttons.
            if gameState != None:
                if gameState['start'] == True:
                    break

            # Resets command empty
            command = ""

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
        sizeVote = None
        submitted = False

        # Creates buttons here:
        smallButton      = Button("5x7", "SMALL", None, self.DEFAULT_FONT)
        mediumButton     = Button("7x9", "MEDIUM", None, self.DEFAULT_FONT)
        bigButton        = Button("10x12", "BIG", None, self.DEFAULT_FONT)
        hugeButton       = Button("12x15",  "HUGE", None, self.DEFAULT_FONT)
        randomSizeButton = Button("Random",  "RANDOM", None, self.DEFAULT_FONT)

        cornersButton   = Button("Corners", "CORNERS", None, self.DEFAULT_FONT)
        crossButton     = Button("Cross", "CROSS", None, self.DEFAULT_FONT)
        rowsButton      = Button("Rows", "ROWS", None, self.DEFAULT_FONT)
        dotsButton      = Button("Dots",  "DOTS", None, self.DEFAULT_FONT)
        randomMapButton = Button("Random",  "RANDOM", None, self.DEFAULT_FONT)

        changeNameButton = Button("Change name", None, (self.displayWidth//2,35), self.DEFAULT_FONT, bgColor=(100,100,100))
        submitButton = Button("SUBMIT", "SUBMIT", (self.displayWidth//2,self.displayHeight-40), self.DEFAULT_FONT, bgColor=(200,100,100))

        # Creates panels here:
        sizePanel = Panel((0, 0), (self.displayWidth//2, self.displayHeight))
        mapPanel = Panel((self.displayWidth//2, 0), (self.displayWidth - (self.displayWidth//2), self.displayHeight),)
        
        # Creates labels here:
        stageLabel = Label("Setup Stage", (0, self.displayHeight-40), self.DEFAULT_FONT, bgColor=(200, 75, 100))
        nameLabel = Label("", (0,0), self.DEFAULT_FONT)
        mapLabel = Label("", (0,30), self.DEFAULT_FONT)
        sizeLabel = Label("", (0,60), self.DEFAULT_FONT)

        # Adds buttons to labels here:
        sizePanel.addElement(smallButton, (sizePanel.getWidth()//2, sizePanel.getHeight()//6))
        sizePanel.addElement(mediumButton, (sizePanel.getWidth()//2, 2*sizePanel.getHeight()//6))
        sizePanel.addElement(bigButton, (sizePanel.getWidth()//2, 3*sizePanel.getHeight()//6))
        sizePanel.addElement(hugeButton, (sizePanel.getWidth()//2, 4*sizePanel.getHeight()//6))
        sizePanel.addElement(randomSizeButton, (sizePanel.getWidth()//2, 5*sizePanel.getHeight()//6))

        mapPanel.addElement(cornersButton, (mapPanel.getWidth()//2, mapPanel.getHeight()//6))
        mapPanel.addElement(crossButton, (mapPanel.getWidth()//2, 2*mapPanel.getHeight()//6))
        mapPanel.addElement(rowsButton, (mapPanel.getWidth()//2, 3*mapPanel.getHeight()//6))
        mapPanel.addElement(dotsButton, (mapPanel.getWidth()//2, 4*mapPanel.getHeight()//6))
        mapPanel.addElement(randomMapButton, (mapPanel.getWidth()//2, 5*mapPanel.getHeight()//6))

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
                        if mapVote != None and sizeVote != None:     # Only lets you submit once you've voted
                            command = submitButton.getValue()
                            name = nameInput.get_text()
                            submitButton.deactivate()
                            self.PLAYERNAME = name
                            submitted = True
                    
                    ### Map button clicks here:
                    if smallButton.isClicked(coords):
                        sizeVote = smallButton.getValue()
                    if bigButton.isClicked(coords):
                        sizeVote = bigButton.getValue()
                    if mediumButton.isClicked(coords):
                        sizeVote = mediumButton.getValue()
                    if hugeButton.isClicked(coords):
                        sizeVote = hugeButton.getValue()
                    if randomSizeButton.isClicked(coords):
                        sizeVote = randomSizeButton.getValue()

                    if cornersButton.isClicked(coords):
                        mapVote = cornersButton.getValue()
                    if crossButton.isClicked(coords):
                        mapVote = crossButton.getValue()
                    if dotsButton.isClicked(coords):
                        mapVote = dotsButton.getValue()
                    if rowsButton.isClicked(coords):
                        mapVote = rowsButton.getValue()
                    if randomMapButton.isClicked(coords):
                        mapVote = randomMapButton.getValue()

            self.display.fill((255,255,255))

            # Draws panels here:
            mapPanel.show(self.display)
            sizePanel.show(self.display)
            
            # Draws buttons for interacting with the server here:
            changeNameButton.show(self.display)
            if submitted == False:
                submitButton.show(self.display)

            # Updates labels here:
            nameLabel.updateText(name)
            mapLabel.updateText(mapVote)
            sizeLabel.updateText(sizeVote)

            # Draws labels here:
            stageLabel.show(self.display)
            nameLabel.show(self.display)
            mapLabel.show(self.display)
            sizeLabel.show(self.display)


            # Draw input area here:
            nameInput.update(events)
            self.display.blit(nameInput.get_surface(), (self.displayWidth//2,0))

            outboundData = { 
                'stage': 'setup',
                'command': command,
                'mapVote': (sizeVote, mapVote),
                'playerName': name
                }
            # Try to send data to GameServer here:
            outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle
            try:          
                self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server
                
                # SOCKET MUST BE BIG ENOUGH SO THAT THE GAME OBJECT CAN FIT:
                inData = self.socket.recvfrom(12000)      # Gets back data. Will be a Pickle object.
            except TimeoutError as t:
                print(t)
            except Exception as e:
                print(e)

            inData = inData[0]                        # (<data>, <address>)
            gameState = pickle.loads(inData)          # Turn Pickle back into dictionary.
                
            if gameState['ready'] == True:
                self.GAME = gameState['game']
                self.GAME.getBoard().setCenterCoords((self.displayWidth//2, self.displayHeight//2))
                self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)
                break       # Advances to next stage of the game.
    
            command = None

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

        # Creates Panels here:
        troopPanel = Panel((0, 0), (self.displayWidth*.2, self.displayHeight))
        bannerPanel = Panel((self.displayWidth*.2, 0), (self.displayWidth*.6, self.displayHeight*.15))
        opponentPanel = Panel((self.displayWidth*.8, 0), (self.displayWidth*.2, self.displayHeight)) 
        buttonPanel =Panel((self.displayWidth*.2, self.displayHeight*.85), (self.displayWidth*.6, self.displayHeight*.15))

        # Creates command buttons here (position is obsolete because it will be given
        # when the button is added to the button panel):
        startButton   = Button("start", "start", None, self.DEFAULT_FONT, active=False)
        addButton     = Button("add", "add", None, self.DEFAULT_FONT, bgColor=(150,0,150))
        upgradeButton = Button("upgrade", "upgrade", None, self.DEFAULT_FONT, bgColor=(200,150,0))
        switchButton  = Button("switch", "switch", None, self.DEFAULT_FONT)

        # Creates labels here:
        stageLabel = Label("Placement Stage", None, self.NAMEPLATE_FONT)
        commandLabel = Label("", None, self.DEFAULT_FONT)
        colorLabel = Label(self.PLAYEROBJECT.getColor(), None, self.DEFAULT_FONT)
        tokenLabel = Label("", None, self.DEFAULT_FONT)
        waitingLabel = Label("Waiting for opponent's turn to end...", None, self.DEFAULT_FONT, bgColor=(80, 150, 0), padding=(self.displayWidth*.3 , self.displayHeight*.1))

        # Adds buttons and labels to Panels here:
        opponentPanel.addElement(startButton, (opponentPanel.getWidth()/2 - (startButton.getWidth()//2), opponentPanel.getHeight() - startButton.getHeight() * 2))
        opponentPanel.addElement(addButton, (50, 2 * opponentPanel.getHeight() // 6 ))
        opponentPanel.addElement(upgradeButton, (50, 3 * opponentPanel.getHeight() // 6))
        opponentPanel.addElement(switchButton,  (50, 4 * opponentPanel.getHeight() // 6))

        bannerPanel.addElement(stageLabel, (0, 0))
        bannerPanel.addElement(commandLabel, (0, bannerPanel.getHeight() - commandLabel.getHeight()))
        bannerPanel.addElement(colorLabel, (0, bannerPanel.getHeight()//2 - colorLabel.getHeight()//2))
        bannerPanel.addElement(tokenLabel, ((bannerPanel.getWidth()//2) - (tokenLabel.getWidth()//2), bannerPanel.getHeight()//2))

        buttonPanel.addElement(waitingLabel, (buttonPanel.getWidth()//2 - waitingLabel.getWidth()//2, buttonPanel.getHeight()//2 - waitingLabel.getHeight()//2))

        # Holds stuff to send to the server here
        newTroop     = None
        previewTroop = None
        command      = None
        square       = None    # Is just a tuple of (x,y)
        upgrades     = (0,0,0,0)
        start        = False
        
        # Makes sure all troops are unique:
        lastSelectedTroop = None

        # Keeps track of which troop is being upgraded here:
        upgradeTroop = None

        # Keeps track of when the user can interact with server
        active = False
        while True:
            # Define the game board here... Just to simplify things.
            board = self.GAME.getBoard()
            player = self.GAME.getPlayerByName(self.PLAYERNAME)

            # Gives each troop a random ID number:
            randomID = random.randint(0,999999)

            tb = ImageButton(self.IMAGES['troop'], ("troop",1,1,25,1,100,(1,1),1,1,"t-%0.6d" % randomID), (self.displayWidth*.2 + (self.displayWidth*.6//6) , self.displayHeight*.9))
            rb = ImageButton(self.IMAGES['rifleman'], ("rifleman",1,3,50,1,80,(1,1),2,2,"r-%0.6d" % randomID), (self.displayWidth*.2 + 2*(self.displayWidth*.6//6) , self.displayHeight*.9)) 
            hb = ImageButton(self.IMAGES['healer'], ("healer",1,1,-30,1,70,(1,1),2,2,"h-%0.6d" % randomID), (self.displayWidth*.2 + 3*(self.displayWidth*.6//6) , self.displayHeight*.9))
            kb = ImageButton(self.IMAGES['knight'], ("knight",1,1,30,2,120,(1,1),1,2,"k-%0.6d" % randomID), (self.displayWidth*.2 + 4*(self.displayWidth*.6//6) , self.displayHeight*.9))
            sb = ImageButton(self.IMAGES['shield'], ("shield",1,1,10,1,175,(1,1),1,2,"s-%0.6d" % randomID), (self.displayWidth*.2 + 5*(self.displayWidth*.6//6) , self.displayHeight*.9))
            
            # Adds troop buttons to the button panel here:
            buttonPanel.addElement(tb, (buttonPanel.getWidth()//6 - tb.getWidth()//2, buttonPanel.getHeight()//2 - tb.getHeight()//2))
            buttonPanel.addElement(rb, (2 * buttonPanel.getWidth()//6 - rb.getWidth()//2, buttonPanel.getHeight()//2 - rb.getHeight()//2))
            buttonPanel.addElement(hb, (3 * buttonPanel.getWidth()//6 - hb.getWidth()//2, buttonPanel.getHeight()//2 - hb.getHeight()//2))
            buttonPanel.addElement(kb, (4 * buttonPanel.getWidth()//6 - kb.getWidth()//2,buttonPanel.getHeight()//2 - kb.getHeight()//2))
            buttonPanel.addElement(sb, (5 * buttonPanel.getWidth()//6 - sb.getWidth()//2, buttonPanel.getHeight()//2 - sb.getHeight()//2))

            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()              
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
            ### MUST BE BEFORE THE PANELS
            self.showBoard(board)

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

                waitingLabel.unHide()

            # Draws buttons for interacting with the game if it's the player's turn
            # Activates visible buttons
            if active == True and start == False and self.PLAYEROBJECT.getTokens() > 0:
                tb.activate()
                rb.activate()
                kb.activate()
                sb.activate()
                hb.activate()
                addButton.activate()
                upgradeButton.activate()
                switchButton.activate()

                waitingLabel.hide()

            # Updates labels here:
            commandLabel.updateText(command)
            tokenLabel.updateText(str(player.getTokens()) + " tokens left")

            # Draws information about the player/stage
            stageLabel.show(self.display)
            colorLabel.show(self.display)
            commandLabel.show(self.display)
            if active == True:
                tokenLabel.show(self.display)

            # Draws the info panels on the board here:
            troopPanel.show(self.display)
            bannerPanel.show(self.display)
            buttonPanel.show(self.display)
            opponentPanel.show(self.display)

            # Displays the preview troop card, if present
            if previewTroop != None:
                self.displayTroopCard(previewTroop, "right")

            # Displays the selected troop's info, if its present
            if newTroop != None:
                self.displayTroopCard(newTroop, "left")
            self.drawPlayerHealthbars(player, "left", previewTroop)

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
            outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle

            # Protocol for communicating to server when it's the player's turn:
            if active == True:
                counter = 0

                # Loops until the message is sent 
                while True:
                    try:      
                        if counter > 0:
                            print("Looping...", counter)
    
                        self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                        # SOCKET MUST BE BIG SO THAT THE GAME OBJECT CAN FIT
                        inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.

                        counter += 1
                        break
                    except TimeoutError as t:
                        print(t)
                    except Exception as e:
                        print(e)

            # Protocol for communicating to server when it's not the player's turn:
            if active != True:
                try:          
                    self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                    # SOCKET MUST BE BIG SO THAT THE GAME OBJECT CAN FIT
                    inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                except TimeoutError as t:
                    print(t)
                except Exception as e:
                    print(e)

            # Processes recieved data here:
            inData = inData[0]                       # (<data>, <address>)
            gameState = pickle.loads(inData)         # Turn Pickle back into dictionary.

            # Gets and sets up the board here
            self.GAME = gameState['game']
            board = self.GAME.getBoard()
            board.setCenterCoords((mapX_Value, mapY_Value))

            self.PLAYEROBJECT = self.GAME.getPlayerByName(self.PLAYERNAME)

            # When the server sends the signal, progresses game to next stage
            if gameState['start'] == True:
                break
            
            # Draws start button when the game is ready:
            if gameState['ready'] == True and start == False:
                startButton.show(self.display)
                startButton.activate()

            # Decides whether the player can send data to the server.
            if self.GAME.getActivePlayer() != self.PLAYERNAME:
                active = False
                if self.PLAYEROBJECT.getTokens() > 0:
                    waitingLabel.show(self.display)
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
        attackButton = Button("attack", "attack", (self.displayWidth*.85, 2*self.displayHeight//8), self.DEFAULT_FONT, bgColor = (0,50,200))
        moveButton = Button("move", "move", (self.displayWidth*.85, 3*self.displayHeight//8), self.DEFAULT_FONT, bgColor=(50,150,0))
        rotateButton = Button("rotate", "rotate", (self.displayWidth*.85, 4*self.displayHeight//8), self.DEFAULT_FONT, bgColor=(200,100,0))
        passButton = Button("pass", "pass", (self.displayWidth*.85, 5*self.displayHeight//8), self.DEFAULT_FONT, bgColor=(200,50,250))
        
        # Create text labels here:
        stageLabel = Label("Battle Stage", (self.displayWidth*.2, 0), self.NAMEPLATE_FONT)
        commandLabel = Label("", (0, 0), self.DEFAULT_FONT)
        colorLabel = Label(self.PLAYEROBJECT.getColor(), (self.displayWidth*.2, stageLabel.getHeight()), self.DEFAULT_FONT)
        moveLabel = Label("", (0, 0), self.DEFAULT_FONT)
        disconnectedLabel = Label('Not connected', (0, 0), self.DEFAULT_FONT)
        waitingLabel = Label("Waiting for opponent's turn to end...", (self.displayWidth//2, self.displayHeight-40), self.DEFAULT_FONT)
        squareLabel = Label("", (0, 0), self.DEFAULT_FONT)

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
            attackButton.show(self.display)
            moveButton.show(self.display)
            rotateButton.show(self.display)
            passButton.show(self.display)
            
            # Updates labels here:
            commandLabel.updateText(command)
            commandLabel.move((self.displayWidth*.2, (self.displayHeight*.15) - commandLabel.getHeight()))
            moveLabel.updateText(str(player.getMoves()) + " moves left")
            moveLabel.move((self.displayWidth//2 - (moveLabel.getWidth()/2), moveLabel.getHeight()))
            disconnectedLabel.move((self.displayWidth//2 - (disconnectedLabel.getWidth()/2), self.displayHeight//2))
            waitingLabel.move((self.displayWidth//2 - (waitingLabel.getWidth()//2), self.displayHeight-40))
            squareLabel.move((self.displayWidth - squareLabel.getWidth(), 0))
            squareLabel.updateText(str(square))

            # Draws information about the player/stage
            stageLabel.show(self.display)
            colorLabel.show(self.display)
            commandLabel.show(self.display)
            if active == True:
                moveLabel.show(self.display)
            if previewTroop != None:
                self.displayTroopCard(previewTroop, "right")
            if selectedTroop != None:
                self.displayTroopCard(selectedTroop, "left")
            if square != None:
                squareLabel.show(self.display)

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
            outboundData = pickle.dumps(outboundData)           # Packages outbound data into Pickle

            # Communicate with server when the active player:
            if active == True:
                # Send message until its recieved:
                while True:
                    try:
                        self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                        # SOCKET MUST BE BIG ENOUGH FOR THE GAME OBJECT TO FIT
                        inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                        break
                    except TimeoutError as t:
                        print(t)
                    except Exception as e:
                        print(e)
                        disconnectedLabel.show(self.display)

            # Communicate with server when NOT the active player:
            if active == False:
                try:
                    self.socket.sendto(outboundData, self.SERVER)       # Sends Pickled data to server

                    # SOCKET MUST BE BIG ENOUGH FOR THE GAME OBJECT TO FIT
                    inData = self.socket.recvfrom(12000)     # Gets back data. Will be a Pickle object.
                except TimeoutError as t:
                    print(t)
                except Exception as e:
                    print(e)
                    disconnectedLabel.show(self.display)

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
            except Exception as e:
                print(e)
                disconnectedLabel.show(self.display)

            # Decides whether the player can send data to the server.
            if self.GAME.getActivePlayer() != self.PLAYERNAME:
                active = False
                waitingLabel.show(self.display)
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