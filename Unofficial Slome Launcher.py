import pygame
import os
import time
import winreg
import json
import win32gui
import win32process
import psutil
import re
import shutil

launcherVersion = 'a0.1.8'

pygame.init()
screen = pygame.display.set_mode((1200, 720))
pygame.display.set_caption("SonicRaptor's Unofficial Slome Launcher")
pygame.display.set_icon(pygame.image.load('launcher/slomeIcon.ico'))

versionList = os.listdir('versions')

scroll = 0
versions = []

profileDictionary = {}
currentProfile = []

loops = 0
versionLoaded = ''
versionKeyword = ''

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
localLowFilePath = os.getenv('USERPROFILE')+'\AppData\LocalLow'

button = pygame.image.load('launcher/button.png')
textFont = pygame.font.SysFont(None, 40)
smallTextFont = pygame.font.SysFont(None, 30)

def syncValues():
    global profileDictionary
    try:
        with open('launcher/config.json', "r") as file:
            profileDictionary = json.load(file)
    except:
        newConfig = {'profile_0' : ['New_Profile',(255,0,0)], 'profile_1' : [], 'profile_2' : [], 'profile_3' : [], 'profile_4' : [], 'profile_5' : [], 'profile_6' : [], 'profile_7' : [], 'profile_8' : [], 'profile_9' : [], 'profileSelected': 0, 'closeLauncher': True, 'useLauncherSaves' : False}
        with open('launcher/config.json', "w") as file:
            json.dump(newConfig, file)
        profileDictionary = newConfig    
    x=0
    while x < 10:
        try:
            profileDictionary[f'profile_{x}'][1] = tuple(profileDictionary[f'profile_{x}'][1])
        except:
            pass
        x+=1
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
    global profileDictionary, currentProfile
    currentProfile = profileDictionary[f'profile_{profileDictionary['profileSelected']}']
    with open('launcher/config.json', "w") as file:
        json.dump(profileDictionary, file)    
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
    if inputUsername == False:
        screen.blit((smallTextFont.render(currentProfile[0], True, (255, 255, 255))), (70, 50))
    else:
        screen.blit((smallTextFont.render(currentProfile[0] + '|', True, (255, 255, 255))), (70, 50))
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

def swapBetweenLauncherSaving(useLauncherSaving):
    dirs = ['\Robotnik08\Slome\saves', '\ZeroEightStudios\Slome\saves', '\ZeroEightStudios\SlomeSlomeSlomeSlome\saves']
    if useLauncherSaving == True:
        if not os.path.exists('launcher\saves'):
            os.makedirs('launcher\saves')
        x = 0
        while x < len(dirs):
            try:
                shutil.copytree(localLowFilePath + dirs[x], 'launcher\saves', copy_function=shutil.copy2, dirs_exist_ok=True)
                shutil.rmtree(localLowFilePath + dirs[x])
            except:
                pass
            os.symlink(os.getcwd() + '\launcher\saves', localLowFilePath + dirs[x], target_is_directory=True)
            x+=1
    elif useLauncherSaving == False:
        x = 0
        while x < len(dirs):
            os.unlink(localLowFilePath + dirs[x])
            os.makedirs(localLowFilePath + dirs[x])
            x+=1
        saves = os.listdir('launcher\saves')
        print(saves)
        rSlome = []
        z8Slome = []
        z8Slomex4 = []
        x = 0
        while x < len(saves):
            try:
                with open(f'launcher\saves\{saves[x]}\latestLaunch.txt') as file:
                    line = file.readline()
                    if 'pre' in line:
                        rSlome.append(saves[x])
                    elif '+' in line:
                        z8Slomex4.append(saves[x])
                    else:
                        z8Slome.append(saves[x])
            except:
                z8Slome.append(saves[x])
            x+=1
        x = 0
        while x < len(rSlome):
            shutil.copytree(f'launcher\saves\{rSlome[x]}', localLowFilePath + f'\Robotnik08\Slome\saves\{rSlome[x]}', copy_function=shutil.copy2, dirs_exist_ok=True)
            x+=1
        x = 0
        while x < len(z8Slome):
            shutil.copytree(f'launcher\saves\{z8Slome[x]}', localLowFilePath + f'\ZeroEightStudios\Slome\saves\{z8Slome[x]}', copy_function=shutil.copy2, dirs_exist_ok=True)
            x+=1
        x = 0
        while x < len(z8Slomex4):
            shutil.copytree(f'launcher\saves\{z8Slomex4[x]}', localLowFilePath + f'\ZeroEightStudios\SlomeSlomeSlomeSlome\saves\{z8Slomex4[x]}', copy_function=shutil.copy2, dirs_exist_ok=True)
            x+=1
            
    return

