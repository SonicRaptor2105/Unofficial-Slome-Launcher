import pygame
import os
import subprocess
import time
import winreg
import json

launcherVersion = 'a0.1.7'

pygame.init()
screen = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("SonicRaptor's Unofficial Slome Launcher")
pygame.display.set_icon(pygame.image.load('launcher/slomeIcon.ico'))

versionList = os.listdir('versions')

scroll = 0
versions = []
closeLauncher = True

profileSelected = 0
allProfiles = [[]]
currentProfile = []

sprite = pygame.image

sliderSelected = 0
sliding = False
inputSelected = 0
inputNumber = False
rgbTestValue = 0
inputUsername = False
usernameTestValue = ''
cursorPosition = 0
bigSlome = False

rgbKeyValues = ['colour_r_h2463154688','colour_g_h2463154709','colour_b_h2463154704']

windowsSlomePath = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,r"Software\ZeroEightStudios\Slome")
currentProfile = [winreg.EnumValue(windowsSlomePath, 25)[1].decode('utf-8').rstrip('\x00'), (winreg.EnumValue(windowsSlomePath, 26)[1], winreg.EnumValue(windowsSlomePath, 27)[1], winreg.EnumValue(windowsSlomePath, 28)[1])]
windowsSlomePath.Close

button = pygame.image.load('launcher/button.png')
textFont = pygame.font.SysFont(None, 40)
smallTextFont = pygame.font.SysFont(None, 30)

def syncValues():
    global allProfiles, profileSelected, closeLauncher
    profiles = open('launcher/profiles.dat', 'r').readlines()
    allProfiles = [[], [], [], [], [], [], [], [], [], []]
    x=0
    while x < 10:
        allProfiles[x] = [profiles[x].replace('\n','').replace('[','').replace(']','')]
        try:
            allProfiles[x] = list(eval(allProfiles[x][0]))
        except:
            allProfiles[x] = []
        x+=1
    profileSelected = int(profiles[10])
    if profiles[11] == 'True':
        closeLauncher = True
    else:
        closeLauncher = False
    checkWinReg()
    return

def checkWinReg():
    global currentProfile
    windowsSlomePath = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,r"Software\ZeroEightStudios\Slome")
    currentProfile = [winreg.EnumValue(windowsSlomePath, 25)[1].decode('utf-8').rstrip('\x00'), (winreg.EnumValue(windowsSlomePath, 26)[1], winreg.EnumValue(windowsSlomePath, 27)[1], winreg.EnumValue(windowsSlomePath, 28)[1])]
    windowsSlomePath.Close

def saveToWinReg():
    winregWrite = winreg.OpenKeyEx(winreg.HKEY_CURRENT_USER,r"Software\ZeroEightStudios\Slome", 0, winreg.KEY_WRITE)
    x = 0
    while x < 3:
        winreg.SetValueEx(winregWrite, rgbKeyValues[x], 0, winreg.REG_DWORD, currentProfile[1][x])
        x+=1
    winreg.SetValueEx(winregWrite, 'username_h2363791411', 0, winreg.REG_BINARY, currentProfile[0].encode('utf-8'))
    winregWrite.Close

def saveProfiles():
    global currentProfile
    currentProfile = allProfiles[profileSelected]
    read = open('launcher/profiles.dat', 'r').readlines()
    profileDictionary = {}
    x=0
    while x < 10:
        read[x] = str(allProfiles[x]) + '\n'
        profileDictionary[f'profile_{x}'] = allProfiles[x]
        x+=1
    read[10] = str(profileSelected) + '\n'
    read[11] = str(closeLauncher)
    profileDictionary['profileSelected'] = profileSelected
    profileDictionary['closeLauncher'] = closeLauncher

    with open('launcher/data.txt', "w") as file:
        json.dump(profileDictionary, file)
        
    with open('launcher/data.txt', "r") as file:
        profileDictionary = json.load(file)

    with open('launcher/profiles.dat', 'w') as write:
        write.writelines(read)
    return

def drawButton(text, font, textColour, x, y):
    screen.blit(button, [x, y])
    displayName = font.render(text, True, textColour)
    screen.blit(displayName, (x + 10, y + 10))

def error(message):
    pygame.draw.rect(screen, (0,0,0), [573 - len(message) * 8 - 50, 290, 600, 50])
    screen.blit((textFont.render(f'Error: {message}', True, (255,0,0))), (573 - len(message) * 8, 300))
    pygame.display.update()
    time.sleep(0.8)
    return

