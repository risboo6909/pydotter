#! /usr/bin/env python
#coding=utf-8

import pygame
import tools
import consts

class ImageButton(object):
    
    STATE_DISABLED = 0
    STATE_ENABLED = 1
    STATE_OVER = 2
    STATE_CLICK = 3
    
    def __init__(self, imagesDict, packName = 'default'):        
        self.mImagesPack = { packName: imagesDict }
        self.mImagesDict = packName
        self.mState = ImageButton.STATE_ENABLED
        self.coord_x = self.coord_y = 0
        self.align = 0
        self.mCallback = None
    
    def setCallback(self, callback):
        self.mCallback = callback
    
    def setState(self, state):
        self.mState = state
    
    def setPos(self, x, y):
        self.coord_x, self.coord_y = x, y
        
    def setAlign(self, align):
        self.align = align

    def setActivePack(self, packName):
        self.mImagesDict = packName

    def addImagesPack(self, name, imagesDict):
        self.mImagesPack[name] = imagesDict

    def getActivePack(self):
        return self.mImagesDict

    def getImageRect(self, state):
        return self.mImagesPack[self.mImagesDict][state].get_rect()
    
    def getAlignedCoords(self, pos):
        img = self.mImagesPack[self.mImagesDict][self.mState]
        if img != None:
            c = tools.extractFlags(pos[0], pos[1], img.get_rect().width, img.get_rect().height, self.align)
            delta = tools.sub(pos, c)
            return tools.add(pos, delta)            
        return pos
    
    def processEvents(self, event):
        img = self.mImagesPack[self.mImagesDict][self.mState]
        if img != None and self.mState != ImageButton.STATE_DISABLED:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == consts.LEFT_MOUSE_BUTTON:
                m_x, m_y = self.getAlignedCoords(event.pos)
                if m_x >= self.coord_x and m_x <= self.coord_x + img.get_rect().width and \
                m_y >= self.coord_y and m_y <= self.coord_y + img.get_rect().height:
                    self.mState = ImageButton.STATE_CLICK
                    # call the callback method
                    self.mCallback()
                    return True
        # button was not pressed, return False
        return False
    
    def update(self):
        img = self.mImagesPack[self.mImagesDict][self.mState]
        if img != None and self.mState != ImageButton.STATE_DISABLED:
            m_x, m_y = self.getAlignedCoords(pygame.mouse.get_pos())            
            if m_x >= self.coord_x and m_x <= self.coord_x + img.get_rect().width and \
            m_y >= self.coord_y and m_y <= self.coord_y + img.get_rect().height:
                self.mState = ImageButton.STATE_OVER                
            else:
                self.mState = ImageButton.STATE_ENABLED
            
    
    def paint(self, surf):
        img = self.mImagesPack[self.mImagesDict][self.mState]
        if img != None:
            tools.drawAligned(surf, img, self.coord_x, self.coord_y, self.align)