def checkLoadedVersion(versionPath):
    global versionLoaded, versionKeyword
    with open(versionPath,'rb') as findVersion:
        findVersion = findVersion.readlines()
        x = 0       
        while x < len(findVersion):
            checkVersion = findVersion[x].decode('UTF-8','ignore').lower().replace('\x00','')
            checkVersion = re.sub(r'[^\x20-\x7E]', '', checkVersion)
            if 'pre-demo' in  checkVersion:
                versionKeyword = 'pre-demo'
                break
            elif 'pre-indev' in checkVersion:
                versionKeyword = 'pre-indev'
                break
            elif 'indev' in checkVersion:
                versionKeyword = 'indev'
                break
            elif 'alpha' in checkVersion:
                versionKeyword = 'alpha'
                break
            elif 'ff@' in checkVersion:
                #This is if Robotnik decides to swap his naming convention for no reason 2 years into the project
                versionKeyword = 'ff@'
                break
            x+=1
        print(versionKeyword)
    if versionKeyword == '' or len(versionKeyword) > 12:
        versionLoaded = 'Unknown or Modified version'
    else:
        if versionKeyword == 'ff@':
            endPos = checkVersion.find('ff')
            for i in range(endPos -1, -1, -1):
                if not checkVersion[i].isdigit() and not checkVersion[i] == '' and not checkVersion[i] == '.':
                    versionLoaded = checkVersion[i + 1 : endPos]
                    versionLoaded = 'alpha ' + versionLoaded
                    break
        else:
            versionLoaded = checkVersion[checkVersion.find(versionKeyword) : checkVersion.find('ff')].strip()
    return()


def checkForFileUpdates():
    global loops, versionLoaded, versionKeyword
    loops+=1
    if loops < 1000:
        return
    else:
        versionPath = ''
        slomeVersion = ''
        worldSave = ''
        logLocation = ''

        try:
            _, currentOpenWindow = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
            process = psutil.Process(currentOpenWindow).exe()
            print(process)
            if 'slome' in process.lower():
                if 'unofficial slome launcher' in process.lower():
                    if 'slomeslomeslomeslome' in process.lower():
                        versionPath = process[process.find('versions') : process.find('\\SlomeSlomeSlomeSlome.exe')]
                        slomeVersion = 'SlomeSlomeSlomeSlome'
                    else:
                        versionPath = process[process.find('versions'):process.lower().find('\\slome.exe')]
                        slomeVersion = 'Slome'
                print(versionPath)
            else:
                versionPath = ''
        except:
            pass
        if versionPath != '':
            checkLoadedVersion(versionPath+f'\{slomeVersion}_Data\globalgamemanagers')
            print(versionLoaded)

        ogLog = os.path.getmtime(localLowFilePath + '\Robotnik08\Slome\Player.log')
        newLog = os.path.getmtime(localLowFilePath + '\ZeroEightStudios\Slome\Player.log')
        aprilFoolsLog = os.path.getmtime(localLowFilePath + '\ZeroEightStudios\SlomeSlomeSlomeSlome\Player.log')

        if ogLog > newLog and ogLog > aprilFoolsLog:
            logLocation = localLowFilePath + '\Robotnik08\Slome\Player.log'
        elif newLog > ogLog and newLog > aprilFoolsLog:
            logLocation = localLowFilePath + '\ZeroEightStudios\Slome\Player.log'
        else:
            logLocation = localLowFilePath + '\ZeroEightStudios\SlomeSlomeSlomeSlome\Player.log'

        with open(logLocation) as log:
            log = log.readlines()
            x = 0
            while x < len(log):
                if 'Level loaded from' in log[x]:
                    worldSave = log[x].replace('Level loaded from: ', '').replace('\n','')
                elif 'Level saved as' in log[x]:
                    worldSave = log[x].replace('Level saved as ', '').replace('/level.dat', '').replace('\n','')
                x+=1

        if worldSave != '':
            checkIfSaved = os.listdir(worldSave)
            x=0
            while x < len(checkIfSaved):
                try:
                    if os.path.getmtime(worldSave + '\\' + checkIfSaved[x]) > os.path.getmtime(worldSave + '\latestLaunch.txt'):
                        with open(worldSave + '\latestLaunch.txt', 'w') as latestLaunch:
                            latestLaunch.write(versionLoaded)
                        break
                except:
                    with open(worldSave + '\latestLaunch.txt', 'w') as latestLaunch:
                        latestLaunch.write(versionLoaded)
                x+=1
            print(worldSave)
        print('done')
        loops = 0

