import pygame as pg

class CommandButton(object):

    def __init__(self, value, coords, color, active=True):
        """ value  = String
           coords  = Tuple describing coordinates of where the button should be drawn
            color  = Tuple of rgb values
            active = Boolean for whether the button can be clicked; default is True"""
        self.value = value
        self.coords = coords
        self.color = color
        self.active = active

        self.surface = None
        self.width = None
        self.height = None

        self.makeButton()
    
    def getValue(self):
        """Returns the button's value (str)."""
        return self.value
    
    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height
    
    def activate(self):
        """Allows a button to be clicked"""
        self.active = True

    def deactivate(self):
        """Does not allow a button to be clicked"""
        self.active = False
        
    def makeButton(self):
        """Creates the button."""
        font = pg.font.SysFont(None, 25)
        self.surface = font.render(self.value, True, (255,255,255))

        self.width = self.surface.get_width()
        self.height = self.surface.get_height()

    def showButton(self,display):
        """Accepts a pygame Display object.
           Displays the button on the provided surface"""
        pg.draw.rect(display, self.color, (self.coords[0], self.coords[1], self.width*1.3, self.height*1.3))
        display.blit(self.surface, (self.coords[0]+.1*self.width, self.coords[1]+.2*self.height))

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area, if button is active.
           Returns nothing if not."""
        xRange = self.coords[0] + self.getWidth()*1.3
        yRange = self.coords[1] + self.getHeight()*1.3

        if coords[0] > self.coords[0] and coords[0] < xRange and self.active == True:
            if coords[1] > self.coords[1] and coords[1] < yRange:
                return True