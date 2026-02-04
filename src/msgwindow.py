#! /usr/bin/env python
#coding=utf-8

import pygame
import consts
import tools
import os

from imagebutton import ImageButton

class MessageWindow(object):
    
    def __init__(self, centerX, centerY, text, font = None, showIcons = False):
        # init everything else
        fontPath = os.path.join('..', 'font', 'freesansbold.ttf')
        self.defaultfont = pygame.font.Font(fontPath, 18)
        self.mCenterX, self.mCenterY = centerX, centerY
        if font == None: font = self.defaultfont
        self.mText = font.render(text, 1, consts.COLOR_WHITE)
        self.mWidth, self.mHeight = font.size(text) 
        self.mWidth += 8
        self.mIcons = showIcons        
        self.initButtons()
                    
    def initButtons(self):
        imgs = { ImageButton.STATE_DISABLED : None, ImageButton.STATE_ENABLED : pygame.image.load(os.path.join('..', 'png', 'ok.png')), \
                ImageButton.STATE_OVER : pygame.image.load(os.path.join('..', 'png', 'ok_over.png')), ImageButton.STATE_CLICK : None }
                        
        self.mOkButton = ImageButton( imgs )
        
        if self.mIcons:
            self.mHeight += self.mOkButton.getImageRect(ImageButton.STATE_ENABLED).height + 4
        
        self.mOkButton.setAlign(tools.HORIZ_RIGHT | tools.VERT_BOTTOM)        
        self.mOkButton.setPos( self.mCenterX - 4, self.mCenterY + (self.mHeight >> 1) - 2 )        
        self.mOkButton.setCallback(self.positiveClick)

        imgs = { ImageButton.STATE_DISABLED : None, ImageButton.STATE_ENABLED : pygame.image.load(os.path.join('..', 'png', 'cancel.png')), \
        ImageButton.STATE_OVER : pygame.image.load(os.path.join('..', 'png', 'cancel_over.png')), ImageButton.STATE_CLICK : None }

        self.mCancelButton = ImageButton( imgs )
        self.mCancelButton.setAlign(tools.HORIZ_LEFT | tools.VERT_BOTTOM)
        self.mCancelButton.setPos( self.mCenterX + 4, self.mCenterY + (self.mHeight >> 1) - 2 )        
        self.mCancelButton.setCallback(self.negativeClick)
    
    def setPositiveCallback(self, callback, *args):
        self.mOkCallback = callback
        self.mOkArgs = args
    
    def setNegativeCallback(self, callback, *args):
        self.mCancelCallback = callback
        self.mCancelArgs = args
    
    def positiveClick(self):        
        self.mOkButton.setState(ImageButton.STATE_ENABLED)
        self.mOkCallback(*self.mOkArgs)
        
    def negativeClick(self):        
        self.mCancelButton.setState(ImageButton.STATE_ENABLED)
        self.mCancelCallback(*self.mCancelArgs)

    def processEvents(self, event):
        if not self.mOkButton.processEvents(event):
            self.mCancelButton.processEvents(event)

    def update(self):
        if self.mIcons:
            self.mOkButton.update()
            self.mCancelButton.update()

    def paint(self, surf):        
        pygame.draw.rect(surf, consts.COLOR_GRAY, pygame.Rect(self.mCenterX - (self.mWidth >> 1), self.mCenterY - (self.mHeight >> 1), self.mWidth, self.mHeight), 0)
        surf.blit(self.mText, (self.mCenterX - (self.mWidth >> 1) + 4, self.mCenterY - (self.mHeight >> 1)))
        if self.mIcons:
            # show buttons if needed
            self.mOkButton.paint(surf)
            self.mCancelButton.paint(surf)
