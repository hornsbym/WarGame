import pygame as pg

class TroopButton(object):

    def __init__(self, value, coords):
        """ value = Tuple of troop information, value[0] should correspond with a file in ./_sprites/.
           coords = Tuple describing coordinates of where the button should be drawn."""
        self.value = value
        self.coords = coords
    
    def getValue(self):
        """Returns the button's value (Troop Object)."""
        return self.value

    def showButton(self,display):
        """Accepts a pygame Display object.
           Displays the button on the provided surface"""
        img = pg.image.load('./_sprites/'+self.value[0]+'.png')
        display.blit(img, self.coords)

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area.
           Returns False if not."""
        xRange = self.coords[0] + 32
        yRange = self.coords[1] + 32

        if coords[0] > self.coords[0] and coords[0] < xRange:
            if coords[1] > self.coords[1] and coords[1] < yRange:
                return True

