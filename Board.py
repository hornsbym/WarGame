import pygame as pg
from Square import Square

class Board(object):
    """Represents the playing surface for the game.
       Holds and represents an array of squares."""

    def __init__(self, width=10, height=9, coords=(0,0)):
        """ width = Integer specifying how many squares wide the game board should be. 
           height = Integer specifying how many squares tall the board should be.
           coords = Tuple specifying the starting position (in pixel coordinates) for the 
                     upper-left hand corner of the board."""
        self.width = width
        self.height = height
        self.startingCoords = coords
        self.squares = []

        self.makeBoard()

    def makeBoard(self):
        """Populates the board with squares."""
        board = []

        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(Square(x,y,self.startingCoords))

            board.append(row)

        self.squares = board

    def showBoard(self,display):
        """Accepts a pygame Display object.
           Iterates through the board's squares and draws them on that display"""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                self.squares[x][y].showSquare(display)
    
    def getSquareCoords(self, coords):
        """Accepts a tuple of coordinates in the form (x,y)
           Iterates through board's squares and returns the square that contains those coordinates."""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].isClicked(coords) == True:
                    return (self.squares[x][y].getX(), self.squares[x][y].getY())

    def getSquareValue(self, tup):
        """Accepts a tuple of form (x,y).
           Iterates through the squares and returns the troop value of the
           square at that location."""
        squareX = tup[0]
        squareY = tup[1]
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].getX() == squareX and self.squares[x][y].getY() == squareY:
                    return self.squares[x][y].getTroop()
    
    def setSquareIcon(self, pos, troop):
        """Accepts a tuple of a square's x-position and y-position.
           Accepts a string designating an icon.
           Finds the square at the designated position and sets its icon."""
        self.squares[pos[0]][pos[1]].setTroop(troop)
        
    def isClicked(self,coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area.
           Returns False if not."""
        xRange = self.startingCoords[0]+(self.width*32)
        yRange = self.startingCoords[1]+(self.height*32)

        if coords[0] > self.startingCoords[0] and coords[0] < xRange:
            if coords[1] > self.startingCoords[1] and coords[1] < yRange:
                return True
        
        return False

    def attack(self,attackerCoords,attackerRange,attackerStrength):
        """Accepts a tuple for the square's relative loacation.
           Accepts an integer for the attacker's attack range.
           If there's a target within range, decreases that target's health."""
        attackerX = attackerCoords[0]
        attackerY = attackerCoords[1]
        
        counter = attackerY+1
        while(attackerY+attackerRange+1 > counter):

            if (counter) > 0:
                if (counter) <= self.height-1:
                    if self.squares[attackerX][counter].getTroop() != None:
                        self.squares[attackerX][counter].getTroop().takeDamage(attackerStrength)
                        print(self.squares[attackerX][counter].getTroop())
                        break

            counter += 1
    
    def killTroops(self):
        """Iterates through entire board.
           If any square's troop's health has reached 0, resets that square."""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].getTroop() != None:
                    self.squares[x][y].killTroop()