def profileMenu():
    global bigSlome, inputNumber, rgbTestValue, inputUsername, sliderSelected, sliding, inputSelected, usernameTestValue, profileDictionary, currentProfile
    bigSlome = False

    syncValues()

    profileMenuRunning = True
    while profileMenuRunning == True:
        screen.blit(pygame.image.load('launcher/largeMenu.png'), (0,0))
        screen.blit((smallTextFont.render(f'Profile: {profileDictionary['profileSelected']}', True, (255, 255, 255))), (14, 690))
        screen.blit(smallTextFont.render('?', True, (255,255,255)), (1170, 16))
        drawUsername()
        drawSlome()
        drawSlider()
        pygame.draw.polygon(screen, [255,255,255], [(332, 175), (352, 195), (332, 215)])
        pygame.draw.polygon(screen, [255,255,255], [(57, 175), (37, 195), (57, 215)])
        if profileDictionary['useLauncherSaves'] == False:
            pygame.draw.lines(screen, [255,255,255], True, [(820,60), (840,60), (840,40), (820,40)])
        elif profileDictionary['useLauncherSaves'] == True:
            pygame.draw.rect(screen, [255,255,255], [820, 40, 20, 20])
        screen.blit((smallTextFont.render('Use Launcher Saves', True, (255,255,255))), (855, 42))
        screen.blit(pygame.image.load('launcher/folderIcon.png'), (1060,44))

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
                        profileDictionary[f'profile_{profileDictionary['profileSelected']}'] = currentProfile
                        if 37 <= mousePosition[0] <= 57:
                            profileDictionary['profileSelected'] -= 1
                            if profileDictionary['profileSelected'] < 0:
                                profileDictionary['profileSelected'] = 0
                        elif 332 <= mousePosition[0] <= 352:
                            profileDictionary['profileSelected'] += 1
                            if profileDictionary['profileSelected'] > 9:
                                profileDictionary['profileSelected'] = 9
                        if profileDictionary[f'profile_{profileDictionary['profileSelected']}'] == []:
                            profileDictionary[f'profile_{profileDictionary['profileSelected']}'] = [f'Profile {profileDictionary['profileSelected']}', (255,255,255)]
                        saveProfiles()
                        saveToWinReg()
                        (1060,44)
                    elif 800 <= mousePosition[0]:
                        if 820 <= mousePosition[0] <= 840 and 40 <= mousePosition[1] <= 60:
                            profileDictionary['useLauncherSaves'] = not profileDictionary['useLauncherSaves']
                            saveProfiles()
                            swapBetweenLauncherSaving(profileDictionary['useLauncherSaves'])
                        elif 1060 <= mousePosition[0] <= 1076 and 44 <= mousePosition[1] <= 60:
                            os.startfile('launcher')

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
            profileDictionary[f'profile_{profileDictionary['profileSelected']}'] = currentProfile
            saveProfiles()
            
        #checkForFileUpdates()
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

    if profileDictionary['closeLauncher'] == True:
        pygame.draw.lines(screen, [255,255,255], True, [(20,420), (40,420), (40,400), (20,400)])
    elif profileDictionary['closeLauncher'] == False:
        pygame.draw.rect(screen, [255,255,255], [20, 400, 20, 20])
    screen.blit((smallTextFont.render('Keep launcher open', True, (255,255,255))), (50, 402))

    x = 0
    while x < len(versionList):
        versions.append([versionList[x], ('versions\\'+versionList[x] + '\Slome.exe'), 550, x * 60 + 20 + scroll])
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
                            weirdNameCases = [versions[x][1], f'versions\\{versionList[x]}\\survival project.exe', f'versions\\{versionList[x]}\\SlomeSlomeSlomeSlome.exe']
                            for filePath in weirdNameCases:
                                try:
                                    os.startfile(filePath)
                                    if profileDictionary['closeLauncher'] == True:
                                        time.sleep(2)
                                        running = False
 
                                    if filePath == f'versions\\{versionList[x]}\\SlomeSlomeSlomeSlome.exe':
                                        slome = 'SlomeSlomeSlomeSlome'
                                    else:
                                        slome = 'Slome'
                                    checkLoadedVersion(f'versions\\{versionList[x]}\\{slome}_Data\\globalgamemanagers')
                                    
                                    break
                                except:
                                    continue
                            else:
                                error('No Slome.exe file found at path')
                        x+=1
                elif 20 <= mousePosition[0] <= 40 and 400 <= mousePosition[1] <= 420:
                    profileDictionary['closeLauncher'] = not profileDictionary['closeLauncher']
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
    #checkForFileUpdates()
    pygame.display.update()

pygame.quit()