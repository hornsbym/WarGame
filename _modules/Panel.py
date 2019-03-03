"""
 Author: Mitchell Hornsby
   File: Panel.py
Purpose: Provide framework for placing items within a size-specified container.
"""
import pygame as pg

class Panel(object):
    def __init__ (self, position, dimensions, bgColor=(255,255,255), visible=True):
        """   position: Tuple of (x, y) values for the upper-left corner of the panel
            dimensions: Tuple of (width, height) values"""
        self.position = position
        self.dimensions = dimensions
        self.bgColor = bgColor
        self.width, self.height = dimensions
        self.visible = True

        self.panel = None
        self.elements = []
    
        self.create()

    def __str__(self):
        """ For testing purposes."""
        return "<Panel position:(%i, %i)>" % (self.position[0], self.position[1])

    def getWidth(self):
        """ Returns int"""
        return self.width
    
    def getHeight(self):
        """ Returns int"""
        return self.height
    
    def getPosition(self):
        """Returns tuple of form (x, y)"""
        return self.position

    def create(self):
        """ Initializes the Pygame rect object."""
        self.panel = pg.rect.Rect(self.position, self.dimensions)  
    
    def hide(self):
        """ Tells the panel to blit."""
        self.visible = False

    def unHide(self):
        """ Tells the panel not to blit."""
        self.visible = True

    def show(self, display):
        """ Accepts a Pygame display object.
            Shows the pygame rect object on the given display if the panel is visible."""
        if self.visible == True:
            pg.draw.rect(display, self.bgColor, self.panel)

            for element in self.elements:
                element.show(display)
        
    def addElement(self, element, position):
        """ Accepts either a Label, Button, or Panel.
            Accepts a tuple describing where the element should appear relative to the Panel's upper-left corner.
            Positions the elements within the panel.
        """
        xOffset, yOffset = position
        element.move((self.position[0] + xOffset, self.position[1] + yOffset))
        self.elements.append(element)
        
    def move(self, newPosition):
        """ Accepts a tuple of form (x, y).
            Shifts the panel and all contained elements to that new location."""
        oldPosition = self.position
        self.position = newPosition

        xOffset = newPosition[0] - oldPosition[0]
        yOffset = newPosition[1] - oldPosition[1]

        for element in self.elements:
            element.move((element.getPosition()[0] + xOffset, element.getPosition()[1] + yOffset))
        
        self.create()
