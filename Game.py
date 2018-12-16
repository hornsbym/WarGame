import pygame as pg
import pygame_textinput
import time

from Square import Square
from Board import Board
from TroopButton import TroopButton
from CommandButton import CommandButton
from Troop import Troop
from Player import Player

# Boilerplate pygame stuff:
pg.init()
clock = pg.time.Clock()
displayWidth = 800
displayHeight = 600
display = pg.display.set_mode((displayWidth,displayHeight))
display.fill((255,255,255))

def displayText(string, tup=(0,0)):
    """Accepts a string and a tuple of x and y coordinates.
       X coordinate should be the first value in the tuple.
       Displays the string in at the designated coordinates."""
    font = pg.font.SysFont(None, 25)
    text = font.render(string, True, (0,0,0))
    display.blit(text, tup)

def upgrade(troop, tokens):
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
            
        display.fill((255,255,255))

        displayText(troop.getName()+" - "+str(tokens)+" tokens",(15,85))

        # Create text labels
        displayText("Range: "+str(troop.previewUpgrade("r",r)),(50,140))
        displayText("Attack: "+str(troop.previewUpgrade("a",a)),(50,180))
        displayText("Speed: "+str(troop.previewUpgrade("s",s)),(50,220))
        displayText("Health: "+str(troop.previewUpgrade("h",h)),(50,260))

        # Show add/subtract buttons
        rPlus.showButton(display)
        rMinus.showButton(display)
        aPlus.showButton(display)
        aMinus.showButton(display)
        sPlus.showButton(display)
        sMinus.showButton(display)
        hPlus.showButton(display)
        hMinus.showButton(display)    

        apply.showButton(display)
        cancel.showButton(display)

        pg.display.update()
        clock.tick(20)

    return abs(STARTING_TOKENS - tokens)

