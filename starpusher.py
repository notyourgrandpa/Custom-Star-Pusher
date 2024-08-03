from pickle import TRUE
import random, sys, copy, os, pygame
from pygame.locals import *
import time

FPS = 30 
WINWIDTH = 800 
WINHEIGHT = 600 
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)

TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 40

CAM_MOVE_SPEED = 5 

OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (  0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
UNDO = 'undo'
NONE = 'none'

class star(pygame.sprite.Sprite):
    def __init__(self, stars, x, y):
        self.stars = stars
        super().__init__()
        self.sprites = []
        num_of_frames = len(os.listdir(f'data/stars/{self.stars}'))
        for i in range(num_of_frames):
            img = pygame.image.load(f'data/stars/{self.stars}/solved{i+1}.png')
            self.sprites.append(img)
        
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.current_sprite += 0.08
        
        if self.stars == '1star':
            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 10
        elif self.stars == '2star':
            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 13
        elif self.stars == '3star':
            if self.current_sprite >= len(self.sprites):
                self.current_sprite = 18
        self.image = self.sprites[int(self.current_sprite)]

def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))

    pygame.display.set_caption('Star Pusher')
    BASICFONT = pygame.font.SysFont('Comic Sans MS', 18)

    IMAGESDICT = {'uncovered goal': pygame.image.load('data/textures/RedSelector.png'),
                  'covered goal': pygame.image.load('data/textures/Selector.png'),
                  'star': pygame.image.load('data/textures/Star.png'),
                  'corner': pygame.image.load('data/textures/Wall_Block_Tall.png'),
                  'wall': pygame.image.load('data/textures/Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('data/textures/Plain_Block.png'),
                  'outside floor': pygame.image.load('data/textures/Grass_Block.png'),
                  'title': pygame.image.load('data/textures/star_title.png'),
                  'disappointed': pygame.image.load('data/textures/disappointed.png'),
                  'princess': pygame.image.load('data/textures/princess.png'),
                  'boy': pygame.image.load('data/textures/boy.png'),
                  'horngirl': pygame.image.load('data/textures/horngirl.png'),
                  'warning' : pygame.image.load('data/textures/Warning.png'),
                  'pinkgirl': pygame.image.load('data/textures/pinkgirl.png'),
                  'rock': pygame.image.load('data/textures/Rock.png'),
                  'short tree': pygame.image.load('data/textures/Tree_Short.png'),
                  'tall tree': pygame.image.load('data/textures/Tree_Tall.png'),
                  'ugly tree': pygame.image.load('data/textures/Tree_Ugly.png')}

    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   '^': IMAGESDICT['horngirl'],
                   '!': IMAGESDICT['warning'],
                   ' ': IMAGESDICT['outside floor']}
    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}

    currentImage = 0
    PLAYERIMAGES = [IMAGESDICT['princess'],
                    IMAGESDICT['boy'],
                    IMAGESDICT['pinkgirl'],
                    IMAGESDICT['horngirl']]

    
    startScreen()

    levels = readLevelsFile('data/levelfile/starPusherLevels.txt')
    currentLevelIndex = 0

    while True: 
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass 
        elif result == 'gameOver':
            currentLevelIndex = currentLevelIndex
            

