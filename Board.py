import pygame as pg
from Square import Square

class Board(object):
    """Represents the playing surface for the game.
       Holds and represents an array of squares."""

    def __init__(self, width, height, centerCoords):
        """ width = Integer specifying how many squares wide the game board should be. 
           height = Integer specifying how many squares tall the board should be.
           coords = Tuple specifying the center coordinates of the display."""
        self.width = width
        self.height = height
        self.centerCoords = centerCoords
        self.squares = []

        self.makeBoard()
    
    def getCoords(self):
        return self.centerCoords

    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height

    def makeBoard(self):
        """Populates the board with squares."""
        board = []

        xOffset = round(self.width * 32//2)
        yOffset = round(self.height * 32//2)

        for x in range(self.width):
            row = []
            for y in range(self.height):
                row.append(Square(x,y,(self.centerCoords[0]-xOffset,self.centerCoords[1]-yOffset)))

            board.append(row)

        self.squares = board

    def showBoard(self,display):
        """Accepts a pygame Display object.
           Iterates through the board's squares and draws them on that display"""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                self.squares[x][y].showSquare(display)

    def findTroopSquare(self, troop):
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
                    print(self.squares[x][y].getX(), self.squares[x][y].getY())
                    return (self.squares[x][y].getX(), self.squares[x][y].getY())

    def getSquareValue(self, tup):
        """Accepts a tuple of form (x,y).
           Iterates through the squares and returns the Troop Object of the
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
        xRange = self.centerCoords[0]+(self.width*32//2)
        yRange = self.centerCoords[1]+(self.height*32//2)

        if coords[0] > self.centerCoords[0]-(self.width*32//2) and coords[0] < xRange:
            if coords[1] > self.centerCoords[1]-(self.height*32//2) and coords[1] < yRange:
                return True
        
        return False

    def killTroops(self):
        """Iterates through entire board.
           If any square's troop's health has reached 0, resets that square."""
        for x in range(len(self.squares)):
            for y in range(len(self.squares[x])):
                if self.squares[x][y].getTroop() != None:
                    self.squares[x][y].killTroop()

    def attack(self,troop):
        """Accepts a Troop object.
           If there's a target within range of the troop, decreases that target's health."""
        troopCoords = (self.findTroopSquare(troop).getX(), self.findTroopSquare(troop).getY())
        orientation = troop.getOrientation()
        attackerX = troopCoords[0]
        attackerY = troopCoords[1]
        attackerRange = troop.getRange()
        attackerStrength = troop.getAttack()

        # Attacks up or down
        if orientation == (1,1) or orientation == (-1,-1):
            if attackerRange + troopCoords[1] > self.height-1:    # Prevents attacking beyond bottom   
                attackerRange = (self.height-1) - troopCoords[1]  # of board.
            for y in range(attackerY,attackerY+orientation[1]*(attackerRange+1),orientation[1]):
                if y != attackerY:
                    # Makes sure the square being attacked isn't empty or on the same team.
                    if self.squares[attackerX][y].getTroop() != None and self.squares[attackerX][y].getTroop().getTeam() != troop.getTeam():
                        self.squares[attackerX][y].getTroop().takeDamage(attackerStrength)
                        break
                    # Stops attack if it hits a teammate
                    if self.squares[attackerX][y].getTroop() != None and self.squares[attackerX][y].getTroop().getTeam() == troop.getTeam():
                        break

        # Attacks left or right
        if orientation == (-1,1) or orientation == (1,-1):
            if attackerRange + troopCoords[0] > self.width-1:    # Prevents attacking beyond right    
                attackerRange = (self.width-1) - troopCoords[0]  # side of board.
            for x in range(attackerX,attackerX+orientation[0]*(attackerRange+1),orientation[0]):
                if x != attackerX:
                    # Makes sure the square being attacked isn't empty or on the same team.
                    if self.squares[x][attackerY].getTroop() != None and self.squares[x][attackerY].getTroop().getTeam() != troop.getTeam():
                        self.squares[x][attackerY].getTroop().takeDamage(attackerStrength)
                        break
                    # Stops attack if it hits a teammate
                    if self.squares[x][attackerY].getTroop() != None and self.squares[x][attackerY].getTroop().getTeam() == troop.getTeam():
                        break
    
    def move(self, troop, targetCoords):
        """Accepts a troop object.
           Accepts a tuple for the desired coordinates to move to.
           Iterates through all squares and tries to move the troop to the given position.
           Applies rotations to troop."""
        current = (self.findTroopSquare(troop).getX(), self.findTroopSquare(troop).getY())
        target  = targetCoords
        speed   = troop.getSpeed()

        self.setTroopOrientation(troop,target)                     # Resets the troop's orientation to match the desired direction.
        orientation = troop.getOrientation()
        
        if current [0] == target[0] and current[1] == target[1]:   # Ignores same-square clicks.
            return
        if current[0] != target[0] and current[1] != target[1]:    # Only allows for straight line moves.
            return
        else:
            # Moves vertically
            if current[0] == target[0]:
                dist = abs(target[1] - current[1])
                if dist > speed:    # Prevents troops from moving farther than their speed allows.
                    dist = speed    
                dist *= orientation[1]

                for y in range(0,dist,orientation[1]):
                    if self.getSquareValue((current[0],current[1]  + y + orientation[1])) == None:
                        self.setSquareValue((current[0],current[1] + y + orientation[1]),troop)
                        self.setSquareValue((current[0],current[1] + y), None)
                    else:
                        return      # Exits the loop if there's another troop in the way.

            # Moves horizontally
            if current[1] == target[1]:

                dist = abs(target[0] - current[0])
                if dist > speed:    # Prevents troops from moving farther than their speed allows.
                    dist = speed    
                dist *= orientation[0]

                for x in range(0, dist, orientation[0]):
                    if self.getSquareValue((current[0]  + x + orientation[0],current[1])) == None:
                        self.setSquareValue((current[0] + x + orientation[0],current[1]),troop)
                        self.setSquareValue((current[0] + x, current[1]), None)
                    else:
                        return      # Exits the loop if there's another troop in the way.
    
    def setTroopOrientation(self,troop,tup):
        """Accepts a Troop Object.
           Accepts a tuple of form (x,y).
           Changes the provided troop's orientation to match where the mouseclick is.
        """
        selectedTroop = troop
        square = tup
        currentSquare = self.findTroopSquare(selectedTroop)
        currentOrientation = selectedTroop.getOrientation()

        # Rotation in place; clicking the troop's own square.
        if square[1] == currentSquare.getY() and square[0] == currentSquare.getX():
                selectedTroop.setOrientation((( currentOrientation[0]**2) * currentOrientation[1] , -1 * (currentOrientation[1]**2) * currentOrientation[0] ))

        # Y rotation here
        if square[0] == currentSquare.getX():
            if square[1] > currentSquare.getY():
                selectedTroop.setOrientation((1,1))
            if square[1] < currentSquare.getY():
                selectedTroop.setOrientation((-1,-1))


        # X rotation here
        if square[1] == currentSquare.getY():
            if square[0] > currentSquare.getX():
                selectedTroop.setOrientation((1,-1))
            if square[0] < currentSquare.getX():
                selectedTroop.setOrientation((-1,1))

        
    