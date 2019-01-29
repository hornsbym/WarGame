import pygame as pg

class TroopButton(object):

    def __init__(self, value, coords, active=True):
        """ value = Tuple of troop information, value[0] should correspond with a file in ./_sprites/.
           coords = Tuple describing coordinates of where the button should be drawn.
           active = Boolean for whether the button can be presses."""
        self.value = value
        self.coords = coords
        self.active = active
    
    def getValue(self):
        """Returns the button's value (Troop Object)."""
        return self.value

    def activate(self):
        """Allows a button to be clicked"""
        self.active = True

    def deactivate(self):
        """Does not allow a button to be clicked"""
        self.active = False

    def showButton(self,display):
        """Accepts a pygame Display object.
           Displays the button on the provided surface"""
        img = pg.image.load('./_sprites/'+self.value[0]+'.png')
        img = pg.transform.rotate(img,180)
        display.blit(img, self.coords)

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area, if the button is active.
           Returns nothing if not."""
        xRange = self.coords[0] + 32
        yRange = self.coords[1] + 32

        if self.active == True:
            if coords[0] > self.coords[0] and coords[0] < xRange:
                if coords[1] > self.coords[1] and coords[1] < yRange:
                    return True

