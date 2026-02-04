#! /usr/bin/env python
#coding=utf-8

"""

    2011 Boris Tatarintsev
    
    Simple class to display high scores 

"""

import pygame
import tools
import os
import strings
import menu
import consts
import strings

import __main__

from hsbasic import HSBasic
from math import pi
from imagebutton import ImageButton

class HSDrawer(object):

    def __init__(self, hs, hsServ, replayCallaback):
        # init fonts
        fontPath = os.path.join('..', 'font', 'freesansbold.ttf')        
        self.smallfont = pygame.font.Font(fontPath, 13)
        self.bigfont = pygame.font.Font(fontPath, 18)
        self.mHSLocal, self.mHSServer = hs, hsServ
        self.mHS = hs
        self.mTableName = None
        self.mReplayCallback = replayCallaback
        # isLocalScores determine which type of score we are currently showing server or local
        self.showLocalScores = True

        fontPath = os.path.join('..', 'font', 'agentred.ttf')
        self.mTitleFont = pygame.font.Font(fontPath, 18)
        self.mTitleSz = self.mTitleFont.size(strings.STR_MAIN_MENU_HSCORE)

        if self.mHSServer != None:
            # init local/server image button
            imgs1 = { ImageButton.STATE_DISABLED : None, ImageButton.STATE_ENABLED : pygame.image.load(os.path.join('..', 'png', 'network_enabled.png')), \
                    ImageButton.STATE_OVER : pygame.image.load(os.path.join('..', 'png', 'network_over.png')), ImageButton.STATE_CLICK : None }
            imgs2 = { ImageButton.STATE_DISABLED : None, ImageButton.STATE_ENABLED : pygame.image.load(os.path.join('..', 'png', 'local_enabled.png')), \
                    ImageButton.STATE_OVER : pygame.image.load(os.path.join('..', 'png', 'local_over.png')), ImageButton.STATE_CLICK : None }

            self.mServerButton = ImageButton(imgs1, 'server')
            self.mServerButton.addImagesPack('local', imgs2)
            self.mServerButton.setAlign(tools.HORIZ_CENTER | tools.VERT_CENTER)
            self.mServerButton.setPos(100, 100)
            self.mServerButton.setCallback(self.switchLocalServer)
                
        # back is also a rotating menu but it consists of only one button :)
        self.mBack = menu.RotatingMenu(x = 320, y = 240, radius = 220, arc = pi, defaultAngle = pi / 2.0)
        self.mBack.addItem(menu.MenuItem(strings.STR_MENU_BACK))            
        self.mBack.selectItem(0)

    def useTable(self, tableName):
        if not self.showLocalScores:
            self.mHSServer.loadScores(self.mTableName)
        self.mTableName = tableName
        self.mBack.update()
        # generate coordinates for high score table items
        self.coords = []
        self.mSelectedIdx = -1
        if self.mTableName != None:
            x, y = (__main__.Game.mScrWidth >> 1), 10
            y += self.mTitleSz[1] + 5            
            y += self.mTitleSz[1]            
            idx = 0
            while idx < HSBasic.SCORES_COUNT:
                self.coords.append( (x, y) )
                y += 15
                idx += 1
                
    def checkMouseOver(self, m_x, m_y):
        for idx in range(len(self.coords)):
            item = self.coords[idx]
            if m_x >= item[0] - (self.mTitleSz[0] >> 1) and m_x <= item[0] + (self.mTitleSz[0] >> 1) and \
                m_y >= item[1] and m_y <= item[1] + self.smallfont.size('0')[1]:
                return idx            
        return -1

    def switchLocalServer(self):
        if self.mServerButton.getActivePack() == 'server':
            self.mServerButton.setActivePack('local')
        else:
            self.mServerButton.setActivePack('server')            
            
        self.mServerButton.mState = ImageButton.STATE_ENABLED
        self.showLocalScores = not self.showLocalScores

    def update(self):
        if self.mHSServer != None:
            self.mServerButton.update()

    def processEvents(self, events, parent):
        for event in events:
            if self.mHSServer != None and self.mServerButton.processEvents(event):
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == consts.LEFT_MOUSE_BUTTON:
                # check if we clicked a mouse over any of menu items
                m_x, m_y = event.pos
                if self.mSelectedIdx != -1:
                    # start the replay for the selected score
                    # self.mReplayCallback(strings.STR_MAIN_MENU_SURVIVE, self.mHS.getScoreByIdx(self.mTableName, self.mSelectedIdx))
                    pass
                for item in self.mBack.items:
                    metrics = item.getMetrics()
                    if m_x >= metrics[0] and m_y >= metrics[1] and m_x <= metrics[2] and m_y <= metrics[3]:
                        parent.showScoreTypeMenu()
                        return True
            elif event.type == pygame.MOUSEMOTION:
                m_x, m_y = event.pos
                selectedIdx = self.checkMouseOver(m_x, m_y)
                if selectedIdx != -1:
                    self.mSelectedIdx = selectedIdx
                    return True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    parent.showScoreTypeMenu()
                    return True            
        return False
    
    def draw(self, surf):

        if self.mHSServer != None:
            self.mServerButton.paint(surf)

        if self.mTableName != None:            
            x, y = __main__.Game.mScrWidth >> 1, 10
            it = self.mHS.getScoreIter(self.mTableName)
            tools.drawTextAligned(surf, self.mTitleFont, strings.STR_MAIN_MENU_HSCORE, x, y, (255, 255, 255), tools.HORIZ_CENTER | tools.VERT_TOP)
            y += self.mTitleSz[1] + 5
            tools.drawTextAligned(surf, self.smallfont, 'Top ' + str(HSBasic.SCORES_COUNT) + ' Scores (' + str(self.mTableName) + ')', x, y, (0, 100, 255), tools.HORIZ_CENTER | tools.VERT_TOP)
            y += self.mTitleSz[1]
            
            idx, color = 0, (255, 255, 255)
            while idx < HSBasic.SCORES_COUNT:
                try:
                    item = next(it)
                    if idx == self.mHS.getLastScoreIdx(self.mTableName):
                        color = (255, 0, 0)
                    else:
                        color = (255, 255, 255)                    
                    tools.drawTextAligned(surf, self.smallfont, str(item[0]), self.coords[idx][0] - (self.mTitleSz[0] >> 1), self.coords[idx][1], color)
                    tools.drawTextAligned(surf, self.smallfont, str(item[1]), self.coords[idx][0] + (self.mTitleSz[0] >> 1), self.coords[idx][1], (0, 255, 0), tools.HORIZ_RIGHT | tools.VERT_TOP)
                except StopIteration:
                    tools.drawTextAligned(surf, self.smallfont, 'empty', self.coords[idx][0] - (self.mTitleSz[0] >> 1), self.coords[idx][1], (100, 100, 100))
                    tools.drawTextAligned(surf, self.smallfont, '0', self.coords[idx][0] + (self.mTitleSz[0] >> 1), self.coords[idx][1], (0, 100, 0), tools.HORIZ_RIGHT | tools.VERT_TOP)                
                if idx == self.mSelectedIdx:                    
                    pygame.draw.rect(surf, (255, 255, 255), pygame.Rect(self.coords[idx][0] - (self.mTitleSz[0] >> 1), self.coords[idx][1], self.mTitleSz[0], self.smallfont.size('0')[1]), 1)
                y += 15
                idx += 1
                
        self.mBack.draw(surf, __main__.Game.mScrWidth, __main__.Game.mScrHeight)

    @property
    def showLocalScores(self):
        return self.mIsLocalScores

    @showLocalScores.setter
    def showLocalScores(self, val):
        self.mIsLocalScores = val
        if self.mIsLocalScores:
            self.mHS = self.mHSLocal
        else:            
            self.mHS = self.mHSServer
        try:
            self.mHS.loadScores(self.mTableName)
        except IOError:
            pass