def setupStage():
    """Determines dimensions of the game board, players' names, and eventually the player's army.
       Return a tuple containing (Board, Player1, Player2)."""

    nameInput1 = pygame_textinput.TextInput("Player 1")
    nameInput2 = pygame_textinput.TextInput("Player 2")
    
    oneByNine      = CommandButton("1x9",(displayWidth*.2-35, displayHeight//2), (0,0,0))
    fiveByNine       = CommandButton("5x9",(displayWidth*.4-35, displayHeight//2), (0,0,0))
    sevenByTwelve    = CommandButton("7x12",(displayWidth*.6-35, displayHeight//2), (0,0,0))
    nineByFifteen = CommandButton("9x15",(displayWidth*.8-35, displayHeight//2), (0,0,0))

    change1 = CommandButton("PLAYER 1",(10,50), (100,100,100))
    change2 = CommandButton("PLAYER 2",(displayWidth-115, 50), (100,100,100))

    b  = None

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
                if oneByNine.isClicked(coords) == True:
                    b = Board(1,7,(displayWidth//2,displayHeight//2))
                    loop = False
                if fiveByNine.isClicked(coords) == True:
                    b = Board(5,9,(displayWidth//2,displayHeight//2))
                    loop = False
                if sevenByTwelve.isClicked(coords) == True:
                    b = Board(7,12,(displayWidth//2,displayHeight//2))
                    loop = False
                if nineByFifteen.isClicked(coords) == True:       
                    b = Board(9,15,(displayWidth//2,displayHeight//2)) 
                    loop = False

        display.fill((255,255,255))

        change1.showButton(display)
        change2.showButton(display)

        oneByNine.showButton(display)
        fiveByNine.showButton(display)
        sevenByTwelve.showButton(display)
        nineByFifteen.showButton(display)

        # Only updates the appropriate textbox
        if selectedInputBox  != None:
            selectedInputBox.update(events)

        display.blit(nameInput1.get_surface(), (10,10))
        display.blit(nameInput2.get_surface(), (displayWidth - nameInput2.get_surface().get_width() - 10,10))

        pg.display.update()
        clock.tick(60)
    
    p1 = Player(nameInput1.get_text(),"blue",None,b.getWidth()*3)
    p2 = Player(nameInput2.get_text(),"red",None,b.getWidth()*3)

    return (b,p1,p2)

def placementStage(gameInfo):
    """Accepts a Board object.
       Creates Player objects and executes the placement stage of the game.
       Returns a tuple containing (Board, Player1, Player2)."""
    b  = gameInfo[0]
    p1 = gameInfo[1]
    p2 = gameInfo[2]

    startButton   = CommandButton("start",(displayWidth-70, displayHeight-30), (0,0,0))

    addButton     = CommandButton("add", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 2*displayHeight//6), (150,0,150))
    upgradeButton = CommandButton("upgrade",(b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 3*displayHeight//6), (200,150,0))
    switchButton  = CommandButton("switch",(b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 4*displayHeight//6), (0,0,0))

    rb = TroopButton(("rifleman",1,3,50,1,100,(1,1),2), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,2*displayHeight//6))
    kb = TroopButton(("knight",1,1,30,2,120,(1,1),1), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,3*displayHeight//6))
    sb = TroopButton(("shield",1,1,10,1,200,(1,1),1), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,4*displayHeight//6))

    newTroop = None
    command  = None
    square   = None

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
                if rb.isClicked(coords) == True:
                    newTroop = Troop(rb.getValue())
                if sb.isClicked(coords) == True:
                    newTroop = Troop(sb.getValue())
                if kb.isClicked(coords) == True:
                    newTroop = Troop(kb.getValue())
                
                if addButton.isClicked(coords) == True:
                    command = addButton.getValue()
                if upgradeButton.isClicked(coords) == True:
                    command = upgradeButton.getValue()
                if switchButton.isClicked(coords) == True:
                    command = switchButton.getValue()
        
        # Clear previous screen, so it can be updated again.
        display.fill((255,255,255))

        b.showBoard(display)

        rb.showButton(display)
        kb.showButton(display)
        sb.showButton(display)

        addButton.showButton(display)
        upgradeButton.showButton(display)
        switchButton.showButton(display)

        # Uncomment for finished game
        if p1.getTokens() == 0 and p2.getTokens() == 0:
            startButton.showButton(display)

        # Uncomment for testing
        # startButton.showButton(display)

        if currentPlayer.getTokens() == 0:
            command = "switch"

        if command == "switch":
            if canSwitch == True:
                switchPlayer = True
                canSwitch = False

        if command == "add":
            if newTroop != None and square != None:
                if square[1] <= 2:
                    if currentPlayer == p1 and b.getSquareValue(square) == None and p2.getTokens() >= 1:
                        p1.addTroop(newTroop)               # Add troop to player's list
                        p1.spendTokens(1)
                        newTroop.setColor()
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        canSwitch = True
                        newTroop = None
                if square[1] >= b.getHeight()-3:
                    if currentPlayer == p2 and b.getSquareValue(square) == None and p1.getTokens() >= 0:
                        p2.addTroop(newTroop)               # Add troop to player's list
                        p2.spendTokens(1)
                        newTroop.setColor()
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        b.setTroopOrientation(newTroop,(0,0)) # Rotates square to face opponents
                        canSwitch = True
                        newTroop = None
                square = None

        if command == "upgrade":
            if square != None:
                troop = b.getSquareValue(square)
                if troop != None:
                    if troop.getTeam() == currentPlayer and troop.getLevel() <= 5:
                        if currentPlayer.getTokens() >= 5:
                            u = upgrade(troop,5)
                        if currentPlayer.getTokens() <= 5:
                            u = upgrade(troop,currentPlayer.getTokens())
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

        displayText(str(currentPlayer.getName())+" - "+str(currentPlayer.getTokens()) + " tokens left",(displayWidth//2,0))

        displayText(str(command), (b.getCoords()[0]-(b.getWidth()*32//2),b.getCoords()[1]-(b.getHeight()*32//2)-30))

        displayText("    New Troop", (0,displayHeight - 210))
        if newTroop != None:
            displayText("Type: "+newTroop.getName(), (0,displayHeight-180))
            displayText("Level: "+str(newTroop.getLevel()), (0,displayHeight-150))
            displayText("Range: "+str(newTroop.getRange()), (0,displayHeight-120))
            displayText("Attack: "+str(newTroop.getAttack())+" ("+str(newTroop.getCooldownCounter())+")", (0,displayHeight-90))
            displayText("Speed: "+str(newTroop.getSpeed()), (0,displayHeight-60))
            displayText("Health: "+str(newTroop.getHealth()), (0,displayHeight-30))

        displayText(str(square), (displayWidth*.9,0))
        displayText(str(square), (displayWidth*.9,0))

        pg.display.update()
        clock.tick(20)

    return (b,p1,p2)

def battleStage(gameInfo):
    """Accepts a tuple containing the Board and Player objects in the game.
       Executes the battle stage of the game."""
    b  = gameInfo[0]
    p1 = gameInfo[1]
    p2 = gameInfo[2]

    p1.setMoves(len(p1.getTroops()))
    p2.setMoves(len(p2.getTroops()))

    attackButton = CommandButton("attack", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 2*displayHeight//8), (0,50,200))
    moveButton = CommandButton("move", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 3*displayHeight//8), (50,150,0))
    rotateButton = CommandButton("rotate", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 4*displayHeight//8), (200,100,0))
    passButton = CommandButton("pass", (b.getCoords()[0] + ((b.getWidth()* 32)/2) + 32, 5*displayHeight//8), (200,50,250))

    # Interface variables
    square = None
    selectedTroop = None
    previewTroop = None
    command = None

    switchPlayer = False

    currentPlayer = p1

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
                if moveButton.isClicked(coords) == True:
                    command = moveButton.getValue()
                if rotateButton.isClicked(coords) == True:
                    command = rotateButton.getValue()
                if passButton.isClicked(coords) == True:
                    command = passButton.getValue()

        # Clear previous screen, so it can be updated again.
        display.fill((255,255,255))

        attackButton.showButton(display)
        moveButton.showButton(display)
        rotateButton.showButton(display)
        passButton.showButton(display)

        b.showBoard(display)
        

            ### GAME LOGIC ###


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

                square = None


        if command == "move":
            if selectedTroop != None and square != None:
                ownSquare = b.findTroopSquare(selectedTroop)
                if square != (ownSquare.getX(),ownSquare.getY()):
                    b.move(selectedTroop,square)
                    if selectedTroop.canMove() == False:
                        currentPlayer.decrementMoves()
                    square = None
                if square == (ownSquare.getX(),ownSquare.getY()):
                    square = None
        

        if command == "rotate":
            if selectedTroop != None and square != None:
                b.setTroopOrientation(selectedTroop,square)
                square = None


        if currentPlayer.getMoves() <= 0:
            currentPlayer.resetMoves()
            currentPlayer.restTroops()

            selectedTroop = None
            square = None
            command = None
            switchPlayer = True

        # Switches active player
        if switchPlayer == True:
            if currentPlayer == p1:
                currentPlayer.decrementCooldowns()
                currentPlayer = p2
            else:
                currentPlayer.decrementCooldowns()
                currentPlayer = p1
            switchPlayer = False

        # Display game data. Testing purposes only.
        displayText(str(currentPlayer.getName())+" - "+str(currentPlayer.getMoves())+ " moves left",(displayWidth//2,0))

        displayText(str(command), (b.getCoords()[0]-(b.getWidth()*32//2),b.getCoords()[1]-(b.getHeight()*32//2)-30))

        displayText(str(pg.mouse.get_pos()), (0,0))
        displayText(str(square), (displayWidth*.9,0))

        displayText("    Enemy Troop Stats", (0,displayHeight-440))
        if previewTroop != None:
            displayText("Type: "+previewTroop.getName(), (0,displayHeight-410))
            displayText("Level: "+str(previewTroop.getLevel()), (0,displayHeight-390))
            displayText("Range: "+str(previewTroop.getRange()), (0,displayHeight-360))
            displayText("Attack: "+str(previewTroop.getAttack())+" ("+str(previewTroop.getCooldownCounter())+")", (0,displayHeight-330))
            displayText("Speed: "+str(previewTroop.getSpeed()), (0,displayHeight-300))
            displayText("Health: "+str(previewTroop.getHealth()), (0,displayHeight-270))

        displayText("    Your Stats", (0,displayHeight - 210))
        if selectedTroop != None:
            displayText("Type: "+selectedTroop.getName(), (0,displayHeight-180))
            displayText("Level: "+str(selectedTroop.getLevel()), (0,displayHeight-150))
            displayText("Range: "+str(selectedTroop.getRange()), (0,displayHeight-120))
            displayText("Attack: "+str(selectedTroop.getAttack())+" ("+str(selectedTroop.getCooldownCounter())+")", (0,displayHeight-90))
            displayText("Speed: "+str(selectedTroop.getSpeed()), (0,displayHeight-60))
            displayText("Health: "+str(selectedTroop.getHealth()), (0,displayHeight-30))


        pg.display.update()
        clock.tick(20)

emptyBoard = setupStage()
startingBoard = placementStage(emptyBoard)
battleStage(startingBoard)
pg.quit()
quit()