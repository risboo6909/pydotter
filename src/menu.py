"""

    Nice rotating menu I've taken from pygame.org    
    http://www.pygame.org/project-Rotating+Menu-975-.html

"""

from math import sin, cos, pi

import pygame
import os
import tools

displayWidth = 640
displayHeight = 480
fpsLimit = 90

def sinInterpolation(start, end, steps=30):
    values = [start]
    delta = end - start
    for i in range(1, steps):
        n = (pi / 2.0) * (i / float(steps - 1))
        values.append(start + delta * sin(n))
    return values

class RotatingMenu:
    def __init__(self, x, y, radius, arc=pi*2, defaultAngle=0, wrap=False, drawBg=True):
        """
        @param x:
            The horizontal center of this menu in pixels.
        
        @param y:
            The vertical center of this menu in pixels.
        
        @param radius:
            The radius of this menu in pixels(note that this is the size of
            the circular path in which the elements are placed, the actual
            size of the menu may vary depending on item sizes.
        @param arc:
            The arc in radians which the menu covers. pi*2 is a full circle.
        
        @param defaultAngle:
            The angle at which the selected item is found.
        
        @param wrap:
            Whether the menu should select the first item after the last one
            or stop.
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.arc = arc
        self.defaultAngle = defaultAngle
        self.wrap = wrap
        
        self.rotation = 0
        self.rotationTarget = 0
        self.rotationSteps = [] #Used for interpolation
        
        self.items = []
        self.selectedItem = None
        self.selectedItemNumber = 0
        
        self.mMenuBg = pygame.image.load(os.path.join('..', 'png', 'bg', 'menubg.png'))
        self.mMenuBg.set_alpha(100)
        self.mDrawBg = drawBg
        #self.mPyGameLogo = pygame.transform.scale(self.mPyGameLogo, (150, 60))
        
        fontPath = os.path.join('..', 'font', 'agentred.ttf')
        RotatingMenu.mMenuFont = pygame.font.Font(fontPath, 18)
        fontPath = os.path.join('..', 'font', 'freesansbold.ttf')        
        RotatingMenu.mSmallFont = pygame.font.Font(fontPath, 13)        
        
    
    def addItem(self, item):
        self.items.append(item)
        if len(self.items) == 1:
            self.selectedItem = item
            
    def getSelectedItemText(self):
        return self.selectedItem.text
    
    def getSelectedItem(self):
        return self.selectedItem
    
    def deselectAll(self):
        for item in self.items:
            item.deselect()
    
    def selectItem(self, itemNumber):
        if self.wrap == True:
            if itemNumber > len(self.items) - 1: itemNumber = 0
            if itemNumber < 0: itemNumber = len(self.items) - 1
        else:
            itemNumber = min(itemNumber, len(self.items) - 1)
            itemNumber = max(itemNumber, 0)
        
        self.selectedItem.deselect()
        self.selectedItem = self.items[itemNumber]
        self.selectedItem.select()
        
        self.selectedItemNumber = itemNumber
        
        if len(self.items) > 1:
            self.rotationTarget = - self.arc * (itemNumber / float(len(self.items) - 1))
        else:
            self.rotationTarget = - self.arc * (itemNumber / float(len(self.items)))
            
        self.rotationSteps = sinInterpolation(self.rotation, self.rotationTarget, 45)
    
    def rotate(self, angle):
        """@param angle: The angle in radians by which the menu is rotated.
        """
        for i in range(len(self.items)):
            item = self.items[i]
            if len(self.items) > 1:                
                n = i / float(len(self.items) - 1)
            else:
                n = i / float(len(self.items))
            rot = self.defaultAngle + angle + self.arc * n
            
            item.x = self.x + cos(rot) * self.radius
            item.y = self.y + sin(rot) * self.radius
    
    def update(self):
        if len(self.rotationSteps) > 0:
            self.rotation = self.rotationSteps.pop(0)
            self.rotate(self.rotation)
    
    def draw(self, display, scrWidth, scrHeight):
        """@param display: A pyGame display object
        """
        if self.mDrawBg:
            tools.drawAligned(display, self.mMenuBg, 0, 0)
        tools.drawTextAligned(display, RotatingMenu.mSmallFont, 'Python Dotter 2011 Boris Tatarintsev', scrWidth, scrHeight, (30, 30, 30), tools.HORIZ_RIGHT | tools.VERT_BOTTOM)
        for item in self.items:
            item.draw(display)

class MenuItem:
    def __init__(self, text="Spam"):
        self.text = text
                        
        self.defaultColor = (255,255,255)
        self.selectedColor = (255,0,0)
        self.color = self.defaultColor        
        self.x = 0
        self.y = 0 #The menu will edit these
        
        self.font = RotatingMenu.mMenuFont
        self.image = self.font.render(self.text, True, self.color)
        self.size = self.font.size(self.text)
        self.xOffset = self.size[0] // 2
        self.yOffset = self.size[1] // 2
    
    def getMetrics(self):
        return self.x - self.xOffset, self.y - self.yOffset, \
            self.x - self.xOffset + self.size[0], self.y - self.yOffset + self.size[1]
    
    def select(self):
        """Just visual stuff"""
        self.color = self.selectedColor
        self.redrawText()
    
    def deselect(self):
        """Just visual stuff"""
        self.color = self.defaultColor
        self.redrawText()
    
    def redrawText(self):
        self.font = RotatingMenu.mMenuFont
        self.image = self.font.render(self.text, True, self.color)
        size = self.font.size(self.text)
        self.xOffset = size[0] // 2
        self.yOffset = size[1] // 2
    
    def draw(self, display):
        display.blit(self.image, (self.x-self.xOffset, self.y-self.yOffset))
