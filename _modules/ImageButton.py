"""
 Author: Mitchell Hornsby
   File: ImageButton.py
Purpose: Subclass of button. Displays an images instead of text.
"""
import pygame as pg
from _modules.Button import Button

class ImageButton(Button):
    def __init__(self, image, actualValue, position, active=True):
        """     image  = Pre-loaded image that will be displayed on the actual button
          actualValue  = String that will be returned whenever the button is clicked
             position  = Tuple describing coordinates of where the button should be drawn
               active  = Boolean for whether the button can be clicked; default is True
                """
        Button.__init__(self, "", actualValue, position, None)
        self.image = image
        self.width = image.get_size()[0]
        self.height = image.get_size()[1]

    def create(self):
        """ Overrides the provided Label .create() method."""
        return

    def show(self,display):
        """Accepts a pygame Display object.
           Displays the button on the provided surface"""
        img = self.image
        img = pg.transform.rotate(img,180)
        display.blit(img, self.position)

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area, if button is active.
           Returns nothing if not."""
        xRange = self.position[0] + self.width
        yRange = self.position[1] + self.height

        if coords[0] > self.position[0] and coords[0] < xRange and self.active == True:
            if coords[1] > self.position[1] and coords[1] < yRange:
                return True