def runLevel(levels, levelNum):
    soundObj = pygame.mixer.Sound('data/sounds/pop.wav')
    pygame.mixer.music.load('data/sounds/backgroundmusic.mp3')
    pygame.mixer.music.play(-1, 0.0)
    global currentImage
    counter = 0
    counter1 = 0
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True
    levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINHEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT
    levelIsComplete = False
    gameOver = False

    cameraOffsetX = 0
    cameraOffsetY = 0

    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    star1 = pygame.sprite.Group()
    star2 = pygame.sprite.Group()
    star3 = pygame.sprite.Group()
    playerScore1 = star('1star',HALF_WINWIDTH,HALF_WINHEIGHT)
    playerScore2= star('2star',HALF_WINWIDTH,HALF_WINHEIGHT)
    playerScore3= star('3star',HALF_WINWIDTH,HALF_WINHEIGHT)
    
    star1.add(playerScore1)
    star2.add(playerScore2)
    star3.add(playerScore3)

    while True: 
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                    gameStateObj['pressedUndo'] = False
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                    gameStateObj['pressedUndo'] = False
                elif event.key == K_UP:
                    playerMoveTo = UP
                    gameStateObj['pressedUndo'] = False
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN
                    gameStateObj['pressedUndo'] = False
                elif event.key == K_u:
                    if gameStateObj['stepCounter'] == 0:
                        playerMoveTo = NONE
                    else:
                        playerMoveTo = UNDO

                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate() 
                elif event.key == K_BACKSPACE:
                    return 'reset' 
                elif event.key == K_p:
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        currentImage = 0
                    mapNeedsRedraw = True


            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False


        if playerMoveTo != None and not levelIsComplete and not gameOver:
            
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)
            if moved and gameStateObj['pressedUndo'] == False and playerMoveTo != NONE:
                soundObj.play()
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True
            elif moved and gameStateObj['pressedUndo'] == True:
                soundObj.play()
                if gameStateObj['stepCounter'] > 0:
                    gameStateObj['stepCounter'] -= 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

            if isGameOver(levelObj, gameStateObj):
                gameOver = True
                keyPressed = False
                playerMoveTo = None

        DISPLAYSURF.fill(BGCOLOR)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'], levelObj['enemy'])
            mapNeedsRedraw = False
        
        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)

        DISPLAYSURF.blit(mapSurf, mapSurfRect)

        DISPLAYSURF.blit(levelSurf, levelRect)
        stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, WINHEIGHT - 10)
        DISPLAYSURF.blit(stepSurf, stepRect)
        
        if levelIsComplete:
            soundObj1 = pygame.mixer.Sound('data/sounds/minecraft_levelup.wav')
            pygame.mixer.music.stop()

            if counter == 0:
                soundObj1.play()
                counter += 1

            if levelNum == 0:
                if gameStateObj['stepCounter'] <= 7:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 7 and (gameStateObj['stepCounter']) <= 10:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()

            elif levelNum == 1:
                if gameStateObj['stepCounter'] <= 78:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 78 and (gameStateObj['stepCounter']) <= 85:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)

                    star1.update()
            elif levelNum == 2:
                if gameStateObj['stepCounter'] <= 55:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 55 and (gameStateObj['stepCounter']) <= 60:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 3:
                if gameStateObj['stepCounter'] <= 456:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 456 and (gameStateObj['stepCounter']) <= 461:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 4:
                if gameStateObj['stepCounter'] <= 281:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 281 and (gameStateObj['stepCounter']) <= 286:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()

            elif levelNum == 5:
                if gameStateObj['stepCounter'] <= 377:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 377 and (gameStateObj['stepCounter']) <= 382:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 6:
                if gameStateObj['stepCounter'] <= 119:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 119 and (gameStateObj['stepCounter']) <= 124:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 7:
                if gameStateObj['stepCounter'] <= 199:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 199 and (gameStateObj['stepCounter']) <= 204:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 8:
                if gameStateObj['stepCounter'] <= 133:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 133 and (gameStateObj['stepCounter']) <= 138:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()
            
            elif levelNum == 9:
                if gameStateObj['stepCounter'] <= 150:
                    star3.draw(DISPLAYSURF)
                    star3.update()
                elif gameStateObj['stepCounter'] > 150 and (gameStateObj['stepCounter']) <= 155:
                    star2.draw(DISPLAYSURF)
                    star2.update()
                else:
                    star1.draw(DISPLAYSURF)
                    star1.update()


            if keyPressed:
                return 'solved'

        if gameOver:
            soundObj2 = pygame.mixer.Sound('data/sounds/spongebob_disappoint.mp3')
            pygame.mixer.music.stop()
            if counter == 0:
                soundObj2.play()
                counter += 1
            
            solvedRect = IMAGESDICT['disappointed'].get_rect()
            solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
            DISPLAYSURF.blit(IMAGESDICT['disappointed'], solvedRect)

            if keyPressed:
                return 'gameOver'

        pygame.display.update() 
        FPSCLOCK.tick()
        
def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False 
    elif mapObj[x][y] in ('#', 'x', '^'):
        return True 
    return False

