"""
 author: Mithell Hornsby
   file: Button.py
purpose: This file provides base code for a generic button class to be used in Pygame projects.
"""
import pygame as pg
from _modules.Label import Label

class Button(Label):
    def __init__(self, faceValue, actualValue, position, font, fontColor=(255,255,255), bgColor=(0,0,0), active=True):
        """ faceValue  = String that will be displayed on the actual button
          actualValue  = String that will be returned whenever the button is clicked
             position  = Tuple describing coordinates of where the button should be drawn
                 font  = Pygame Font object defining how the text should be drawn
            fontColor  = Tuple of rgb values
              bgColor  = Color that the back of the button should be
               active  = Boolean for whether the button can be clicked; default is True
               """
        Label.__init__(self, faceValue, position, font, fontColor=fontColor, bgColor=bgColor, visible=active)
        self.value = actualValue
        self.active = active
    
    def getValue(self):
        """Returns the button's value (str)."""
        return self.value
    
    def activate(self):
        """ Allows a button to be clicked.
            Also unHides the button from if the the button is hidden."""
        self.active = True
        self.unHide()

    def deactivate(self):
        """ Does not allow a button to be clicked.
            Also hides the button from view."""
        self.active = False
        self.hide()

    def isClicked(self, coords):
        """Accepts a tuple of coordinates in form (x,y).
           Returns True if the coordinates fall within the board's active area, if button is active.
           Returns False if not."""
        xRange = self.position[0] + self.getWidth()*1.3
        yRange = self.position[1] + self.getHeight()*1.3

        if coords[0] > self.position[0] and coords[0] < xRange and self.active == True:
            if coords[1] > self.position[1] and coords[1] < yRange:
                return True
        
        return False