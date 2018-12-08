import pygame as pg

class CommandButton(object):

    def __init__(self, value, coords, color):
        """ value = String
           coords = Tuple describing coordinates of where the button should be drawn
            color = Tuple of rgb values"""
        self.value = value
        self.coords = coords
        self.color = color
    
    def getValue(self):
        """Returns the button's value (str)."""
        return self.value

    def showButton(self,display):
        """Accepts a pygame Display object.
           Displays the button on the provided surface"""
        pg.draw.rect(display, self.color, (self.coords[0], self.coords[1], 75, 30))
        font = pg.font.SysFont(None, 25)
        text = font.render(self.value, True, (255,255,255))
        display.blit(text, (self.coords[0], self.coords[1]))

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area.
           Returns False if not."""
        xRange = self.coords[0] + 75
        yRange = self.coords[1] + 30

        if coords[0] > self.coords[0] and coords[0] < xRange:
            if coords[1] > self.coords[1] and coords[1] < yRange:
                return True