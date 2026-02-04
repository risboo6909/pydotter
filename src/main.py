#! /usr/bin/env python
#coding=utf-8

"""

    2011 Boris Tatarintsev

    Python and PyGame implementation of well-known dotter game
    which is available for ios/android devices.

"""

import pygame
import pygame.locals
import sys
import os
import consts
import configreader
import time
import random
import tools
import menu
import particles
import strings
import eztext


from hsdrawer    import HSDrawer
from hslocal     import HSLocal
from hsremote    import HSRemote
from math        import pi
from mysprite    import MySprite
from mygroup     import MyGroup
from imagebutton import ImageButton
from msgwindow   import MessageWindow


class Game(object):
    
    def __init__(self):
        """ Contrustor """
        self.mScreenFall = None
        # we begin with impossible state ;)
        self.mState = -1
        # here we remember the previous game state
        self.mPrevState = self.mState
        # init config reader
        self.mCR = configreader.ConfigReader()
        # read game settings        
        self.mIsReducedEffects = self.mCR.get('Effects', 'ReduceEffects')        
        self.mIsCheatsEnabled = self.mCR.get('Gameplay', 'Cheats')
        self.mIsServerScore = self.mCR.get('Network', 'ServerScores')
        self.mSndPlayer = tools.getSoundPlayer(self.mCR.get('Sound', 'Sound'))
        # init pygame
        self.initPyGame(consts.SCREEN_WIDTH, consts.SCREEN_HEIGHT)
        # init sounds
        self.initSounds()
        # init sprites and menu
        self.initSprites()
        self.initMenu()
        self.initMessageWindows()
        # init graphical buttons
        self.initButtons()        
        # init high scores stuff
        # local scores manager
        self.mHSManager = HSLocal()
        # server scores manager
        if self.mIsServerScore:
            self.mHSManagerServer = HSRemote()
        else:
            self.mHSManagerServer = None
        # high scores table drawer
        self.mHSDrawer = HSDrawer(self.mHSManager, self.mHSManagerServer, self.startReplay)

    def initPyGame(self, scrWidth, scrHeight):
        """ Initialize pygame """
        # initialize game window
        pygame.init()
        # init display
        Game.mScrWidth, Game.mScrHeight = scrWidth, scrHeight
        # pygame
        self.mWindow = pygame.display.set_mode((self.mScrWidth, self.mScrHeight))
        self.mSurface = pygame.display.get_surface()
        # init caption and icon
        pygame.display.set_icon(pygame.image.load(os.path.join('..', 'icon', 'icon.gif'))) 
        pygame.display.set_caption('Python Dotter v1.0.0 (rc2)')
        # init fonts
        fontPath = os.path.join('..', 'font', 'freesansbold.ttf')
        self.bigfont = pygame.font.Font(fontPath, 40)
        self.medfont = pygame.font.Font(fontPath, 20)
        self.smallfont = pygame.font.Font(fontPath, 13)
        self.tinyfont = pygame.font.Font(fontPath, 12) 
        self.microfont = pygame.font.Font(fontPath, 7)        

    def loadImagesList(self, imgList):
        """ Load images one by one into hash """
        output = {}
        idx = 0
        for item in imgList:
            output[idx] = pygame.image.load(item)
            idx += 1
        return output

    def initButtons(self):
        imgs = { ImageButton.STATE_DISABLED : pygame.image.load(os.path.join('..', 'png', 'finish_disabled.png')), ImageButton.STATE_ENABLED : pygame.image.load(os.path.join('..', 'png', 'finish_enabled.png')), \
                ImageButton.STATE_OVER : pygame.image.load(os.path.join('..', 'png', 'finish_over.png')), ImageButton.STATE_CLICK : None }
        self.mFinishButton = ImageButton( imgs )
        
        self.mFinishButton.setAlign(tools.HORIZ_RIGHT | tools.VERT_BOTTOM)
        self.mFinishButton.setPos(self.mScrWidth - 5, self.mScrHeight - 5)
        self.mFinishButton.setCallback(self.finishButtonCallback)
        
    def initMessageWindows(self):
        self.mMsgGameOver = MessageWindow(self.mScrWidth >> 1, self.mScrHeight >> 1, "Game over", self.bigfont, False)
        self.mMsgReady = MessageWindow(self.mScrWidth >> 1, self.mScrHeight >> 1, "Ready?", self.bigfont, False)
        self.mMsgPaused = MessageWindow(self.mScrWidth >> 1, self.mScrHeight >> 1, "Game paused", self.bigfont, False)
        
        self.mDlgConfirm = MessageWindow(self.mScrWidth >> 1, self.mScrHeight >> 1, "Are you sure?", self.medfont, True)
        self.mDlgConfirm.setPositiveCallback(self.gameOver)
        self.mDlgConfirm.setNegativeCallback(self.returnToPrevState)
        
    def initSounds(self):
        """ Load sounds """
        pygame.mixer.init(44100, -16, 1, 1024)
        self.mSounds = {}
        self.mSounds['click'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'click.wav'))
        self.mSounds['wrong'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'wrong.wav'))
        self.mSounds['collide'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'collide.wav'))
        self.mSounds['siren'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'siren.wav'))
        self.mSounds['gameover'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'gameover.wav'))
        self.mSounds['pop'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'pop.wav'))
        self.mSounds['applause'] = pygame.mixer.Sound(os.path.join('..', 'sound', 'applause.wav'))
    
    def initSprites(self):
        """ Initialize game sprites """
        # load images
        self.mImgVBar = pygame.image.load(os.path.join('..', 'png', 'vert_bar.png'))        
        
        # load dots images        
        self.mImgDots = self.loadImagesList(tools.getFilesByMask(os.path.join('..', 'png'), 'dot*.png'))
        
        # cursors
        self.mImgSmallShadow = pygame.image.load(os.path.join('..', 'png', 'shadow_small.png'))
        self.mImgBigShadow = pygame.image.load(os.path.join('..', 'png', 'shadow_big.png'))
        self.mImgSmallShadow.set_alpha(50)
        self.mImgBigShadow.set_alpha(50)

        # load arrows images
        self.mArrowImgs = {}
        self.mArrowImgs[consts.DIRECT_LEFT] = pygame.image.load(os.path.join('..', 'png', 'arrow_left.png'))
        self.mArrowImgs[consts.DIRECT_RIGHT] = pygame.image.load(os.path.join('..', 'png', 'arrow_right.png'))
        self.mArrowImgs[consts.DIRECT_UP] = pygame.image.load(os.path.join('..', 'png', 'arrow_up.png'))
        self.mArrowImgs[consts.DIRECT_DOWN] = pygame.image.load(os.path.join('..', 'png', 'arrow_down.png'))
                        
        # scale all images down for hud
        self.mArrowImgsHUD = {}
        self.mArrowImgsHUD[consts.DIRECT_LEFT] = pygame.transform.scale(self.mArrowImgs[consts.DIRECT_LEFT], (20, 21))
        self.mArrowImgsHUD[consts.DIRECT_RIGHT] = pygame.transform.scale(self.mArrowImgs[consts.DIRECT_RIGHT], (20, 21))
        self.mArrowImgsHUD[consts.DIRECT_UP] = pygame.transform.scale(self.mArrowImgs[consts.DIRECT_UP], (20, 21))
        self.mArrowImgsHUD[consts.DIRECT_DOWN] = pygame.transform.scale(self.mArrowImgs[consts.DIRECT_DOWN], (20, 21))
        
        # load stars images
        self.mImgStarFull = pygame.image.load(os.path.join('..', 'png', 'star_full.png'))
        self.mImgStarEmpty = pygame.image.load(os.path.join('..', 'png', 'star_empty.png'))
        
        # load backgrounds
        self.mBacks = {}
        self.mBacks = self.loadImagesList(tools.getFilesByMask(os.path.join('..', 'png', 'bg'), 'bg*.png'))
        for j in range(len(self.mBacks)):
            self.mBacks[j].set_alpha(consts.BG_MAX_ALPHA)
            
        # load instructions screen
        self.mInstrScreen = pygame.image.load(os.path.join('..', 'png', 'bg', 'instructions.png'))
        
        self.mDynObjsGroup = MyGroup()

    def initMenu(self):
        """ Initialize game menu """
        # create main menu
        self.mMainMenu = menu.RotatingMenu(x = 320, y = 240, radius = 220, arc = pi, defaultAngle = pi / 2.0, drawBg = not self.mIsReducedEffects)
        self.mMainMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_STANDART))
        self.mMainMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_SURVIVE))
        self.mMainMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_HSCORE))
        # this will be implemented in final release
        self.mMainMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_INSTR))
        self.mMainMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_EXIT))
        self.mMainMenu.selectItem(0)        
        # create score menu
        self.mScoreMenu = menu.RotatingMenu(x = 320, y = 240, radius = 200, arc = pi, defaultAngle = pi / 2.0)
        self.mScoreMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_STANDART))
        self.mScoreMenu.addItem(menu.MenuItem(strings.STR_MAIN_MENU_SURVIVE))
        self.mScoreMenu.addItem(menu.MenuItem(strings.STR_MENU_BACK))
        self.mScoreMenu.selectItem(0)        
        
    def startNewGame(self, gameType = consts.GAME_MODE_STANDART, isReplay = False):
        """ Start new game, reset all parameters to defaults """
        # stop all sounds
        pygame.mixer.stop()
        
        self.mDynObjsGroup = MyGroup()        
        self.mFlashInterp = self.getFlashInterp()
        self.mScreenFall = tools.getFallEffectDrawer(self.mSurface, self.mScrWidth, self.mScrHeight)        
                
        self.reinitParticles()
        
        self.mFinishButton.mState = ImageButton.STATE_ENABLED
        
        if not isReplay:
            self.mReplayData = []
            self.mLastEvent = None
        else:
            self.mLastEvent = self.mReplayData.pop()
            
        self.mIsReplay = isReplay        
        
        self.mNumDots = 0
        self.mLives = consts.MAX_LIVES
        self.mScore = 0
        self.mScoreTreshold = 0
        self.mGameType = gameType
        self.mSimulateBreakup = False
        self.mWasCollision = False
        
        # [timers for survival mode >]
        self.mTotalTime = consts.SURVIVAL_THINK_TIME_MS
        self.mTimeLeft = consts.SURVIVAL_THINK_TIME_MS
        # [<]
        
        self.changeState(consts.STATE_PLAY)

        self.mBGChangeTime = pygame.time.get_ticks()
        self.mGameTime = pygame.time.get_ticks()
        self.mCountDownTimer = consts.MAXTIMER
        self.mColorIdx = 0
        
        self.mBackIdx = random.randint(0, len(self.mBacks) - 1)
        
        # make all backgrounds visible
        for bkgImg in self.mBacks.values():
            bkgImg.set_alpha(consts.BG_MAX_ALPHA)
        
        self.mNewBackIdx = self.mBackIdx        
        self.mFlashScreen = False        
        self.mNextDot = self.mImgDots[random.randint(0, len(self.mImgDots) - 1)]        

        self.mFirstShowDirection = False
        self.mDirectionShown = False
        self.mAnimateDirection = False
        self.processEvents()

    def reinitParticles(self):
        """ Reinit particle system """
        self.mParticlesGroup = pygame.sprite.Group()
        particles.Particle.containers = self.mParticlesGroup
        
    def showMainMenu(self):
        """ Dislpay main menu """
        self.mScreenFall = tools.getFallEffectDrawer(self.mSurface, self.mScrWidth, self.mScrHeight)
        self.changeState(consts.STATE_MAIN_MENU)
        self.mMainMenu.selectItem(0)
        self.processEvents()

    def showScoreTypeMenu(self):
        """ Display score type menu """
        self.mScreenFall = tools.getFallEffectDrawer(self.mSurface, self.mScrWidth, self.mScrHeight)
        self.changeState(consts.STATE_CHOOSE_SCORE_TYPE)
        self.mScoreMenu.selectItem(0)
        self.processEvents()
        
    def getCurMenu(self):
        if self.mState == consts.STATE_MAIN_MENU:
            return self.mMainMenu
        elif self.mState == consts.STATE_CHOOSE_SCORE_TYPE :
            return self.mScoreMenu
            
    def showHSTable(self, scoreType = strings.STR_MAIN_MENU_STANDART):
        """ Show high scores screen """
        self.mScreenFall = tools.getFallEffectDrawer(self.mSurface, self.mScrWidth, self.mScrHeight)
        self.mHSDrawer.useTable(scoreType)
        self.changeState(consts.STATE_SHOW_HIGH_SCORES)

    def startReplay(self, gameType, replayData):        
        self.mReplayData = replayData
        self.mReplayData.reverse()
        self.startNewGame(gameType, True)        

    def finishButtonCallback(self):
        # this method is being called when user presses the finish button        
        self.mShutterFunc = tools.getShutterEffectDrawer(self.mSurface, self.mImgVBar, self.mScrWidth, 2000)
        self.mFinishButton.setState(ImageButton.STATE_ENABLED)
        self.changeState(consts.STATE_FINISH_CONFIRM)        

    def gameOver(self, *args):
        """ Switch to game over state and ask player to enter a name if needed """
        pygame.mixer.stop()
        if not self.changeState(consts.STATE_ENTER_NAME):
            self.startNewGame(self.mGameType)

    @staticmethod
    def getGameTypeString(gameType):
        return strings.STR_MAIN_MENU_STANDART if gameType == consts.GAME_MODE_STANDART else strings.STR_MAIN_MENU_SURVIVE

    @staticmethod
    def getGameTypeID(gameType):
        return consts.GAME_MODE_STANDART if gameType == strings.STR_MAIN_MENU_STANDART else consts.GAME_MODE_SURVIVAL
    
    def reduceLives(self):
        """ Decrease player lives """
        pygame.mixer.stop()
        if self.mLives > 0:
            self.mLives -= 1
            self.reinitParticles()
            self.changeState(consts.STATE_PREPARE)
            self.mShutterFunc = tools.getShutterEffectDrawer(self.mSurface, self.mImgVBar, self.mScrWidth, 2000)
            self.mFlashScreen = False
            self.mTimeLeft = self.mTotalTime
            self.mCountDownTimer = consts.MAXTIMER
    
    def getFlashInterp(self):
        """ Returns linear interpolator for screen flashing """
        return tools.getLinearInterp(100, 0, consts.SCREEN_FLASH_PERIOD)
    
    def getParticleType(self, particle):        
        return consts.SMALL_PARTICLE if particle.radius == consts.SMALL_DOT_RADIUS else consts.BIG_PARTICLE

    def isLocalOrServerHighScore(self):
        label = "You\'ve got a highscore!"
        flag = False
        if self.mIsServerScore:
            try:
                # update server scores first
                self.mHSManagerServer.getRemoteScores(self.mGameType)
            except IOError:
                pass
            # check if player has a highscore in at least one table            
            if self.mHSManagerServer.isHighScore(Game.getGameTypeString(self.mGameType), self.mScore):            
                label += " Global record!"
                flag = True
            if self.mHSManager.isHighScore(Game.getGameTypeString(self.mGameType), self.mScore):
                label += " Local record!"
                flag = True            
        else:
            if self.mHSManager.isHighScore(Game.getGameTypeString(self.mGameType), self.mScore):
                label += " Local record!"
                flag = True
        
        if flag:
            self.mNameBox = eztext.Input(maxlength=6, color=(0,0,0), prompt=label, font=self.smallfont, \
                                    x = self.mScrWidth / 2 - 200, y = self.mScrHeight / 2 - 30)
            return True
        
        return False
    
    def createNewDynamicObject(self, pos):
        """ Create a new dynamic particle """
                
        newParticle = MySprite(self.mNextDot, self.mDynObjsGroup, [pos[0] - (self.mNextDot.get_rect().width >> 1), pos[1] - (self.mNextDot.get_rect().height >> 1)], \
                            self.mDirection)
        
        # choose next particle size
        nextParticle = self.mImgDots[random.randint(0, len(self.mImgDots) - 1)]
        
        return newParticle, nextParticle
        
    def chooseRandomDirection(self):
        """ Select direction for the next particle """
        self.mDirection = random.randint(0, consts.DIRECT_COUNT - 1)
        self.mAnimateDirection = True
        self.mDirectionAnimationTime = consts.DIRECT_ANIM_SCALE_TIME
        
    def returnToPrevState(self):
        self.mState = self.mPrevState
        return True
    
    def changeState(self, newState):
        # TODO: make this method to look nicer :)
        # changes the state to newState, returns True if success and False otherwise        
        if self.mState != newState:
            if newState == consts.STATE_ENTER_NAME:
                if self.isLocalOrServerHighScore():
                    self.mPrevState = self.mState
                    self.mState = newState
                    self.mSndPlayer(self.mSounds['applause'])
                    return True
            else:
                self.mPrevState = self.mState
                self.mState = newState
                return True
        return False
    
    def testCollide(self, p1, p2, deltaMS):
        """ Dynamic collision detection """
        # test AABB - AABB intersection           
        if tools.AABB_IntersectTest(p1, p2, deltaMS)[0]:
            # test circle-circle intersection
            res = tools.circleCircleIntersect(p1.center_x, p1.center_y, p2.center_x, p2.center_y, \
                                              p1.radius, p2.radius, p1.velocity, p2.velocity, deltaMS)
            if res[0]: return True, res[1]
        return False, -1
    
    def testOverlap(self, p1, p2):
        """ Static collision detection, mb this will be removed later because it is enough to use dynamic detection
            for this purpose
        """
        # test AABB - AABB intersection
        if tools.AABBAABB_Overlap(p1, p2, 2):
            # test circle-circle intersection            
            return tools.circlesOverlap(p1.center, p2.center, p1.radius + 1, p2.radius + 1)
        return False
        
    def showExplode(self, p1, p2):
        """ Init particles explosion """
        # compute collision point
        v = tools.sub( p1.center, p2.center )        
        b = tools.mul(v, 0.5)
        c = [0] * 2
        c[0] = p2.coord_x + p2.radius + b[0]
        c[1] = p2.coord_y + p2.radius + b[1]
        # show explosion :)
        for i in range(consts.COLLISION_PARTICLES):
            particles.Particle(c, random.uniform(-1, 1), random.uniform(-1, 1), 0, 0.01, 3,
                            [((random.randrange(128, 256), random.randrange(128, 256), random.randrange(128, 256)),
                                (255, 255, 255), 20), ((255, 255, 255), (0, 0, 0), 10)])
    
    def reflectCircles(self, c1, c2):
        """ Compute the reflection vectors of the two collided particles """
        new_v1, new_v2 = tools.getCirclesReflection( c1.coords, c1.velocity, c2.coords, c2.velocity )                            
        
        axis = tools.sub( c1.coords, c2.coords )

        # project velocities to the axis from center of c1 to the center of c2
        v1_proj = tools.proj( c1.velocity, axis )
        v2_proj = tools.proj( c2.velocity, axis )
        
        v_rel = v1_proj - v2_proj
        
        mass_total = c1.mass + c2.mass

        # here we compute particles speeds after collision
        u1_mag = abs( (((c1.mass - c2.mass) * v_rel) / mass_total) - v1_proj)
        u2_mag = abs( ((2 * c1.mass * v_rel) / mass_total) - v1_proj)

        # avoid hyper-velocities to reduce collisions computation errors :)
        if u1_mag >= consts.MAX_VELOCITY_MAGNITUDE : u1_mag = consts.MAX_VELOCITY_MAGNITUDE
        if u2_mag >= consts.MAX_VELOCITY_MAGNITUDE : u2_mag = consts.MAX_VELOCITY_MAGNITUDE

        # compute new velocity magnitude
        v1_norm = tools.normalize( new_v1 )
        v2_norm = tools.normalize( new_v2 )

        # final velocity after collision
        c1.velocity = tools.mul(v1_norm, u1_mag)
        c2.velocity = tools.mul(v2_norm, u2_mag)
                
    def processMenuAction(self, menuItemID):
        """ Menu actions handler """
        if self.mState == consts.STATE_MAIN_MENU:
            if menuItemID == strings.STR_MAIN_MENU_STANDART:
                self.startNewGame()
            elif menuItemID == strings.STR_MAIN_MENU_SURVIVE:
                self.startNewGame(consts.GAME_MODE_SURVIVAL)
            elif menuItemID == strings.STR_MAIN_MENU_HSCORE:
                self.showScoreTypeMenu()
            elif menuItemID == strings.STR_MAIN_MENU_INSTR:
                self.changeState(consts.STATE_ABOUT)
            elif menuItemID == strings.STR_MAIN_MENU_EXIT:
                sys.exit(0)
        elif self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
            if menuItemID == strings.STR_MAIN_MENU_STANDART:
                self.showHSTable(strings.STR_MAIN_MENU_STANDART)
            elif menuItemID == strings.STR_MAIN_MENU_SURVIVE:
                self.showHSTable(strings.STR_MAIN_MENU_SURVIVE)            
            elif menuItemID == strings.STR_MENU_BACK:
                self.showMainMenu()

    def processEvents(self):
        """ Main events handling loop """
        
        delta = 0        
        while True:
            
            s = pygame.time.get_ticks()
            events = pygame.event.get()
            
            for event in events:
                
                if event.type == pygame.locals.QUIT:
                    sys.exit(0)
                
                result = False
                if self.mState == consts.STATE_ENTER_NAME:
                    self.mNameBox.update(events)
                    
                elif self.mState == consts.STATE_SHOW_HIGH_SCORES:
                    result = self.mHSDrawer.processEvents(events, self)
                
                # if event was not handled elsewhere
                if not result:
                    
                    if event.type == pygame.locals.ACTIVEEVENT and \
                    (self.mState == consts.STATE_PLAY or self.mState == consts.STATE_PAUSED):
                        
                        if (event.state == 2 and event.gain == 0) or (event.state == 6 and event.gain == 0):
                            self.mShutterFunc = tools.getShutterEffectDrawer(self.mSurface, self.mImgVBar, self.mScrWidth, 2000)
                            self.changeState(consts.STATE_PAUSED)
                        elif (event.state == 2 and event.gain == 1) or (event.state == 6 and event.gain == 1):                            
                            self.changeState(consts.STATE_PLAY)
                            break
                    
                    elif event.type == pygame.KEYDOWN:
                        
                        if self.mState == consts.STATE_MAIN_MENU or self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
                            if event.key == pygame.K_LEFT:
                                self.getCurMenu().selectItem(self.getCurMenu().selectedItemNumber + 1)
                            if event.key == pygame.K_RIGHT:
                                self.getCurMenu().selectItem(self.getCurMenu().selectedItemNumber - 1)
                            if event.key == pygame.K_RETURN:
                                self.processMenuAction(self.getCurMenu().getSelectedItemText())

                        if self.mState == consts.STATE_PLAY or self.mState == consts.STATE_CHOOSE_SCORE_TYPE or self.mState == consts.STATE_PAUSED \
                            or self.mState == consts.STATE_PREPARE or self.mState == consts.STATE_GAMEOVER or self.mState == consts.STATE_FINISH_CONFIRM \
                                or self.mState == consts.STATE_ABOUT:
                            if event.key == pygame.K_ESCAPE:
                                self.showMainMenu()
                        
                        if self.mIsCheatsEnabled:
                            # cheats
                            if event.key == 275 and self.mState == consts.STATE_PLAY:
                                self.mScore += 100
                            if event.key == 276 and self.mState == consts.STATE_PLAY:
                                self.mLives -= 1

                        if consts.__DEBUG__:
                            # debug
                            if event.key == 276 and self.mState == consts.STATE_PLAY:
                                self.mDirection = consts.DIRECT_LEFT
                            if event.key == 275 and self.mState == consts.STATE_PLAY:
                                self.mDirection = consts.DIRECT_RIGHT
                            if event.key == 273 and self.mState == consts.STATE_PLAY:
                                self.mDirection = consts.DIRECT_UP
                            if event.key == 274 and self.mState == consts.STATE_PLAY:
                                self.mDirection = consts.DIRECT_DOWN

                    elif event.type == pygame.MOUSEMOTION:
                        
                        if self.mState == consts.STATE_MAIN_MENU or self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
                            m_x, m_y = event.pos
                            for item in self.getCurMenu().items:
                                metrics = item.getMetrics()
                                if m_x >= metrics[0] and m_y >= metrics[1] and m_x <= metrics[2] and m_y <= metrics[3]:
                                    self.getCurMenu().selectedItem.deselect()
                                    self.getCurMenu().selectedItem = item
                                    item.select()
                                    break
                        elif self.mState == consts.STATE_PLAY:
                            self.mFinishButton.processEvents(event)

                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == consts.LEFT_MOUSE_BUTTON:
                        
                        if self.mState == consts.STATE_MAIN_MENU or self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
                            # check if we clicked a mouse over any of menu items
                            m_x, m_y = event.pos
                            for item in self.getCurMenu().items:
                                metrics = item.getMetrics()
                                if m_x >= metrics[0] and m_y >= metrics[1] and m_x <= metrics[2] and m_y <= metrics[3]:
                                    self.processMenuAction(item.text)
                                    break
                        
                        elif self.mState == consts.STATE_PLAY:
                            
                            # okay, user has clicked inside the game field, create new moving sprite
                            # and start to animate it
                            if not self.mSimulateBreakup and self.mDirectionShown:
                                
                                # if user didn't press finish button
                                if not self.mFinishButton.processEvents(event): 
                                
                                    newParticle, nextParticle = self.createNewDynamicObject(event.pos)
                                    
                                    # check if user doesn't try to click over another particle
                                    success = True
                                    for particle in self.mDynObjsGroup:
                                        if particle != newParticle:
                                            result = self.testOverlap(particle, newParticle)
                                            if result:
                                                success = False
                                                self.mDynObjsGroup.remove(newParticle)                                                
                                                self.mSndPlayer(self.mSounds['wrong'])
                                                break
                                            
                                    if success:
                                        
                                        # save timestamp and coordinates for replay
                                        self.mReplayData.append( [self.mGameTime , event.pos[:], self.getParticleType(newParticle), newParticle.velocity[:]] )
                                        
                                        pygame.mixer.stop()
                                        self.mSndPlayer(self.mSounds['click'])                                
                                        self.mNextDot = nextParticle
                                        self.mScore += consts.SCORE_STEP
                                        
                                        if self.mScore % 500 == 0 and self.mScore != 0 and self.mScore > self.mScoreTreshold:
                                            self.mTotalTime -= consts.SURVIVAL_TIME_REDUCE_MS
                                            self.mScoreTreshold = self.mScore
                                        
                                        self.chooseRandomDirection()
                                        self.mNumDots += 1
                                        self.mFlashScreen = False
                                        self.mTimeLeft = self.mTotalTime
                                                                        
                        elif self.mState == consts.STATE_PREPARE:
                            # enable finish button
                            if self.mFinishButton.mState == ImageButton.STATE_DISABLED:
                                self.mFinishButton.mState = ImageButton.STATE_ENABLED                            
                            self.changeState(consts.STATE_PLAY)
                            
                        elif self.mState == consts.STATE_FINISH_CONFIRM:
                            self.mDlgConfirm.processEvents(event)                            
                        
                        elif self.mState == consts.STATE_GAMEOVER:
                            self.gameOver()                            
                            
            self.update(delta)
            self.paint(delta)
            
            # if game runs to fast - slow it down for a little bit :]
            if delta < 10:
                time.sleep((10 - delta) / 1000.0)
            
            delta = pygame.time.get_ticks() - s

    def update(self, deltaMS):
        """ Update method. Detects particles collisions and updates their
            states
        """ 
        if self.mState == consts.STATE_PLAY:

            self.mGameTime += deltaMS

            if self.mFirstShowDirection:
                self.chooseRandomDirection()
                self.mFirstShowDirection = False
                self.mDirectionShown = True
            
            """
            # replay feature, will be done in next releases
            if self.mIsReplay and self.mGameTime >= self.mLastEvent[0]:
                self.mLastEvent = self.mReplayData.pop()
            """
                                
            self.mFinishButton.update()
                        
            if self.mGameType == consts.GAME_MODE_SURVIVAL:
                if self.mTimeLeft <= 0:
                    self.mTimeLeft = self.mTotalTime
                    self.reduceLives()
                    self.mFlashScreen = False                                    
            
            # animate direction array if needed
            if self.mAnimateDirection:            
                self.mDirectionAnimationTime -= deltaMS
                if self.mDirectionAnimationTime <= 0:
                    # disable when animation is finished
                    self.mAnimateDirection = False

            to_remove = set()
            checked = set()
            
            collidedParticles = False

            self.mParticlesGroup.update(deltaMS)

            # check for collisions first

            globalMinTime = deltaMS
            collidedA = collidedB = None

            for curParticle in self.mDynObjsGroup:

                minTime = deltaMS
                collidedParticle = None

                for anotherParticle in self.mDynObjsGroup:

                    # check object AABBs collisions. it's fast and simple.
                    # most collisions will be refused at this step without testing circle-circle intersection
                    if curParticle != anotherParticle and anotherParticle not in checked:
                        # dont check zero-speed particles
                        if tools.magnitude(curParticle.velocity) > tools.epsilon and tools.magnitude(anotherParticle.velocity) > tools.epsilon:
                            res = self.testCollide(curParticle, anotherParticle, deltaMS)
                            if res[0]:
                                if res[1] <= minTime:
                                    minTime = res[1]
                                    collidedParticle = anotherParticle
                                if globalMinTime >= minTime:
                                    globalMinTime = minTime
                                    collidedA = curParticle
                                    collidedB = collidedParticle

                checked.add(curParticle)

            if collidedA != collidedB != None:

                if not self.mSimulateBreakup:
                    # start simple collisions simulation
                    self.mSimulateBreakup = True
                    self.mFlashScreen = True
                    self.mWasCollision = True
                    self.mFlashInterp = self.getFlashInterp()
                    # disable finish button when particles colliding
                    self.mFinishButton.mState = ImageButton.STATE_DISABLED

                self.mSndPlayer(self.mSounds['collide'])
                collidedA.collide = collidedB.collide = True

            # move all the sprites
            for curParticle in self.mDynObjsGroup:

                curParticle.update(globalMinTime)
                
                if not curParticle.mCollide:                    
                    # check screen borders
                    if curParticle.coord_y <= -curParticle.height and curParticle.dir == consts.DIRECT_UP:
                        curParticle.coord_y = Game.mScrHeight + (curParticle.coord_y + curParticle.height)
                    elif curParticle.coord_y >= Game.mScrHeight and curParticle.dir == consts.DIRECT_DOWN:
                        curParticle.coord_y = -curParticle.height + (curParticle.coord_y % Game.mScrHeight)
                    elif curParticle.coord_x <= -curParticle.width and curParticle.dir == consts.DIRECT_LEFT:
                        curParticle.coord_x = Game.mScrWidth + (curParticle.coord_x + curParticle.width)
                    elif curParticle.coord_x >= Game.mScrWidth and curParticle.dir == consts.DIRECT_RIGHT:
                        curParticle.coord_x = -curParticle.width + (curParticle.coord_x % Game.mScrWidth)
                else:
                    if curParticle not in to_remove:                                            
                        collidedParticles = True                        
                        # if particle was collided and it has used all the
                        # time available for it - just destroy it!                                            
                        if curParticle.live_timer(deltaMS) >= 100:
                            to_remove.add(curParticle)                            
                            # show nice explosion
                            b = curParticle.coord_x, curParticle.coord_y
                            for i in range(consts.SELFEXPLODE_COLLISION_PARTICLES):
                                particles.Particle(b, random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01), 3,
                                                [((random.randrange(128, 256), random.randrange(128, 256), random.randrange(128, 256)),
                                                    (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)), 20),
                                                    ((random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256)), (0, 0, 0), 10)])
                            self.mScore -= consts.SCORE_STEP
                            self.mSndPlayer(self.mSounds['pop'])
                            
                        elif curParticle.coord_y <= -curParticle.rect.height or curParticle.coord_y >= self.mScrHeight or \
                            curParticle.coord_x <= -curParticle.rect.width or curParticle.coord_x >= self.mScrWidth:
                            # if particle goes beyond the screen borders then we simply destroy it
                            to_remove.add(curParticle)
                            self.mScore -= consts.SCORE_STEP

            if collidedA != collidedB != None:                
                self.showExplode(collidedA, collidedB)
                self.reflectCircles(collidedA, collidedB)

            if to_remove:
                for item in to_remove: self.mDynObjsGroup.remove(item)
                
            if not collidedParticles:
                
                self.mSimulateBreakup = False

                # mWasCollision flag ensures that we will reduce player
                # lives only by one per collision
                if self.mWasCollision:
                    self.reduceLives()
                    self.mWasCollision = False

                if self.mGameType == consts.GAME_MODE_SURVIVAL:
                    if self.mTimeLeft <= consts.SURVIVAL_FLASH_TIME and not self.mFlashScreen:
                        self.mSndPlayer(self.mSounds['siren'], -1)                        
                        self.mFlashInterp = self.getFlashInterp()                        
                        self.mFlashScreen = True
                                
                # don't count time during collision scene
                self.mTimeLeft -= deltaMS
                
                # if player doesn't have lives left, go to game over state
                if self.mLives == 0:
                    pygame.mixer.stop()
                    self.mShutterFunc = tools.getShutterEffectDrawer(self.mSurface, self.mImgVBar, self.mScrWidth, 2000)
                    self.changeState(consts.STATE_GAMEOVER)
                    self.mSndPlayer(self.mSounds['gameover'])
        
        elif self.mState == consts.STATE_MAIN_MENU:
            self.mMainMenu.update()
            
        elif self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
            self.mScoreMenu.update()
            
        elif self.mState == consts.STATE_ENTER_NAME:
            if self.mNameBox.finished:
                self.mHSManager.insertScore(Game.getGameTypeString(self.mGameType), self.mNameBox.value, self.mScore, self.mReplayData)
                if self.mIsServerScore:
                    try:
                        self.mHSManagerServer.insertScore(Game.getGameTypeString(self.mGameType), self.mNameBox.value, self.mScore, self.mReplayData)
                    except IOError:
                        pass
                self.mHSManager.saveScoreData()
                self.startNewGame(self.mGameType)
                
        elif self.mState == consts.STATE_FINISH_CONFIRM:
            self.mDlgConfirm.update()

        elif self.mState == consts.STATE_SHOW_HIGH_SCORES:
            self.mHSDrawer.update()
    
    def drawHUD(self):
        """ Draw Head Up Interface """
        # draw lives left
        x = consts.LIVES_HUD_X
        for j in range(consts.MAX_LIVES):
            tmpImg = self.mImgStarFull if j < self.mLives else self.mImgStarEmpty
            self.mSurface.blit(tmpImg, (x, consts.LIVES_HUD_Y))
            x += tmpImg.get_width()
        # draw last direction arrow
        if self.mDirectionShown:
            x = self.mScrWidth - consts.DIRECT_HUD_X_OFFSET
            y = consts.DIRECT_HUD_Y
            tools.drawAligned(self.mSurface, self.mArrowImgsHUD[self.mDirection], x, y, tools.HORIZ_CENTER | tools.VERT_CENTER)
        # draw score
        scrPosX = self.mScrWidth >> 1
        tools.drawTextAligned(self.mSurface, self.smallfont, 'Score', scrPosX, 15, (255, 255, 255), tools.HORIZ_CENTER | tools.VERT_CENTER)
        tools.drawTextAligned(self.mSurface, self.smallfont, str(self.mScore), scrPosX, 30, (255, 255, 255), tools.HORIZ_CENTER | tools.VERT_CENTER)
        # draw game type string        -
        tools.drawTextAligned(self.mSurface, self.smallfont, 'Game type: ' + Game.getGameTypeString(self.mGameType), 0, self.mScrHeight, (100, 100, 100), tools.HORIZ_LEFT | tools.VERT_BOTTOM)
        # draw timeleft in survival mode
        #if self.mGameType == strings.STR_MAIN_MENU_SURVIVE:
        if self.mGameType == consts.GAME_MODE_SURVIVAL:
            tools.drawTextAligned(self.mSurface, self.medfont, str((self.mTimeLeft / 1000) + 1), self.mScrWidth >> 1, self.mScrHeight, (255, 255, 255), tools.HORIZ_CENTER | tools.VERT_BOTTOM)
        self.mFinishButton.paint(self.mSurface) 
            
    def drawBackground(self):
        """ Draw dynamical background """
        # draw grid
        for y in range(0, self.mScrHeight, consts.GRID_STEP_XY):
            pygame.draw.line(self.mSurface, (55, 55, 55), (0, y), (self.mScrWidth, y), 1)
        for x in range(0, self.mScrWidth, consts.GRID_STEP_XY):
            pygame.draw.line(self.mSurface, (55, 55, 55), (x, 0), (x, self.mScrHeight), 1)
        
        if not self.mIsReducedEffects:
            if self.mState == consts.STATE_PLAY:
                time_passed = self.mGameTime - self.mBGChangeTime
                a = (consts.BG_CHANGE_TIME_MS - 2 * consts.BG_FADE_TIME_MS)
                if time_passed >= a and time_passed < a + consts.BG_FADE_TIME_MS:
                    # start bg fade out transition
                    p = consts.BG_MAX_ALPHA - (consts.BG_MAX_ALPHA * (time_passed - a)) / consts.BG_FADE_TIME_MS
                    self.mBacks[self.mBackIdx].set_alpha(p)
                    while self.mNewBackIdx == self.mBackIdx:
                        self.mNewBackIdx = random.randint(0, len(self.mBacks) - 1)
                elif time_passed >= consts.BG_CHANGE_TIME_MS - consts.BG_FADE_TIME_MS and time_passed < consts.BG_CHANGE_TIME_MS:
                    # choose new random wallpaper
                    p = (consts.BG_MAX_ALPHA * (time_passed - (consts.BG_CHANGE_TIME_MS - consts.BG_FADE_TIME_MS))) / consts.BG_FADE_TIME_MS
                    self.mBackIdx = self.mNewBackIdx
                    self.mBacks[self.mBackIdx].set_alpha(p)
                elif time_passed >= consts.BG_CHANGE_TIME_MS:
                    self.mBGChangeTime = pygame.time.get_ticks()
                    self.mBacks[self.mBackIdx].set_alpha(consts.BG_MAX_ALPHA)
                
            tools.drawAligned(self.mSurface, self.mBacks[self.mBackIdx], 0, 0, tools.HORIZ_LEFT | tools.VERT_TOP)
        
    def paint(self, deltaMS):
        """ Draws everything in the game :) """
        
        # It may seem strange that I pass deltaMS into it, but it was done just for convenience. 

        if self.mState == consts.STATE_PLAY or self.mState == consts.STATE_PAUSED or self.mState == consts.STATE_GAMEOVER \
            or self.mState == consts.STATE_PREPARE or self.mState == consts.STATE_FINISH_CONFIRM:
                        
            self.mColorIdx = 0
            
            if self.mFlashScreen:
                if self.mState == consts.STATE_PLAY:
                    self.mColorIdx = self.mFlashInterp(deltaMS)                
                if self.mColorIdx <= 0: 
                    self.mFlashInterp = self.getFlashInterp()
                    self.mColorIdx = self.mFlashInterp(0)
                        
            self.mSurface.fill( (self.mColorIdx, 0, 0) )
            self.drawBackground()                                                

            if consts.__DEBUG__:
                # draw bounding boxes
                for obj in self.mDynObjsGroup:
                    pygame.draw.rect(self.mSurface, (255, 255, 255), pygame.Rect(obj.coord_x, obj.coord_y, obj.rect.width, obj.rect.height))

            self.mDynObjsGroup.draw(self.mSurface)

            if self.mAnimateDirection:
                # draw direction arrow if needed
                arrowImg = self.mArrowImgs[self.mDirection]            
                k = (1.0 * self.mDirectionAnimationTime / consts.DIRECT_ANIM_SCALE_TIME)
                k_x = arrowImg.get_width() - int(arrowImg.get_width() * k)
                k_y = arrowImg.get_height() - int(arrowImg.get_height() * k)
                tempImg = pygame.transform.scale(arrowImg, (k_x, k_y))
                tempImg.set_alpha(255 * k)
                tools.drawAligned(self.mSurface, tempImg, self.mScrWidth >> 1, self.mScrHeight >> 1, tools.HORIZ_CENTER | tools.VERT_CENTER)
                                
            if self.mState == consts.STATE_PLAY:
                m_x, m_y = pygame.mouse.get_pos()
                ghost_img = self.mImgSmallShadow if (self.mNextDot.get_rect().width >> 1) == consts.SMALL_DOT_RADIUS else self.mImgBigShadow
                tools.drawAligned(self.mSurface, ghost_img, m_x, m_y, tools.HORIZ_CENTER | tools.VERT_CENTER)
                self.mParticlesGroup.draw(self.mSurface)
                
            self.drawHUD()
            
            if self.mState == consts.STATE_PAUSED:
                self.mShutterFunc(deltaMS)
                self.mMsgPaused.paint(self.mSurface)                
            elif self.mState == consts.STATE_GAMEOVER:
                self.mShutterFunc(deltaMS)
                self.mMsgGameOver.paint(self.mSurface)
               # if res: self.gameOver()                    
            elif self.mState == consts.STATE_PREPARE:
                self.mShutterFunc(deltaMS)
                self.mMsgReady.paint(self.mSurface)
            elif self.mState == consts.STATE_FINISH_CONFIRM:
                self.mShutterFunc(deltaMS)
                self.mDlgConfirm.paint(self.mSurface)                
            
        elif self.mState == consts.STATE_MAIN_MENU:
            
            self.mSurface.fill( (0, 0, 0) )
            self.mMainMenu.draw(self.mSurface, self.mScrWidth, self.mScrHeight)
            
        elif self.mState == consts.STATE_CHOOSE_SCORE_TYPE:
            
            self.mSurface.fill( (0, 0, 0) )
            self.mScoreMenu.draw(self.mSurface, self.mScrWidth, self.mScrHeight)
            
        elif self.mState == consts.STATE_SHOW_HIGH_SCORES:
            
            self.mSurface.fill( (0, 0, 0) )
            self.mHSDrawer.draw(self.mSurface)
            
        elif self.mState == consts.STATE_ENTER_NAME:
            
            self.mNameBox.draw(self.mSurface)
        
        elif self.mState == consts.STATE_ABOUT:
        
            tools.drawAligned(self.mSurface, self.mInstrScreen, 0, 0)

        elif self.mState == consts.STATE_CONNECT:

            Game.msgConnect.paint(self.mSurface)

        if self.mScreenFall != None:
            result = self.mScreenFall(deltaMS)
            if self.mState == consts.STATE_PLAY and not self.mDirectionShown and not result:
                self.mFirstShowDirection = True                
            
        pygame.display.flip()


pyDotterGame = Game()
pyDotterGame.showMainMenu()
