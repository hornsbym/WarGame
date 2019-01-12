import pygame as pg
import time
from screeninfo import get_monitors

# from server import GameServer

import _modules.pygame_textinput as pygame_textinput
from _modules.Square import Square
from _modules.Board import Board
from _modules.TroopButton import TroopButton
from _modules.CommandButton import CommandButton
from _modules.Player import Player
from _modules.Troop import Troop

import _maps.basic_map as basic
import _maps.test_map as test
import _maps.big_map as big

class Game(object):
    """Class containing ALL pertinent Game information.
       Contains the board and the players, and displays information to the self.display."""
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

        self.lobbyStage()
        emptyBoard = self.setupStage()
        startingBoard = self.placementStage(emptyBoard)
        self.battleStage(startingBoard)

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

    def canUpgrade(self, player,troop):
        """Accepts a Player object.
        Accepts a Troop object.
        Checks to see if the player object has enough tokens to purchase a given troop. """
        tokens = player.getTokens()
        cost   = troop.getCost()
        if cost > tokens:
            return False
        else: 
            return True

    def upgrade(self, troop, tokens):
        """Accepts a troop object.
        Accepts an integer representing spendable tokens.
        Accepts a tuple of coordinates where the player has clicked.
        Displays the troop's stats and allows the user to see what
        happens when they add upgrade points to certain attributes.
        Upgrades the troop when user presses "apply".
        Returns integer representing how many tokens were spent."""
        STARTING_TOKENS = tokens
        tokens = tokens

        # Create add/subtract button
        rPlus  = CommandButton("+",(25, 140), (0,225,75))
        rMinus = CommandButton(" -",(10, 140), (225,0,75))
        aPlus  = CommandButton("+",(25, 180), (0,225,75))
        aMinus = CommandButton(" -",(10, 180), (225,0,75))
        sPlus  = CommandButton("+",(25, 220), (0,225,75))
        sMinus = CommandButton(" -",(10, 220), (225,0,75))
        hPlus  = CommandButton("+",(25, 260), (0,225,75))
        hMinus = CommandButton(" -",(10, 260), (225,0,75))

        apply  = CommandButton("Apply",(100,300),(0,0,0))
        cancel = CommandButton("Cancel",(10,300), (255, 75,75))

        # Keep track of upgrades
        r = 0
        a = 0
        s = 0
        h = 0

        coords = None 

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
                        return 0
                    if apply.isClicked(coords) == True:
                        pass

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
                        troop.upgradeStats("r",r)
                        troop.upgradeStats("a",a)
                        troop.upgradeStats("s",s)
                        troop.upgradeStats("h",h)
                        loop = False
                
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

            pg.display.update()
            self.clock.tick(20)

        return abs(STARTING_TOKENS - tokens)



    ### -------| Game Loops Below |------- ###


    
    def lobbyStage(self):
        """Waits for two players to join."""
        dots    = ""
        counter = 0

        loop = True
        while (loop == True):
            # Gets all the events from the game window. A.k.a., do stuff here.

            events = pg.event.get()

            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            
            self.display.fill((255,255,255))

            
            if counter % 30 == 0:
                dots += "."
            
            if len(dots) > 3:
                dots = ""

            self.displayText("Waiting"+dots,(self.displayWidth//2,self.displayHeight//2))

            counter += 1

            pg.display.update()
            self.clock.tick(30)

    def setupStage(self):
        """Determines dimensions of the game board, players' names, and eventually the player's army.
        Return a tuple containing (Board, Player1, Player2)."""

        nameInput1 = pygame_textinput.TextInput("Player 1")
        nameInput2 = pygame_textinput.TextInput("Player 2")
        
        testMap       = CommandButton("TEST",(self.displayWidth*.25-35, self.displayHeight//2), (0,0,0))
        baseMap       = CommandButton("BASIC",(self.displayWidth*.5-35, self.displayHeight//2), (0,0,0))
        bigMap        = CommandButton("BIG",(self.displayWidth*.75-35, self.displayHeight//2), (0,0,0))

        change1 = CommandButton("PLAYER 1",(10,50), (100,100,100))
        change2 = CommandButton("PLAYER 2",(self.displayWidth-115, 50), (100,100,100))

        b  = None
        m  = None

        selectedInputBox = None

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

                    if coords[0] > 10 and coords[0] < 10 + nameInput1.get_surface().get_width():
                        if coords[1] > 10 and coords[1] < 10 + nameInput1.get_surface().get_height():
                            selectedInputBox = nameInput1
                    
                    if coords[0] > 10 and coords[0] < 10 + nameInput2.get_surface().get_width():
                        if coords[1] > 50 and coords[1] < 50 + nameInput2.get_surface().get_height():
                            selectedInputBox = nameInput2

                    if change1.isClicked(coords) == True:
                        selectedInputBox = nameInput1
                    
                    if change2.isClicked(coords) == True:
                        selectedInputBox = nameInput2

                    # Creates a new board in the middle of the screen.
                    if testMap.isClicked(coords) == True:
                        m = test
                        b = Board(m.dimensions[0], m.dimensions[1],(self.displayWidth//2,self.displayHeight//2),m.MAP)
                        loop = False
                    if baseMap.isClicked(coords) == True:
                        m = basic
                        b = Board(m.dimensions[0], m.dimensions[1],(self.displayWidth//2,self.displayHeight//2),m.MAP)
                        loop = False
                    if bigMap.isClicked(coords) == True:
                        m = big
                        b = Board(m.dimensions[0], m.dimensions[1],(self.displayWidth//2,self.displayHeight//2),m.MAP)
                        loop = False


            self.display.fill((255,255,255))

            change1.showButton(self.display)
            change2.showButton(self.display)

            testMap.showButton(self.display)
            baseMap.showButton(self.display)
            bigMap.showButton(self.display)

            # Only updates the appropriate textbox
            if selectedInputBox  != None:
                selectedInputBox.update(events)

            self.display.blit(nameInput1.get_surface(), (10,10))
            self.display.blit(nameInput2.get_surface(), (self.displayWidth - nameInput2.get_surface().get_width() - 10,10))

            pg.display.update()
            self.clock.tick(60)
        
        p1 = Player(nameInput1.get_text(),"blue",None,m.tokens)
        p2 = Player(nameInput2.get_text(),"red",None,m.tokens)

        return (b,p1,p2)

    def placementStage(self, gameInfo):
        """Accepts a Board object.
        Creates Player objects and executes the placement stage of the game.
        Returns a tuple containing (Board, Player1, Player2)."""
        b  = gameInfo[0]
        p1 = gameInfo[1]
        p2 = gameInfo[2]

        startButton   = CommandButton("start",(self.displayWidth-70, self.displayHeight-30), (0,0,0))

        addButton     = CommandButton("add", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 2*self.displayHeight//6), (150,0,150))
        upgradeButton = CommandButton("upgrade",(b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 3*self.displayHeight//6), (200,150,0))
        switchButton  = CommandButton("switch",(b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 4*self.displayHeight//6), (0,0,0))

        tb = TroopButton(("troop",1,1,25,1,100,(1,1),1,1), (b.getCoords()[0] - (b.getWidth()//2 * 32)-150, 2*self.displayHeight//6))
        rb = TroopButton(("rifleman",1,3,50,1,80,(1,1),2,2), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100, 2*self.displayHeight//6))
        hb = TroopButton(("healer",1,1,-30,1,70,(1,1),2,2), (b.getCoords()[0] - (b.getWidth()//2 * 32)-150, 3*self.displayHeight//6))    
        kb = TroopButton(("knight",1,1,30,2,120,(1,1),1,2), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100, 3*self.displayHeight//6))
        sb = TroopButton(("shield",1,1,10,1,175,(1,1),1,2), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100, 4*self.displayHeight//6))

        newTroop = None
        previewTroop = None
        command  = None
        square   = None    # Is just a tuple of (x,y)

        canSwitch = False
        switchPlayer   = False

        currentPlayer = p1

        loop = True
        while (loop == True):
            # Gets all the events from the game window. A.k.a., do stuff here.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()               # Uncomment for finished game...
                    if startButton.isClicked(coords) == True and p1.getTokens() == 0 and p2.getTokens() == 0:
                        loop = False
                    if b.isClicked(coords) == True:
                        square = b.getSquareCoords(coords)
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

            b.showBoard(self.display)

            tb.showButton(self.display)
            rb.showButton(self.display)
            kb.showButton(self.display)
            sb.showButton(self.display)
            hb.showButton(self.display)

            addButton.showButton(self.display)
            upgradeButton.showButton(self.display)
            switchButton.showButton(self.display)

            # Uncomment for finished game
            if p1.getTokens() == 0 and p2.getTokens() == 0:
                startButton.showButton(self.display)

            # Uncomment for testing
            # startButton.showButton(self.display)

            if currentPlayer.getTokens() == 0:
                command = "switch"

            if square != None:
                previewTroop = b.getSquareValue(square)

            if command == "switch":
                if canSwitch == True:
                    switchPlayer = True
                    canSwitch = False

            if command == "add":
                if newTroop != None and square != None:
                    if b.getSquareType(square) == "bluesquare":
                        if currentPlayer == p1 and b.getSquareValue(square) == None and p2.getTokens() >= 1 and self.canUpgrade(currentPlayer,newTroop) == True:
                            p1.addTroop(newTroop)               # Add troop to player's list
                            p1.spendTokens(newTroop.getCost())
                            newTroop.setColor()
                            b.setSquareValue(square,newTroop)   # Add troop to board
                            canSwitch = True
                            newTroop = None
                    if b.getSquareType(square) == "redsquare":
                        if currentPlayer == p2 and b.getSquareValue(square) == None and p1.getTokens() >= 0 and self.canUpgrade(currentPlayer,newTroop) == True:
                            p2.addTroop(newTroop)               # Add troop to player's list
                            p2.spendTokens(newTroop.getCost())
                            newTroop.setColor()
                            b.setSquareValue(square,newTroop)   # Add troop to board
                            b.setTroopOrientation(newTroop,(square[0],0)) # Rotates square to face opponents
                            canSwitch = True
                            newTroop = None
                    square = None

            if command == "upgrade":
                if square != None:
                    troop = b.getSquareValue(square)
                    if troop != None:
                        if troop.getTeam() == currentPlayer and troop.getLevel() <= 5:
                            if currentPlayer.getTokens() >= 5:
                                if self.canUpgrade(currentPlayer,troop) == True:   ###
                                    u = self.upgrade(troop,5-troop.getLevel())     ###
                            if currentPlayer.getTokens() < 5:
                                if abs(5-troop.getLevel()) < currentPlayer.getTokens():
                                    u = self.upgrade(troop, abs(5-troop.getLevel()))
                                if abs(5-troop.getLevel()) >= currentPlayer.getTokens():
                                    u = self.upgrade(troop,currentPlayer.getTokens())
                            currentPlayer.spendTokens(u)
                            square = None 
                            canSwitch = True

            # Switches active players
            if switchPlayer == True:
                if currentPlayer == p1:
                    currentPlayer = p2
                else:
                    currentPlayer = p1
                switchPlayer = False
                command = None
                
            self.displayText(str(previewTroop), (0, 30))

            self.displayText(str(currentPlayer.getName())+" - "+str(currentPlayer.getTokens()) + " tokens left",(self.displayWidth//2,0))

            self.displayText(str(command), (b.getCoords()[0]-(b.getWidth()*32//2),b.getCoords()[1]-(b.getHeight()*32//2)-30))

            self.displayText("    New Troop", (0,self.displayHeight - 210))
            if newTroop != None:
                self.displayText("Type: "+newTroop.getName(), (0,self.displayHeight-180))
                self.displayText("Level: "+str(newTroop.getLevel()), (0,self.displayHeight-150))
                self.displayText("Range: "+str(newTroop.getRange()), (0,self.displayHeight-120))
                self.displayText("Attack: "+str(newTroop.getAttack())+" ("+str(newTroop.getCooldownCounter())+")", (0,self.displayHeight-90))
                self.displayText("Speed: "+str(newTroop.getSpeed()), (0,self.displayHeight-60))
                self.displayText("Health: "+str(newTroop.getHealth()), (0,self.displayHeight-30))

            self.displayText(str(square), (self.displayWidth*.9,0))
            self.displayText(str(square), (self.displayWidth*.9,0))

            pg.display.update()
            self.clock.tick(30)

        return (b,p1,p2)

    def battleStage(self, gameInfo):
        """Accepts a tuple containing the Board and Player objects in the game.
        Executes the battle stage of the game."""
        b  = gameInfo[0]
        p1 = gameInfo[1]
        p2 = gameInfo[2]

        b.normalizeBoard()
        p1.setMoves(len(p1.getTroops()))
        p2.setMoves(len(p2.getTroops()))

        attackButton = CommandButton("attack", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 2*self.displayHeight//8), (0,50,200))
        moveButton = CommandButton("move", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 3*self.displayHeight//8), (50,150,0))
        rotateButton = CommandButton("rotate", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 4*self.displayHeight//8), (200,100,0))
        passButton = CommandButton("pass", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 5*self.displayHeight//8), (200,50,250))

        # Interface variables
        square = None
        selectedTroop = None
        previewTroop = None
        command = None

        switchPlayer = False

        # Keeps track of which panels should be updated
        info_update      = True
        p1_top_update    = True
        p1_bottom_update = True
        p2_update        = True
        p3_top_update    = True
        p3_bottom_update = True

        currentPlayer = p1

        info_panel = pg.Rect(0,0,self.displayWidth,25)

        # Creates update panels
        panel_one_top = pg.Rect(0,25,self.displayWidth//4,(self.displayHeight*.76)-25)
        panel_one_bottom = pg.Rect(0,self.displayHeight*.76,self.displayWidth//4,self.displayHeight*.24)
        panel_two = pg.Rect(self.displayWidth//4,25,2*(self.displayWidth//4),self.displayHeight-25)
        panel_three_top = pg.Rect(3*(self.displayWidth//4),25,(self.displayWidth/4),self.displayHeight*.76-25)
        panel_three_bottom = pg.Rect(3*(self.displayWidth//4),self.displayHeight*.76,(self.displayWidth/4),self.displayHeight*.24)

        timer_start = time.time()
        timer_end   = None
        pass_number = 0
        while True:
            # Gets all the events from the game window. A.k.a., do stuff here.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()

                if event.type == pg.MOUSEBUTTONDOWN:
                    coords = pg.mouse.get_pos()
                    if b.isClicked(coords) == True:
                        square = b.getSquareCoords(coords)
                    else:
                        square = None
                        selectedTroop = None
                        previewTroop  = None

                    if attackButton.isClicked(coords) == True:
                        command = attackButton.getValue()
                    elif moveButton.isClicked(coords) == True:
                        command = moveButton.getValue()
                    elif rotateButton.isClicked(coords) == True:
                        command = rotateButton.getValue()
                    elif passButton.isClicked(coords) == True:
                        command = passButton.getValue()
                    else:
                        if b.isClicked(coords) == False:
                            command = None

            # Clear previous screen, so it can be updated again.
            
            self.display.fill((255,255,255))

            attackButton.showButton(self.display)
            moveButton.showButton(self.display)
            rotateButton.showButton(self.display)
            passButton.showButton(self.display)

            b.showBoard(self.display)

            self.drawPlayerHealthbars(p1,  "LEFT", selectedTroop)
            self.drawPlayerHealthbars(p2,  "RIGHT", selectedTroop)


                ### GAME LOGIC ###


            if selectedTroop != None:
                if currentPlayer == p1:
                    self.displayTroopCard(selectedTroop,"LEFT")
                    p1_bottom_update = True
                if currentPlayer == p2:
                    self.displayTroopCard(selectedTroop,"RIGHT")
                    p3_bottom_update = True
                    

            if previewTroop != None:
                if currentPlayer == p1:
                    self.displayTroopCard(previewTroop, "RIGHT")
                    p3_bottom_update = True
                if currentPlayer == p2:
                    self.displayTroopCard(previewTroop, "LEFT")
                    p1_bottom_update = True


            if square != None:
                if b.getSquareValue(square) != None:
                    if b.getSquareValue(square).getTeam() == currentPlayer:
                        selectedTroop = b.getSquareValue(square)
                    if b.getSquareValue(square).getTeam() != currentPlayer:
                        previewTroop = b.getSquareValue(square)
                    

            if command == "pass":
                switchPlayer = True
                command = None


            if command == "attack":
                if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer and selectedTroop.getCooldownCounter() == 0:
                    b.attack(selectedTroop)
                    currentPlayer.decrementMoves()
                    selectedTroop.setCooldownCounter()

                    b.killTroops()    # Remove troops from board.

                    p1.killTroops()   # Remove troops from players' records.
                    p2.killTroops()

                    p1_top_update =True 
                    p3_top_update = True
                    square = None


            if command == "move":
                if selectedTroop != None and square != None:
                    ownSquare = b.findTroopSquare(selectedTroop)
                    if square != (ownSquare.getX(),ownSquare.getY()):
                        b.move(selectedTroop,square)
                        p2_update = True
                        if selectedTroop.canMove() == False:
                            currentPlayer.decrementMoves()
                            selectedTroop.resetStamina()
                        square = None
                    if square == (ownSquare.getX(),ownSquare.getY()):
                        square = None


            if command == "rotate":
                if selectedTroop != None and square != None:
                    p2_update = True
                    b.setTroopOrientation(selectedTroop,square)
                    square = None
            

            if currentPlayer.getMoves() <= 0:
                switchPlayer = True


            # Switches active player
            if switchPlayer == True:
                currentPlayer.resetMoves()
                currentPlayer.restTroops()

                selectedTroop = None
                square = None
                command = None

                if currentPlayer == p1:
                    currentPlayer.decrementCooldowns()
                    currentPlayer = p2
                else:
                    currentPlayer.decrementCooldowns()
                    currentPlayer = p1

                switchPlayer = False

            # self.Display game data. Testing purposes only. info_panel data.
            self.displayText(str(currentPlayer.getName())+" - "+str(currentPlayer.getMoves())+ " moves left",(self.displayWidth*.66,0))

            self.displayText(str(command), (self.displayWidth*.33,0))

            self.displayText(str(pg.mouse.get_pos()), (0,0))
            self.displayText(str(square), (self.displayWidth*.9,0))

            update_panels = []
            if info_update == True:
                update_panels.append(info_panel)
                # pg.draw.rect(self.display, (0,0,200), info_panel, 2)    # For testing only...
            if p1_bottom_update == True:
                update_panels.append(panel_one_bottom)
                # pg.draw.rect(self.display, (0,0,200), panel_one_bottom, 2)
            if p1_top_update == True:
                update_panels.append(panel_one_top)
                # pg.draw.rect(self.display, (0,0,200), panel_one_top, 2)
            if p2_update == True:
                update_panels.append(panel_two)
                # pg.draw.rect(self.display, (0,0,200), panel_two, 2)
            if p3_bottom_update == True:
                update_panels.append(panel_three_bottom)
                # pg.draw.rect(self.display, (0,0,200), panel_three_bottom, 2)
            if p3_top_update == True:
                update_panels.append(panel_three_top)
                # pg.draw.rect(self.display, (0,0,200), panel_three_top, 2)

            pg.display.update(update_panels)

            # Keep for testing rendering speed
            if pass_number % 30 == 0:
                timer_end = time.time()
                print("TIME:", timer_end - timer_start)

            pass_number += 1
            self.clock.tick(30)

Game()

