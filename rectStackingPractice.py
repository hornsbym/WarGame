import pygame as pg
import time
from _modules.CommandButton import CommandButton as CB

pg.init()
clock = pg.time.Clock()
displayWidth = 500
displayHeight = 500
display = pg.display.set_mode((displayWidth,displayHeight),pg.RESIZABLE)
display.fill((110,110,110))

DEFAULT_FONT   = pg.font.SysFont(None, 25)

rect_one = pg.Rect(0,0, 2*displayWidth//3,displayHeight)
rect_two = pg.Rect(displayWidth//3, 0,  2*displayWidth//3, displayHeight)

redButton = CB("red", (0,0), (90,90,90), DEFAULT_FONT)
blueButton = CB("blue", (displayWidth-50, 0), (90,90,90), DEFAULT_FONT)


def main():
    selectedPane = "red"
    while(True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                coords = pg.mouse.get_pos()
                if redButton.isClicked(coords):
                    selectedPane = redButton.getValue()
                if blueButton.isClicked(coords):
                    selectedPane = blueButton.getValue()

    
        if selectedPane == "red":
            pg.draw.rect(display, (90,90,255),rect_two)
            pg.draw.rect(display, (255,90,90),rect_one)
        if selectedPane == "blue":
            pg.draw.rect(display, (255,90,90),rect_one)
            pg.draw.rect(display, (90,90,255),rect_two)

        redButton.showButton(display)
        blueButton.showButton(display)
        

        pg.display.update()

        clock.tick(5)

main()
quit()