def drawUsername():
    overlay = pygame.Surface((250, 25), pygame.SRCALPHA)
    overlay.fill((255,255,255,80))
    screen.blit(overlay, (70, 47))
    screen.blit((smallTextFont.render(currentProfile[0], True, (255, 255, 255))), (70, 50))
    return

def drawSlome():
    sprite = pygame.image.load('launcher/slomePlaceholder.png').convert()
    if currentProfile[1] == (0,0,0):
        currentProfile[1] = (1,1,1)
    sprite.set_colorkey((0,0,0))
    pixels = pygame.PixelArray(sprite)
    pixels.replace((255,255,255), currentProfile[1])
    temp = list(currentProfile[1])
    x=0
    while x < 3:
        if currentProfile[1][x] - 55 >= 0:
            temp[x] = currentProfile[1][x] - 55
        else:
            temp[x] = 1
        x+=1
    pixels.replace((200,200,200), (temp[0], temp[1], temp[2]))
    pixels.close()
    del(temp)
    screen.blit(sprite, (72,80))
    if bigSlome:
        sprite = pygame.transform.scale(sprite, (280, 280))
        screen.blit(sprite, (57,65))
    return

def drawSlider():
    x=0
    while x < 3:
        pygame.draw.rect(screen, [255,255,255], [40, (350 + x * 35), 255, 4])
        pygame.draw.rect(screen, [255,255,255], [40 + currentProfile[1][x], (342 + x * 35), 5, 20])
        pygame.draw.rect(screen, [30,30,30], [320, (340 + x * 35), 45, 24])
        screen.blit(smallTextFont.render(str(currentProfile[1][x]), True, (255,255,255)), (325, 343 + x * 35))
        x+=1
    return

def profileMenu():
    global bigSlome, inputNumber, rgbTestValue, inputUsername, sliderSelected, sliding, inputSelected, usernameTestValue, profileSelected, allProfiles, currentProfile
    bigSlome = False

    syncValues()

    profileMenuRunning = True
    while profileMenuRunning == True:
        pygame.draw.rect(screen, [0,0,0], [0,0,1200,720])
        screen.blit(pygame.image.load('launcher/largeMenu.png'), (15,15))
        screen.blit((smallTextFont.render(f'Profile: {profileSelected}', True, (255, 255, 255))), (26, 674))
        drawUsername()
        drawSlome()
        drawSlider()
        pygame.draw.polygon(screen, [255,255,255], [(332, 175), (352, 195), (332, 215)])
        pygame.draw.polygon(screen, [255,255,255], [(57, 175), (37, 195), (57, 215)])

        mousePosition = pygame.mouse.get_pos() 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] == True:
                    inputNumber = False
                    rgbTestValue = 0
                    inputUsername = False
                    if 40 <= mousePosition[0] <= 295 and 300 <= mousePosition[1] <= 700:
                        x=0
                        while x < 3:
                            if 40 <= mousePosition[0] <= 295 and (340 + x * 35) <= mousePosition[1] <= (360 + x * 35):
                                sliderSelected = x
                                sliding = True
                            x+=1
                    elif 320 <= mousePosition[0] <= 365 and 340 <= mousePosition[1] <= 445:
                        x=0
                        while x < 3:
                            if 320 <= mousePosition[0] <= 365 and (340 + x * 35) <= mousePosition[1] <= (364 + x * 35):
                                inputSelected = x
                                inputNumber = True
                            x+=1
                    elif 70 <= mousePosition[0] <= 320 and 47 <= mousePosition[1] <= 72:
                        inputUsername = True
                        usernameTestValue = currentProfile[0]
                    elif 37 <= mousePosition[0] <= 352 and  175 <= mousePosition[1] <= 215:
                        allProfiles[profileSelected] = currentProfile
                        if 37 <= mousePosition[0] <= 57:
                            profileSelected -= 1
                            if profileSelected < 0:
                                profileSelected = 0
                        elif 332 <= mousePosition[0] <= 352:
                            profileSelected += 1
                            if profileSelected > 9:
                                profileSelected = 9
                        if allProfiles[profileSelected] == []:
                            allProfiles[profileSelected] = [f'Profile {profileSelected}', (255,255,255)]
                        saveProfiles()
                        saveToWinReg()
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                sliding = False

            elif event.type == pygame.MOUSEMOTION:
                if sliding == True:
                    tempProfile = list(currentProfile[1])
                    tempProfile[sliderSelected] = min(255, max(0, (mousePosition[0] - 40)))
                    currentProfile[1] = tuple(tempProfile)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return()
                if inputNumber == True:
                    if pygame.K_0 <= event.key <= pygame.K_9:
                        rgbTestValue = int(str(rgbTestValue) + str(event.key - pygame.K_0))
                        if rgbTestValue > 255:
                            rgbTestValue = 255
                    elif event.key == pygame.K_BACKSPACE:
                        if rgbTestValue >= 10:
                            rgbTestValue = int(str(rgbTestValue)[:-1])
                        else:
                            rgbTestValue = 0
                    elif event.key == pygame.K_RETURN:
                        inputNumber = False
                        break
                    tempProfile = list(currentProfile[1])
                    tempProfile[inputSelected] = rgbTestValue
                    currentProfile[1] = tuple(tempProfile)
                elif inputUsername == True:
                    if event.key == pygame.K_BACKSPACE:
                        usernameTestValue = usernameTestValue[:-1]
                    elif pygame.K_a <= event.key <= pygame.K_z or pygame.K_0 <= event.key <= pygame.K_9 or event.unicode in "!@#$%^&*()_-+={}[]\|:;\"'><,.?/~` ":
                        if len(usernameTestValue) <= 21:
                            usernameTestValue = usernameTestValue + event.unicode
                    currentProfile[0] = usernameTestValue

        if inputNumber == True:
            overlay = pygame.Surface((45, 24), pygame.SRCALPHA)
            overlay.fill((255,255,255,120))
            screen.blit(overlay, (320, (340 + inputSelected * 35)))

        elif inputUsername == True:
            overlay = pygame.Surface((250, 25), pygame.SRCALPHA)
            overlay.fill((255,255,255,120))
            screen.blit(overlay, (70, 47))

        if sliding == True or inputNumber == True or inputUsername == True:
            saveToWinReg()
            allProfiles[profileSelected] = currentProfile
            saveProfiles()
        
        pygame.display.update()



