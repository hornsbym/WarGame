import pygame as pg
import time

from Square import Square
from Board import Board
from TroopButton import TroopButton
from CommandButton import CommandButton
from Troop import Troop

# Canned pg stuff:
pg.init()
clock = pg.time.Clock()
displayWidth = 600
displayHeight = 400
display = pg.display.set_mode((displayWidth,displayHeight))
display.fill((255,255,255))

def displayText(string, tup=(0,0)):
    """Accepts a string and a tuple of x and y coordinates.
       X coordinate should be the first value in the tuple.
       Displays the string in at the designated coordinates."""
    font = pg.font.SysFont(None, 25)
    text = font.render(string, True, (0,0,0))
    display.blit(text, tup)

def main():
    """Executes the startup script and initiates the main game loop."""

    # Creates a new board in the middle of the screen.
    b = Board(5,5,(round(displayWidth/2-80),round(displayHeight/2)-80))

    rb = TroopButton(("rifleman",1,3,10,1,100), (50,75))
    kb = TroopButton(("knight",1,1,10,2,100), (50,125))
    sb = TroopButton(("shield",1,1,10,1,200), (50, 175))
    tb = TroopButton(('target',1,0,0,0,100), (50,225))

    attackButton = CommandButton("attack", (450, 75), (0,50,150))
    moveButton = CommandButton("move", (450, 125), (50,150,0))

    clicked = None
    square = None
    selectedTroop = None
    command = None

    while True:
        # Gets all the events from the game window. A.k.a., do stuff here.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

            if event.type == pg.MOUSEBUTTONDOWN:
                coords = pg.mouse.get_pos()
                if b.isClicked(coords) == True:
                    clicked = coords
                    square = b.getSquareCoords(coords)

                # Checks the troop placement buttons
                if rb.isClicked(coords) == True:
                    selectedTroop = Troop(rb.getValue())
                if sb.isClicked(coords) == True:
                    selectedTroop = Troop(sb.getValue())
                if kb.isClicked(coords) == True:
                    selectedTroop = Troop(kb.getValue())
                if tb.isClicked(coords) == True:
                    selectedTroop = Troop(tb.getValue())

                if attackButton.isClicked(coords) == True:
                    command = attackButton.getValue()
                if moveButton.isClicked(coords) == True:
                    command = moveButton.getValue()

        # Clear previous screen, so it can be updated again.
        display.fill((255,255,255))

        rb.showButton(display)
        kb.showButton(display)
        sb.showButton(display)
        tb.showButton(display)

        attackButton.showButton(display)
        moveButton.showButton(display)

        b.showBoard(display)

            ### GAME LOGIC ###

        # Adds troops to the board.
        if square != None and selectedTroop != None:
            b.setSquareIcon(square,selectedTroop)   
            square = None
            selectedTroop = None
        
        if square != None and selectedTroop == None:
            selectedTroop = b.getSquareValue(square)
            if selectedTroop != None and command == "attack":
                b.attack((square), selectedTroop.getRange(), selectedTroop.getAttack())
                square = None
        
        b.killTroops()

        # Display game data. Testing purposes only.
        displayText(str(pg.mouse.get_pos()), (0,0))
        displayText(str(square), (displayWidth*.9,0))
        displayText(str(selectedTroop), (0,displayHeight-30))
        displayText(str(command), (displayWidth*.9,displayHeight-30))


        pg.display.update()
        clock.tick(60)
    
main()
pg.quit()
quit()