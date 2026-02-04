#! /usr/bin/env python
#coding=utf-8

"""
    2011 Boris Tatarintsev
    
    I extend pygame's standart class to add my own methods
    and parameters to sprites

"""

import pygame
import random
import tools
import consts

import __main__

class MySprite(pygame.sprite.Sprite):
    
    def __init__(self, image, gr, coords, direction):
        # init parent
        pygame.sprite.Sprite.__init__(self, gr)
        # we coordinates as tuples now
        
        self.image = image
        self.rect = image.get_rect()
        self.rect.left, self.rect.top = coords
        
        self.mCoords = coords
        self.mDirection = direction                
        self.mRadius = self.width >> 1
        self.mCollide = False
        self.mVel = self.computeVelocity(self.mDirection) 
        self.mInvVel = tools.inv(self.mVel)
        self.mMass = random.randint(10, 20) if self.mRadius == consts.SMALL_DOT_RADIUS else random.randint(20, 30)
        self.resetLiveTimer()
    
    def resetLiveTimer(self):
        self.mLiveTimer = tools.getLinearInterp(0, 100, consts.COLLIDED_DOT_LIVE_TIME)
    
    def update(self, deltaMS):
        """ Update particle coordinates """
        self.coord_x += self.v_x * deltaMS
        self.coord_y += self.v_y * deltaMS
        self.rect.left = self.coord_x
        self.rect.top = self.coord_y        
            
    def computeVelocity(self, direction):
        """ Setup the speed new particle should have """
        if direction == consts.DIRECT_LEFT:            
            return -(1.0 * __main__.Game.mScrWidth + self.width) / consts.DOT_TRAVEL_TIME_MS, 0
        elif direction == consts.DIRECT_RIGHT:
            return (1.0 * __main__.Game.mScrWidth + self.width) / consts.DOT_TRAVEL_TIME_MS, 0
        elif direction == consts.DIRECT_UP:
            return 0, -(1.0 * __main__.Game.mScrHeight + self.height) / consts.DOT_TRAVEL_TIME_MS
        elif direction == consts.DIRECT_DOWN:
            return 0, (1.0 * __main__.Game.mScrHeight +  self.height) / consts.DOT_TRAVEL_TIME_MS
    
    @property
    def radius(self):
        return self.mRadius
    
    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
    
    @property
    def dir(self):
        return self.mDirection
    
    @property
    def center(self):
        return (self.coord_x + self.radius, self.coord_y + self.radius)

    @property
    def center_x(self):
        return self.coord_x + self.radius

    @property
    def center_y(self):
        return self.coord_y + self.radius
    
    @property
    def velocity(self):
        return self.mVel
    
    @property
    def invvel(self):
        return self.mInvVel
    
    @velocity.setter
    def velocity(self, vec):
        self.mVel = vec
        self.mInvVel = tools.inv(self.mVel)
    
    @property
    def coords(self):
        return self.mCoords
    
    @property
    def mass(self):
        return self.mMass
    
    # back compatibility with the old code
    
    @property
    def live_timer(self):
        return self.mLiveTimer        
    
    @property
    def collide(self):
        return self.mCollide
    
    @collide.setter
    def collide(self, val):
        self.mCollide = val
    
    @property
    def coord_x(self):
        return self.mCoords[0]
    
    @property
    def coord_y(self):
        return self.mCoords[1]
    
    @coord_x.setter
    def coord_x(self, val):
        self.mCoords[0] = val
    
    @coord_y.setter
    def coord_y(self, val):
        self.mCoords[1] = val
        
    @property
    def v_x(self):
        return self.mVel[0]
    
    @property
    def v_y(self):
        return self.mVel[1]