def decorateMap(mapObj, startxy):
    startx, starty = startxy

    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*', '^'):
                mapObjCopy[x][y] = ' '

    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):

            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    if isWall(mapObj, x, y):
        return True

    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return True 

    elif (x, y) in gameStateObj['stars']:
        return True 

    return False

def getStepCount(gameStateObj):
    return gameStateObj
    
def makeMove(mapObj, gameStateObj, playerMoveTo):
    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']
    starIndex = gameStateObj['starIndex']
    starx = gameStateObj['lastStarLocationx']
    stary = gameStateObj['lastStarLocationy']

    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0
    elif playerMoveTo == UNDO:
        if gameStateObj['pressedUndo'] == False:
            if gameStateObj['lastMove'] == UP:
                xOffset = 0
                yOffset = 1
                if gameStateObj['isStarMoved'] == True:
                    stars[starIndex] = (starx + xOffset, stary + yOffset)
                    gameStateObj['isStarMoved'] = False
            if gameStateObj['lastMove'] == RIGHT:
                xOffset = -1
                yOffset = 0
                if gameStateObj['isStarMoved'] == True:
                    stars[starIndex] = (starx + xOffset, stary + yOffset)
                    gameStateObj['isStarMoved'] = False
            if gameStateObj['lastMove'] == DOWN:
                xOffset = 0
                yOffset = -1
                if gameStateObj['isStarMoved'] == True:
                    stars[starIndex] = (starx + xOffset, stary + yOffset)
                    gameStateObj['isStarMoved'] = False
            if gameStateObj['lastMove'] == LEFT:
                xOffset = 1
                yOffset = 0
                if gameStateObj['isStarMoved'] == True:
                    stars[starIndex] = (starx + xOffset, stary + yOffset)
                    gameStateObj['isStarMoved'] = False
            gameStateObj['pressedUndo'] = True
        else:
            xOffset = 0
            yOffset = 0
            gameStateObj['pressedUndo'] = True
            return False
    elif playerMoveTo == NONE:
        xOffset = 0
        yOffset = 0

    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
                ind = stars.index((playerx + xOffset, playery + yOffset))
                gameStateObj['starIndex'] = ind
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
                gameStateObj['lastStarLocationx'] = stars[ind][0]
                gameStateObj['lastStarLocationy'] = stars[ind][1]
                gameStateObj['isStarMoved'] = True
            else:
                gameStateObj['isStarMoved'] = False
                return False
        else:
            gameStateObj['isStarMoved'] = False
                
        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        gameStateObj['lastMove'] = playerMoveTo
        
        return True


def startScreen():
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50 
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    instructionText = ['Push the stars over the marks.',
                       'Arrow keys to move, WASD for camera control, P to change character.',
                       'Backspace to reset level, Esc to quit.',
                       'N for next level, B to go back a level.',
                       'U to Undo.',
                       '',
                       'Avoid placing stars on a red tile!']

    DISPLAYSURF.fill(BGCOLOR)

    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord += 10 
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height 
        DISPLAYSURF.blit(instSurf, instRect)

    while True: 
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return 

        pygame.display.update()
        FPSCLOCK.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']
    mapFile.close()

    levels = [] 
    levelNum = 0
    mapTextLines = [] 
    mapObj = [] 
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None 
            starty = None
            goals = [] 
            stars = [] 
            enemy = [] 
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))
                    if mapObj[x][y] in ('^'):
                        enemy.append((x, y))

            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars,
                            'lastStepCount': [],
                            'isStarMoved': False,
                            'starIndex': 0,
                            'lastStarLocationx': startx,
                            'lastStarLocationy': starty,
                            'lastMove': NONE,
                            'pressedUndo': False}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals': goals,
                        'startState': gameStateObj,
                        'enemy': enemy
                        }

            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) # call right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) # call left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) # call down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) # call up


def drawMap(mapObj, gameStateObj, goals, enemy):
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * TILEFLOORHEIGHT, TILEWIDTH, TILEHEIGHT))
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING:
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect)
            
            elif (x,y) in enemy:
                mapSurf.blit(IMAGESDICT['warning'], spaceRect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)
    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    """Returns True if all the goals have stars in them."""
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            return False
    return True

def isGameOver(levelObj, gameStateObj):
    for warning in levelObj['enemy']:
        if warning in gameStateObj['stars']:
            return True
    return False


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()