syncValues()
running = True
while running:
    screen.fill('white')
    screen.blit(pygame.image.load('launcher/leftSide.png'), (0,0))
    screen.blit(pygame.image.load('launcher/rightSide.png'), (400,0))

    drawUsername()
    drawSlome()

    screen.blit((smallTextFont.render(launcherVersion, True, (255,255,255))), (14, 690))

    if closeLauncher == True:
        pygame.draw.lines(screen, [255,255,255], True, [(20,420), (40,420), (40,400), (20,400)])
    elif closeLauncher == False:
        pygame.draw.rect(screen, [255,255,255], [20, 400, 20, 20])
    screen.blit((smallTextFont.render('Keep launcher open', True, (255,255,255))), (50, 402))

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
                inputNumber = False
                rgbTestValue = 0
                inputUsername = False
                if mousePosition[0] > 400:
                    x = 0
                    while x < len(versionList):
                        if 550 <= mousePosition[0] <= 1050 and versions[x][3] <= mousePosition[1] <= versions[x][3] + 50:
                            try:
                                subprocess.Popen(versions[x][1])
                                if closeLauncher == True:
                                    time.sleep(2)
                                    running = False
                            except:
                                try:
                                    subprocess.Popen(str('versions/'+versionList[x] + '/survival project.exe'))
                                    if closeLauncher == True:
                                        time.sleep(2)
                                        running = False
                                except:
                                    try:
                                        subprocess.Popen(str('versions/'+versionList[x] + '/SlomeSlomeSlomeSlome.exe'))
                                        if closeLauncher == True:
                                            time.sleep(2)
                                            running = False
                                    except:
                                        error('No Slome.exe file found at path')
                        x+=1
                elif 20 <= mousePosition[0] <= 40 and 400 <= mousePosition[1] <= 420:
                    closeLauncher = not closeLauncher
                    saveProfiles()
                elif 72 <= mousePosition[0] <= 322 and 80 <= mousePosition[1] <= 330:
                    profileMenu()
                
        elif event.type == pygame.MOUSEMOTION:
            if 72 <= mousePosition[0] <= 322 and 80 <= mousePosition[1] <= 330:
                bigSlome = True
            else:
                bigSlome = False

        elif event.type == pygame.MOUSEWHEEL:
            if (scroll >= 0 and event.y > 0) or (versions[-1][3] <= 660 and event.y < 0):
                pass
            else:
                scroll += event.y * 15

    versions = []
    pygame.display.update()

pygame.quit()