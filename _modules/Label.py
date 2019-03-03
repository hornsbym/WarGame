"""
 author: Mitchell Hornsby
   file: Label.py
purpose: Provides an object that displays text on a Pygame surface.
"""
import pygame as pg

class Label(object):
    def __init__(self, text, position, font, fontColor=(0,0,0), bgColor=(255,255,255), padding=(10, 6), transparent=False, visible=True):
        """     text = String describing what to write
            position = Tuple of x-y values describing where to create the label
                font = Pygame Font object describing how to write the text
           fontColor = (Optional) Color the text should appear as
             bgColor = (Optional) Background color the text should be mounted on 
             padding = (Optional) Tuple describing how much space should be between the text and the border
        """
        self.text = text
        self.position = position
        self.font = font
        self.fontColor = fontColor
        self.bgColor = bgColor
        self.xPadding = padding[0]
        self.yPadding = padding[1]

        self.transparent = transparent
        self.visible = visible

        self.surface = None
        self.textWidth = None
        self.textHeight = None
        self.width = None
        self.height = None

        self.create()

    def __str__(self):
        """ For testing purposes."""
        return "<Label text:'%s' position:(%i, %i)>" % (self.text, self.position[0], self.position[1])
    
    def getWidth(self):
        """ Returns Int."""
        return self.width
    
    def getHeight(self):
        """ Returns Int."""
        return self.height

    def getTextWidth(self):
        """Returns Int."""
        return self.textWidth

    def getTextHeight(self):
        """Returns Int."""
        return self.textHeight

    def getPosition(self):
        """Returns tuple of form (x, y)"""
        return self.position

    def hide(self):
        """ Tells the widget not to show itself."""
        self.visible = False
    
    def unHide(self):
        """ Tells the widget to show itself."""
        self.visible = True

    def move(self, newCoords):
        """ Accepts a tuple of x-y values.
            Moves the label to that new position."""
        self.position = newCoords
        self.create()

    def create(self):
        """ Creates the label upon initilization."""
        font = self.font
        self.surface = font.render(self.text, True, self.fontColor)

        self.textWidth = self.surface.get_width()
        self.textHeight = self.surface.get_height()

        self.width = self.textWidth + self.xPadding
        self.height = self.textHeight + self.yPadding
    
    def show(self, display):
        """ Accepts a Pygame display.
            Draws the label on the provided display.
            If position is 'None', this methods does nothing."""
        if self.visible == True:
            if self.position != None:
                if self.transparent == False:
                    pg.draw.rect(display, self.bgColor, (self.position[0], self.position[1], self.width, self.height))

                display.blit(self.surface, (self.position[0] + self.xPadding/2, self.position[1] + self.yPadding/2))

    def updateText(self, string):
        """ Accepts a String.
            Changes the label's text to reflect this string."""
        self.text = string
        self.create()