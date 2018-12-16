import pygame as pg
from Troop import Troop

# squareImg = pg.image.load("./_sprites/square.jpg")

class Square(object):
    """Contains information about a single square on the game board."""

    def __init__(self, x, y, coords):
        """     x = Integer for the square's horizontal position 
                    (relative to the other squares on the board.)
                y = Integer for the square's vertical position 
                    (relative to the other squares on the board.)
           coords = Tuple containing the starting position for the 
                    board as a whole, not individual squares."""
        self.x = x
        self.y = y
        self.coords = coords
        self.icon = "square"
        self.troop = None
        self.color = ""

    def getX(self):
        """Returns the square's x-value."""
        return self.x

    def getY(self):
        """Returns the square's y-value"""
        return self.y
    
    def getTroop(self):
        """Returns the square's troop object."""
        return self.troop
    
    def setIcon(self):
        """Accepts a string.
           Sets that string as the square's icon attribute."""
        self.icon = self.troop.getColor()+self.troop.getName()

    def setColor(self,color):
        """Accepts a string.
           This string represents the color of the occupying team."""
        self.color = color
    
    def setTroop(self, troop):
        """Accepts a Troop object.
           Stores that Troop object in the state variables.
           Also resets the square's icon to reflect the appropriate troop."""      
        self.troop = troop
        
        if troop == None:
            self.icon = 'square'
            return
            
        self.setIcon()

    def showSquare(self,display):
        """Accepts a pygame Display object as an argument.
           Shows the square in that display.
           Handles rotations."""
        img = pg.image.load("./_sprites/"+self.icon+".png")

        # Handles rotations
        if self.getTroop() != None:
            orientation = self.getTroop().getOrientation()
            if orientation == (1,1):
                img = pg.transform.rotate(img, 0)
            if orientation == (1,-1):
                img = pg.transform.rotate(img, 90)
            if orientation == (-1,1):
                img = pg.transform.rotate(img, -90)
            if orientation == (-1,-1):
                img = pg.transform.rotate(img, 180)
        
        display.blit(img, (self.coords[0] + (self.x * 32), self.coords[1] + ( self.y * 32)))

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area.
           Returns False if not."""
        xRange = self.coords[0] + (self.x * 32) +32
        yRange = self.coords[1] + ( self.y * 32) +32

        if coords[0] > self.coords[0] and coords[0] < xRange:
            if coords[1] > self.coords[1] and coords[1] < yRange:
                return True
        
        return False

    def killTroop(self):
        """Checks whether the square's troop's heath has reached 0.
           If so, resets the square to its base state."""
        if self.getTroop().getHealth() <= 0:
            self.icon = "square"
            self.troop = None

