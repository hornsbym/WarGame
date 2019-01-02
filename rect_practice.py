import pygame as pg
import time
import random

pg.init()
clock = pg.time.Clock()
displayWidth = 200
displayHeight = 150
display = pg.display.set_mode((displayWidth,displayHeight),pg.RESIZABLE)
display.fill((255,255,255))

rect_one = pg.Rect(0,0,displayWidth//3,displayHeight)
rect_two = pg.Rect(displayWidth//3, 0,  displayWidth//3, displayHeight)
rect_three = pg.Rect(2*(displayWidth//3), 0,  displayWidth//3, displayHeight)

def main():
    update_list = [rect_one,rect_two,rect_three]
    while(True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                x = pg.mouse.get_pos()[0]
                if x > 0 and x < displayWidth//3:
                    if rect_one in update_list:
                        update_list.remove(rect_one)
                    else:
                        update_list.append(rect_one)
                if x > displayWidth//3 and x < 2*(displayWidth//3):
                    if rect_two in update_list:
                        update_list.remove(rect_two)
                    else:
                        update_list.append(rect_two)
                if x > 2*(displayWidth//3):
                    if rect_three in update_list:
                        update_list.remove(rect_three)
                    else:
                        update_list.append(rect_three)
    
        if len(update_list) != 0:
            color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))

        pg.draw.rect(display,color,(0,displayHeight//4,displayWidth,displayHeight//2))

        pg.display.update(update_list)

        clock.tick(5)

main()
quit()