
import random

pg.init()
clock = pg.time.Clock()
displayWidth = 200
displayHeight = 150
display = pg.display.set_mode((displayWidth,displayHeight),pg.RESIZABLE)
display.fill((255,255,255))

def main():
    colorNames  = ['r','g','b']
    colorValues = {"r":0,"g":0,"b":0}

    colorA = 'r'
    colorB = 'g'
    colorC = 'b'

    track = 'lighten'

    while(True):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        if track == 'lighten':
            print("A")
            a = colorValues[colorA]
            b = colorValues[colorB]
            c = colorValues[colorC]

            if a == 255 and b == 255 and c == 255:
                print("B")
                colors = colorNames 

                colorA = random.choice(colors)
                colors.remove(colorA)
                colorB = random.choice(colors)
                colors.remove(colorB)
                colorC = random.choice(colors)
                colors.remove(colorC)

                track = 'darken'
            
            if a < 255:
                print("C")
                colorValues[colorA] += 1
            
            if a == 255 and b < 255:
                print("D")
                colorValues[colorB] += 1
            
            if a == 255 and b == 255 and c < 255:
                print("E")
                colorValues[colorC] += 1


        if track == 'darken':
            a = colorValues[colorA]
            b = colorValues[colorB]
            c = colorValues[colorC]

            if a == 0 and b == 0 and c == 0:
                colors = colorNames 

                colorA = random.choice(colors)
                colors.remove(colorA)
                colorB = random.choice(colors)
                colors.remove(colorB)
                colorC = random.choice(colors)
                colors.remove(colorC)

                track = 'lighten'

            if a > 0:
                colorValues[colorA] -= 1
            
            if a == 0 and b > 0:
                colorValues[colorB] -= 1
            
            if a == 0 and b == 0 and c > 0:
                colorValues[colorC] -= 1
            
        color = (a,b,c)
        # print(track+'ing:', color)
        
        display.fill(color)
        pg.display.update()

        clock.tick(60)

main()
quit()