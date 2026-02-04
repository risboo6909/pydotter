#! /usr/bin/env python
#coding=utf-8

"""
    2011 Boris Tatarintsev
    
    Extend standart pygame Group class to add specific behaviour.
    This class is for drawing moving particles.

"""

import pygame
import tools
import random

class MyGroup(pygame.sprite.Group):
    
    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def draw(self, surface):
        """ Here we have own drawer to draw tails for particles """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            if spr.collide:
                # draw tail            
                a = tools.add(spr.coords, tools.mul(spr.invvel, 100))
                a = int(a[0]), int(a[1])
                mag = tools.magnitude(spr.invvel)                
                for j in range(int(20 * mag)):
                    c_x = random.randint(a[0], a[0] + spr.width)
                    c_y = random.randint(a[1], a[1] + spr.height)
                    color = random.randint(0, 255)
                    surface.set_at((c_x, c_y), (color, color, color))
            
        self.lostsprites = []
