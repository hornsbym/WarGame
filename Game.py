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
    
    fiveByEight     = CommandButton("5x8",(displayWidth*.2-35, displayHeight//2), (0,0,0))
    sixByNine       = CommandButton("6x9",(displayWidth*.4-35, displayHeight//2), (0,0,0))
    nineByTwelve    = CommandButton("9x12",(displayWidth*.6-35, displayHeight//2), (0,0,0))
    elevenByFifteen = CommandButton("11x15",(displayWidth*.8-35, displayHeight//2), (0,0,0))

    change1 = CommandButton("PLAYER 1",(10,50), (100,100,100))
    change2 = CommandButton("PLAYER 2",(displayWidth-100, 50), (100,100,100))

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
                if fiveByEight.isClicked(coords) == True:
                    b = Board(5,7,(displayWidth//2,displayHeight//2))
                    loop = False
                if sixByNine.isClicked(coords) == True:
                    b = Board(6,9,(displayWidth//2,displayHeight//2))
                    loop = False
                if nineByTwelve.isClicked(coords) == True:
                    b = Board(9,12,(displayWidth//2,displayHeight//2))
                    loop = False
                if elevenByFifteen.isClicked(coords) == True:       
                    b = Board(11,15,(displayWidth//2,displayHeight//2)) 
                    loop = False

        display.fill((255,255,255))

        change1.showButton(display)
        change2.showButton(display)

        fiveByEight.showButton(display)
        sixByNine.showButton(display)
        nineByTwelve.showButton(display)
        elevenByFifteen.showButton(display)

        if selectedInputBox  != None:
            selectedInputBox.update(events)

        display.blit(nameInput1.get_surface(), (10,10))
        display.blit(nameInput2.get_surface(), (displayWidth - nameInput2.get_surface().get_width() - 10,10))

        pg.display.update()
        clock.tick(60)
    
    p1 = Player(nameInput1.get_text(),None,10,10)
    p2 = Player(nameInput2.get_text(),None,10,10)

    return (b,p1,p2)

def placementStage(gameInfo):
    """Accepts a Board object.
       Creates Player objects and executes the placement stage of the game.
       Returns a tuple containing (Board, Player1, Player2)."""
    b  = gameInfo[0]
    p1 = gameInfo[1]
    p2 = gameInfo[2]

    startButton = CommandButton("start",(displayWidth-70, displayHeight-30), (0,0,0))
    addButton   = CommandButton("add", (displayWidth-75, 175), (150,0,150))

    rb = TroopButton(("rifleman",1,3,10,1,100,(1,1)), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,displayHeight//5))
    kb = TroopButton(("knight",1,1,10,2,100,(1,1)), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,2*displayHeight//5))
    sb = TroopButton(("shield",1,1,10,1,200,(1,1)), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,3*displayHeight//5))
    tb = TroopButton(('target',1,0,0,0,100,(1,1)), (b.getCoords()[0] - (b.getWidth()//2 * 32)-100,4*displayHeight//5))

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
                if b.getSquareValue(square).getTeam() == currentPlayer.getName():
                    selectedTroop = b.getSquareValue(square)


        if command == "attack":
            if selectedTroop != None and square != None and selectedTroop.getTeam() == currentPlayer.getName():
                b.attack(selectedTroop)
                currentPlayer.decrementMoves()
                square = None


        if command == "move":
            if selectedTroop != None and square != None:
                b.move(selectedTroop,square)
                currentPlayer.decrementMoves()
                square = None
        

        if command == "rotate":
            if selectedTroop != None and square != None:
                b.setTroopOrientation(selectedTroop,square)
                square = None

        if currentPlayer.getMoves() <= 0:
            if currentPlayer == p1:
                currentPlayer.resetMoves()
                selectedTroop = None
                square = None
                command = None
                currentPlayer = p2
            else:
                currentPlayer.resetMoves()
                selectedTroop = None
                square = None
                command = None
                currentPlayer = p1

                
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