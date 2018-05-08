from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *


FPS = 30
SCREENWIDTH  = 500
SCREENHEIGHT = 500
# amount by which base can maximum shift to left
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of move)
PLAYERS_LIST = (
    # bb8
    (
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg'
    ),
    # bb8
    (
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg'
    ),
    # bb8
    (
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg',
        'assets/sprites/sw/bb8_disney.jpg'
    )
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/grid.png',
    'assets/sprites/grid.png'
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('BB8 Game')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/sw/message.jpg').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['disappointed']    = pygame.mixer.Sound('assets/audio/sw/bb8_disappointed' + soundExt)
    SOUNDS['success']    = pygame.mixer.Sound('assets/audio/sw/bb8_success' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['move']   = pygame.mixer.Sound('assets/audio/sw/bb8_move' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        #pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        #IMAGES['pipe'] = (
        #    pygame.transform.rotate(
        #        pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), 180),
        #        pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        #)

        # hismask for pipes
        #HITMASKS['pipe'] = (
        #    getHitmask(IMAGES['pipe'][0]),
        #    getHitmask(IMAGES['pipe'][1]),
        #)

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of bb8"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.20)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 3.2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first move sound and return values for mainGame
                SOUNDS['move'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        #SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo):
    score = playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    #newPipe1 = getRandomPipe()
    #newPipe2 = getRandomPipe()

    # list of upper pipes
    #upperPipes = [
    #    {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
    #    {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    #]

    # list of lowerpipe
    #lowerPipes = [
    #    {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
    #    {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    #]

    #pipeVelX = -4

    # player velocity, max velocity, downward accleration, accleration on move
    playerMoveY    =  0   # player's velocity along Y, default same as playerMoved
    playerMaxMoveY =  0   # max vel along Y, max descend speed
    playerMinMoveY =  0   # min vel along Y, max ascend speed
    playerAccY    =   0   # players downward accleration
    playerMoveX    =  0   # player's velocity along X, default same as playerMoved
    playerMaxMoveX =  0   # max vel along X, max descend speed
    playerMinMoveX =  0   # min vel along X, max ascend speed
    playerAccX    =   0   # players sideway accleration
    playerRot     =   1   # player's rotation
    playerVelRot  =   0   # angular speed
    playerRotThr  =   0   # rotation threshold
    playerMoveAcc =   30   # players distance on moving
    playerMoved = False # True when player move


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if (event.key == K_UP):
                    if playery > -2 * IMAGES['player'][0].get_height():
                        playerMoveY = (-1) * playerMoveAcc
                        playerMoved = True
                        #SOUNDS['move'].play()

                if (event.key == K_DOWN):
                    if playery > -2 * IMAGES['player'][0].get_height():
                        playerMoveY = playerMoveAcc
                        playerMoved = True
                        #SOUNDS['move'].play()

                if (event.key == K_RIGHT):
                    if playerx > -2 * IMAGES['player'][0].get_height():
                        playerMoveX = playerMoveAcc
                        playerMoved = True
                        #SOUNDS['move'].play()

                if (event.key == K_LEFT):
                    if playerx > -2 * IMAGES['player'][0].get_height():
                        playerMoveX = (-1) * playerMoveAcc
                        playerMoved = True
                        #SOUNDS['move'].play()

                if playerMoved:
                    playery += playerMoveY
                    playerx += playerMoveX
                    playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
                    SCREEN.blit(playerSurface, (playerx, playery))

                    pygame.display.update()
                    FPSCLOCK.tick(FPS)

                    playerMoved = False
                    playerMoveY = 0
                    playerMoveX = 0

        # check for crash here
        #crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
        #                       upperPipes, lowerPipes)
        #if crashTest[0] :
        #    return {
        #        'y': playery,
        #        'groundCrash': crashTest[1],
        #        'basex': basex,
        #        'upperPipes': upperPipes,
        #        'lowerPipes': lowerPipes,
        #        'score': score,
        #        'playerMoveY': playerMoveY,
        #        'playerRot': playerRot
        #    }

        # check for score
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        #for pipe in upperPipes:
        #    pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
        #    if pipeMidPos <= playerMidPos < pipeMidPos + 4:
        #        score += 1
        #        SOUNDS['point'].play()

        # playerIndex basex change
        #if (loopIter + 1) % 3 == 0:
        #    playerIndex = next(playerIndexGen)
        #loopIter = (loopIter + 1) % 30
        #basex = -((-basex + 100) % baseShift)

        # rotate the player
        #if playerRot > -90:
        #    playerRot -= playerVelRot

        # player's Y axis movement
        #if playerMoveY < playerMaxMoveY and not playerMoved:
        #    playerMoveY += playerAccY
        #if playerMoved:
        #    playerMoved = False

            # more rotation to cover the threshold (calculated in visible rotation)
            #playerRot = 0

        playerHeight = IMAGES['player'][playerIndex].get_height()
        
        #print(BASEY, playery, playerHeight)
        #print(min(playerMoveY, BASEY - playery - playerHeight))
        #playery += min(playerMoveY, BASEY - playery - playerHeight)
        #playery += playerMoveY

        # move pipes to left
        #for uPipe, lPipe in zip(upperPipes, lowerPipes):
        #    uPipe['x'] += pipeVelX
        #    lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        #if 0 < upperPipes[0]['x'] < 5:
        #    newPipe = getRandomPipe()
        #    upperPipes.append(newPipe[0])
        #    lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        #if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
        #    upperPipes.pop(0)
        #    lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        #for uPipe, lPipe in zip(upperPipes, lowerPipes):
        #    SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
        #    SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        #SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score
        showScore(score)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        


def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerMoveY = crashInfo['playerMoveY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    SOUNDS['hit'].play()
    if not crashInfo['groundCrash']:
        SOUNDS['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= BASEY - 1:
                    return

        # player y shift
        if playery + playerHeight < BASEY - 1:
            playery += min(playerMoveY, BASEY - playery - playerHeight)

        # player velocity change
        if playerMoveY < 15:
            playerMoveY += playerAccY

        # rotate only when it's a hazard crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        #SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx,playery))

        FPSCLOCK.tick(FPS)
        pygame.display.update()


def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
