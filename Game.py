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
displayWidth = 650
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
    
    p1 = Player(nameInput1.get_text(),None,b.getWidth()*3)
    p2 = Player(nameInput2.get_text(),None,b.getWidth()*3)

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
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        p1.addTroop(newTroop)               # Add troop to player's list
                        p1.spendTokens(1)
                        canSwitch = True
                        newTroop = None
                if square[1] >= b.getHeight()-3:
                    if currentPlayer == p2 and b.getSquareValue(square) == None and p1.getTokens() >= 0:
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        p2.addTroop(newTroop)               # Add troop to player's list
                        p2.spendTokens(1)
                        canSwitch = True
                        newTroop = None
                square = None

        if command == "upgrade":
            if square != None:
                troop = b.getSquareValue(square)
                if troop != None and troop.getTeam() == currentPlayer.getName():
                    troop.incrementLevel()
                    currentPlayer.spendTokens(1)
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
    
    # Changes all troops stats based on their levels
    p1.upgradeTroops()
    p2.upgradeTroops()

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
                if b.getSquareValue(square).getTeam() == currentPlayer.getName():
                    selectedTroop = b.getSquareValue(square)
                if b.getSquareValue(square).getTeam() != currentPlayer.getName():
                    previewTroop = b.getSquareValue(square)


        if command == "pass":
            switchPlayer = True
            command = None


        if command == "attack":
            if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer.getName() and selectedTroop.getCooldownCounter() == 0:
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

        displayText("    Selected Troop", (0,displayHeight - 210))
        if selectedTroop != None:
            displayText("Type: "+selectedTroop.getName(), (0,displayHeight-180))
            displayText("Level: "+str(selectedTroop.getLevel()), (0,displayHeight-150))
            displayText("Range: "+str(selectedTroop.getRange()), (0,displayHeight-120))
            displayText("Attack: "+str(selectedTroop.getAttack())+" ("+str(selectedTroop.getCooldownCounter())+")", (0,displayHeight-90))
            displayText("Speed: "+str(selectedTroop.getSpeed()), (0,displayHeight-60))
            displayText("Health: "+str(selectedTroop.getHealth()), (0,displayHeight-30))

        displayText("    Troop Preview", (displayWidth-150,displayHeight-210))
        if previewTroop != None:
            displayText("Type: "+previewTroop.getName(), (displayWidth-150,displayHeight-180))
            displayText("Level: "+str(previewTroop.getLevel()), (displayWidth-150,displayHeight-150))
            displayText("Range: "+str(previewTroop.getRange()), (displayWidth-150,displayHeight-120))
            displayText("Attack: "+str(previewTroop.getAttack())+" ("+str(previewTroop.getCooldownCounter())+")", (displayWidth-150,displayHeight-90))
            displayText("Speed: "+str(previewTroop.getSpeed()), (displayWidth-150,displayHeight-60))
            displayText("Health: "+str(previewTroop.getHealth()), (displayWidth-150,displayHeight-30))


        pg.display.update()
        clock.tick(20)

emptyBoard = setupStage()
startingBoard = placementStage(emptyBoard)
battleStage(startingBoard)
pg.quit()
quit()