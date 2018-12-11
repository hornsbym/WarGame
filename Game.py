import pygame as pg
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
    """Determines dimensions of the game board, and eventually the player's army."""
    
    fiveByEight     = CommandButton("5x8",(displayWidth*.2-35, displayHeight//2), (0,0,0))
    sixByNine       = CommandButton("6x9",(displayWidth*.4-35, displayHeight//2), (0,0,0))
    nineByTwelve    = CommandButton("9x12",(displayWidth*.6-35, displayHeight//2), (0,0,0))
    elevenByFifteen = CommandButton("11x15",(displayWidth*.8-35, displayHeight//2), (0,0,0))

    loop = True
    while (loop == True):
        # Gets all the events from the game window. A.k.a., do stuff here.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

            if event.type == pg.MOUSEBUTTONDOWN:
                coords = pg.mouse.get_pos()

                # Creates a new board in the middle of the screen.
                if fiveByEight.isClicked(coords) == True:
                    return Board(5,7,(displayWidth//2,displayHeight//2))
                if sixByNine.isClicked(coords) == True:
                    return Board(6,9,(displayWidth//2,displayHeight//2))
                if nineByTwelve.isClicked(coords) == True:
                    return Board(9,12,(displayWidth//2,displayHeight//2))
                if elevenByFifteen.isClicked(coords) == True:       
                    return Board(11,15,(displayWidth//2,displayHeight//2)) 

        fiveByEight.showButton(display)
        sixByNine.showButton(display)
        nineByTwelve.showButton(display)
        elevenByFifteen.showButton(display)

        pg.display.update()
        clock.tick(60)

def placementStage(board):
    """Accepts a Board object.
       Creates Player objects and executes the placement stage of the game.
       Returns a tuple containing (Board, Player1, Player2)."""
    b  = board
    p1 = Player("Player 1",None,b.getWidth()*3,5)
    p2 = Player("Player 2",None,b.getWidth()*3,5)

    startButton = CommandButton("start",(displayWidth-70, displayHeight-30), (0,0,0))
    addButton   = CommandButton("add", (displayWidth-75, 175), (150,0,150))

    rb = TroopButton(("rifleman",1,3,10,1,100,(1,1)), (15,75))
    kb = TroopButton(("knight",1,1,10,2,100,(1,1)), (15,125))
    sb = TroopButton(("shield",1,1,10,1,200,(1,1)), (15, 175))
    tb = TroopButton(('target',1,0,0,0,100,(1,1)), (15,225))

    newTroop = None
    command  = None
    square   = None

    currentPlayer = p1

    loop = True
    while (loop == True):
        # Gets all the events from the game window. A.k.a., do stuff here.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                coords = pg.mouse.get_pos()
                if startButton.isClicked(coords) == True:
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
                if tb.isClicked(coords) == True:
                    newTroop = Troop(tb.getValue())
                
                if addButton.isClicked(coords) == True:
                    command = addButton.getValue()
        
        # Clear previous screen, so it can be updated again.
        display.fill((255,255,255))

        b.showBoard(display)

        rb.showButton(display)
        kb.showButton(display)
        sb.showButton(display)
        tb.showButton(display)

        addButton.showButton(display)
        startButton.showButton(display)

        if command == "add":
            if newTroop != None and square != None:
                if square[1] <= 2:
                    if currentPlayer == p1 and b.getSquareValue(square) == None:
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        p1.addTroop(newTroop)               # Add troop to player's list
                        currentPlayer = p2
                        newTroop = None
                if square[1] >= b.getHeight()-4:
                    if currentPlayer == p2 and b.getSquareValue(square) == None:
                        b.setSquareValue(square,newTroop)   # Add troop to board
                        p2.addTroop(newTroop)               # Add troop to player's list
                        currentPlayer = p1
                        newTroop = None
                square = None

        displayText(str(currentPlayer.getName()),(displayWidth//2,0))

        displayText("New: "+str(newTroop), (0,displayHeight-50))
        displayText(str(command), (displayWidth*.9,displayHeight-80))       
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

    attackButton = CommandButton("attack", (displayWidth-75, 75), (0,50,200))
    moveButton = CommandButton("move", (displayWidth-75, 125), (50,150,0))
    rotateButton = CommandButton("rotate", (displayWidth-75, 175), (200,100,0))

    # Interface variables
    square = None
    selectedTroop = None
    command = None

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

                if attackButton.isClicked(coords) == True:
                    command = attackButton.getValue()
                if moveButton.isClicked(coords) == True:
                    command = moveButton.getValue()
                if rotateButton.isClicked(coords) == True:
                    command = rotateButton.getValue()

        # Clear previous screen, so it can be updated again.
        display.fill((255,255,255))

        attackButton.showButton(display)
        moveButton.showButton(display)
        rotateButton.showButton(display)

        b.showBoard(display)
        

            ### GAME LOGIC ###


        if square != None:
            if b.getSquareValue(square) != None:
                selectedTroop = b.getSquareValue(square)


        if command == "attack":
            if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer.getName():
                b.attack(selectedTroop)
                square = None

                # FIX ME --->
                if currentPlayer == p1:
                    currentPlayer = p2
                else:
                    currentPlayer = p1


        if command == "move":
            if selectedTroop != None and square != None:
                b.move(selectedTroop,square)
                square = None
        

        if command == "rotate":
            if selectedTroop != None and square != None:
                b.setTroopOrientation(selectedTroop,square)
                square = None
                

                
        b.killTroops()    # Remove troops from board.

        p1.killTroops()   # Remove troops from players' records.
        p2.killTroops()

        # Display game data. Testing purposes only.
        displayText(str(currentPlayer.getName()),(displayWidth//2,0))

        displayText(str(pg.mouse.get_pos()), (0,0))
        displayText(str(square), (displayWidth*.9,0))

        displayText("Select: "+str(selectedTroop), (0,displayHeight-30))
        displayText(str(command), (displayWidth*.9,displayHeight-60))

        pg.display.update()
        clock.tick(20)

emptyBoard = setupStage()
startingBoard = placementStage(emptyBoard)
battleStage(startingBoard)
pg.quit()
quit()