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

    def findTroop(self, troop):
        """Accepts a Troop object.
           Iterates through all the squares and returns the square with the matching troop.
           Returns nothing if the troop isn't found."""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].getTroop() == troop:
                    return self.squares[x][y]
    
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
    
    def setSquareValue(self, pos, troop):
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

    def attack(self,troop):
        """Accepts a Troop object.
           If there's a target within range of the troop, decreases that target's health."""
        troopCoords = (self.findTroop(troop).getX(), self.findTroop(troop).getY())
        attackerX = troopCoords[0]
        attackerY = troopCoords[1]
        attackerRange = troop.getRange()
        attackerStrength = troop.getAttack()
        
        counter = attackerY+1
        while(attackerY+attackerRange+1 > counter):

            if (counter) > 0:
                if (counter) <= self.height-1:
                    if self.squares[attackerX][counter].getTroop() != None:
                        self.squares[attackerX][counter].getTroop().takeDamage(attackerStrength)
                        break

            counter += 1
    
    def killTroops(self):
        """Iterates through entire board.
           If any square's troop's health has reached 0, resets that square."""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].getTroop() != None:
                    self.squares[x][y].killTroop()
    
    def move(self, troop, targetCoords):
        """Accepts a troop object.
           Accepts a tuple for the desired coordinates to move to.
           Iterates through all squares and tries to move the troop to the given position."""
        current = (self.findTroop(troop).getX(), self.findTroop(troop).getY())
        target  = targetCoords
        speed   = troop.getSpeed()
        
        if current [0] == target[0] and current[1] == target[1]:   # Ignores same-square clicks.
            return
        if current[0] != target[0] and current[1] != target[1]:    # Only allows for straight line moves.
            return
        else:
            # Moves vertically
            if current[0] == target[0]:
                
                dist = target[1] - current[1]
                if dist > speed:
                    dist = speed    # Prevents troops from moving farther than their speed allows.

                for y in range(dist):
                    if self.getSquareValue((current[0],current[1]  + y + 1)) == None:
                        self.setSquareValue((current[0],current[1] + y + 1),troop)
                        self.setSquareValue((current[0],current[1] + y), None)
                    else:
                        return      # Exits the loop if there's another troop in the way.

            # Moves horizontally
            if current[1] == target[1]:

                dist = target[0] - current[0]
                if dist > speed:
                    dist = speed    # Prevents troops from moving farther than their speed allows.

                for x in range(dist):
                    if self.getSquareValue((current[0]  + x + 1,current[1])) == None:
                        self.setSquareValue((current[0] + x + 1,current[1]),troop)
                        self.setSquareValue((current[0] + x, current[1]), None)
                    else:
                        return      # Exits the loop if there's another troop in the way.
            
                        