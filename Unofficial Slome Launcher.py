import pygame
import os
import subprocess
from time import sleep
import winreg

pygame.init()
screen = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("SonicRaptor's Unofficial Slome Launcher")
pygame.display.set_icon(pygame.image.load('launcher/slomeIcon.ico'))

versionList = os.listdir('versions')

scroll = 0
versions = []
closeLauncher = True
profile = []

button = pygame.image.load('launcher/button.png')
textFont = pygame.font.SysFont(None, 40)
smallTextFont = pygame.font.SysFont(None, 30)

windowsSlomePath = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,r"Software\ZeroEightStudios\Slome")
profile = [winreg.EnumValue(windowsSlomePath, 25)[1], (winreg.EnumValue(windowsSlomePath, 26)[1], winreg.EnumValue(windowsSlomePath, 27)[1], winreg.EnumValue(windowsSlomePath, 28)[1])]

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
    screen.blit(pygame.image.load('launcher/rightSide.png'), (400,0))

    profile[0] = profile[0]
    screen.blit((smallTextFont.render(profile[0], True, (255, 255, 255))), (70, 50))
    sprite = pygame.image.load('launcher/slomePlaceholder.png').convert()
    if profile[1] == (0,0,0):
        profile[1] = (1,1,1)
    sprite.set_colorkey((0,0,0))
    pixels = pygame.PixelArray(sprite)
    pixels.replace((255,255,255), profile[1])
    temp = list(profile[1])
    x = 0
    while x < 3:
        if profile[1][x] - 55 >= 0:
            temp[x] = profile[1][x] - 55
        else:
            temp[x] = 1
        x+=1
    pixels.replace((200,200,200), (temp[0], temp[1], temp[2]))
    pixels.close()
    del(temp)
    screen.blit(sprite, (72,80))


    screen.blit((smallTextFont.render('a0.1.1', True, (255,255,255))), (14, 690))

    if closeLauncher == True:
        pygame.draw.lines(screen, [255,255,255], True, [(20,550), (40,550), (40,570), (20,570)])
    else:
        pygame.draw.rect(screen, [255,255,255], [20, 550, 20, 20])
    screen.blit((smallTextFont.render('Keep launcher open', True, (255,255,255))), (50, 552))

    x = 0
    while x < len(versionList):
        versions.append([versionList[x], ('versions/'+versionList[x] + '/Slome.exe'), 550, x * 60 + 20 + scroll])
        if len(versionList[x]) > 28:
            versions[-1][0] = versionList[x][:28] + '...'
        drawButton(versions[x][0],textFont,(255,255,255),versions[x][2], versions[x][3])
        x+=1

    mousePosition = pygame.mouse.get_pos() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0] == True:
                x = 0
                while x < len(versionList):
                    if 550 <= mousePosition[0] <= 1050 and versions[x][3] <= mousePosition[1] <= versions[x][3] + 50:
                        try:
                            subprocess.Popen(versions[x][1])
                            if closeLauncher == True:
                                sleep(0.5)
                                running = False
                        except:
                            try:
                                subprocess.Popen(str('versions/'+versionList[x] + '/survival project.exe'))
                                if closeLauncher == True:
                                    sleep(0.5)
                                    running = False
                            except:
                                try:
                                    subprocess.Popen(str('versions/'+versionList[x] + '/SlomeSlomeSlomeSlome.exe'))
                                    if closeLauncher == True:
                                        sleep(0.5)
                                        running = False
                                except:
                                    error('No Slome.exe file found at path')
                    x+=1
                if 20 <= mousePosition[0] <= 40 and 550 <= mousePosition[1] <= 570:
                    closeLauncher = not closeLauncher
        elif event.type == pygame.MOUSEWHEEL:
            if (scroll >= 0 and event.y > 0) or (versions[-1][3] <= 660 and event.y < 0):
                pass
            else:
                scroll += event.y * 15

    versions = []
    pygame.display.update()

pygame.quit()