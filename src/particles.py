#! /usr/bin/env python
#coding=utf-8

"""

    Very simple and basic particles implementation.
    Taken from http://www.scriptedfun.com/particle-effects-for-games/

"""

import pygame

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, vx, vy, ax, ay, size, colorstructure):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.vx, self.vy, self.ax, self.ay = vx, vy, ax, ay
        self.images = []
        for x in colorstructure:
            start, end, duration = x
            startr, startg, startb = start
            endr, endg, endb = end
            def f(s, e, t):
                return s + int((e - s)*(t/float(duration)))
            for t in range(duration):
                image = pygame.Surface((size, size)).convert()
                image.fill((f(startr, endr, t), f(startg, endg, t), f(startb, endb, t)))
                self.images.append(image)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center = pos)
    def update(self, *args):
        deltaMS = args[0]
        self.rect.move_ip(self.vx * deltaMS, self.vy * deltaMS)
        self.vx = self.vx + self.ax * deltaMS
        self.vy = self.vy + self.ay * deltaMS
        if not self.images:
            self.kill()
        else:
            self.image = self.images.pop(0)
    