import pygame
import os
import subprocess
from time import sleep

pygame.init()
screen = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("SonicRaptor's Unofficial Slome Launcher")
pygame.display.set_icon(pygame.image.load('launcher/icon.ico'))

versionList = os.listdir('versions')

scroll = 0
versions = []
closeLauncher = True

button = pygame.image.load('launcher/button.png')
textFont = pygame.font.SysFont(None, 40)
smallTextFont = pygame.font.SysFont(None, 30)
def drawButton(text, font, textColour, x, y):
    screen.blit(button, [x, y])
    displayName = font.render(text, True, textColour)
    screen.blit(displayName, (x + 10, y + 10))

def error(message):
    pygame.draw.rect(screen, (0,0,0), [573 - len(message) * 8 - 50, 290, 600, 50])
    screen.blit((textFont.render(f'Error: {message}', True, (255,0,0))), (573 - len(message) * 8, 300))
    pygame.display.update()
    sleep(0.8)
    return



running = True
while running:
    screen.fill('white')
    screen.blit(pygame.image.load('launcher/leftSide.png'), (0,0))
    screen.blit((smallTextFont.render('a0.1.0', True, (0,0,0))), (8, 695))

    if closeLauncher == True:
        screen.blit((smallTextFont.render('Keep launcher open', True, (0,0,0))), (50, 402))
        pygame.draw.lines(screen, [0,0,0], True, [(20,420), (40,420), (40,400), (20,400)])
    else:
        screen.blit((smallTextFont.render('Keep launcher open', True, (0,0,0))), (50, 402))
        pygame.draw.rect(screen, [0, 0, 0], [20, 400, 20, 20])

    x = 0
    while x < len(versionList):
        versions.append([versionList[x], ('versions/'+versionList[x] + '/Slome.exe'), 600, x * 60 + 20 + scroll])
        if len(versionList[x]) > 28:
            versions[-1][0] = versionList[x][:28] + '...'
        drawButton(versions[x][0],textFont,(0,0,0),versions[x][2], versions[x][3])
        x+=1

    mousePosition = pygame.mouse.get_pos() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] == True:
                x = 0
                while x < len(versionList):
                    if 600 <= mousePosition[0] <= 1100 and versions[x][3] <= mousePosition[1] <= versions[x][3] + 50:
                        try:
                            subprocess.Popen(versions[x][1])
                            if closeLauncher == True:
                                running = False
                        except:
                            try:
                                subprocess.Popen(str('versions/'+versionList[x] + '/survival project.exe'))
                                if closeLauncher == True:
                                    running = False
                            except:
                                try:
                                    subprocess.Popen(str('versions/'+versionList[x] + '/SlomeSlomeSlomeSlome.exe'))
                                    if closeLauncher == True:
                                        running = False
                                except:
                                    error('No Slome.exe file found at path')
                    x+=1
                if 20 <= mousePosition[0] <= 40 and 400 <= mousePosition[1] <= 420:
                    closeLauncher = not closeLauncher
        elif event.type == pygame.MOUSEWHEEL:
            scroll += event.y * 15
            if scroll >= 0:
                scroll = 0
            elif versions[-1][3] <= 660:
                scroll += 15

    versions = []
    pygame.display.update()

pygame.quit()