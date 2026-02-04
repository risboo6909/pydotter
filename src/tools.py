#! /usr/bin/env python
#coding=utf-8

"""
    2011 Boris Tatarintsev

    This file contains mostly mathematical functions such as
    vector reflection, aabb vs aabb sweep test, circle vs circle sweep test,
    various vector operations, etc.
    
    It also contains some auxiliary functions and procedures which make
    my life easier. :)
    
"""


import pygame
import os
import glob
import random
import math
import pickle

from io import BytesIO, StringIO

epsilon = 1e-9
huge = 1e+10

HORIZ_LEFT = 1
HORIZ_RIGHT = 2
HORIZ_CENTER = 4
VERT_TOP = 8
VERT_BOTTOM = 16
VERT_CENTER = 32

def extractFlags(x, y, w, h, align):
    if align & HORIZ_LEFT:
        x = x
    elif align & HORIZ_RIGHT:
        x = x - w
    elif align & HORIZ_CENTER:
        x = x - w / 2
    
    if align & VERT_TOP:
        y = y
    elif align & VERT_BOTTOM:
        y = y - h
    elif align & VERT_CENTER:
        y = y - h / 2
    
    return x, y

def drawAligned(surf, img, x, y, align = (HORIZ_LEFT | VERT_TOP)):        
    x, y = extractFlags(x, y, img.get_width(), img.get_height(), align)            
    surf.blit(img, (x, y))
    
def drawTextAligned(surf, fnt, string, x, y, color, align = (HORIZ_LEFT | VERT_TOP)):
    w, h = fnt.size(string)
    x, y = extractFlags(x, y, w, h, align)
    rendered = fnt.render(string, 1, color)
    surf.blit(rendered, (x, y))

def getSoundPlayer(soundEnabled):
    # just a small closure to keep soundEnabled option available for play    
    def play(sound, loop = 0):
        if soundEnabled: sound.play(loop)
    return play

def getShutterEffectDrawer(surf, img, scr_width, max_t):
    count = max(1, scr_width // img.get_rect().width)
    timestep = max(1, max_t // count)
    max_t += timestep
    total_time = [timestep]
    def f(deltaMS):            
        x, t = 0, timestep
        if total_time[0] >= max_t:
            total_time[0] = max_t
        for idx in range(count):
            r, m = total_time[0] / t, 0            
            if r > 0:
                if total_time[0] - t >= timestep:
                    m = timestep - 2
                else:
                    m = total_time[0] - t
            alpha = int((150 * m) / max(1, (timestep - 2)))
            img.set_alpha(alpha)
            drawAligned(surf, img, x, 0, HORIZ_LEFT | VERT_TOP)
            x += img.get_rect().width            
            t += timestep
        total_time[0] += deltaMS
        return total_time[0] >= max_t
    return f

def getFallEffectDrawer(surf, scrWidth, scrHeight):
    numHoriz, numVert = 20, 10
    partWidth, partHeight = max(1, scrWidth // numHoriz), max(1, scrHeight // numVert)
    effectFinished = [False]
    parts = []
    # create surfaces and fill them with the screen image
    for idx in range(numHoriz * numVert):
        # ok so, this looks horrible but it's actually very simple
        # we create a list of sublists where each sublist consists of
        # [x, y, x0, y0, random number in interval [0.05, 0.01) which will represent speed, surface of size partWidth, partHeight]
        parts.append([0, 0, 0, 0, random.uniform(0.05, 0.1), pygame.Surface((partWidth, partHeight))])
    
    # here what we do is taking each of the small early generated surface and
    # render the whole screen into them with specific offset to the top-left,
    # so each surface contains a part of the whole screen
    x, y = 0, 0    
    for part in parts:        
        part[5].blit(surf, (x, y))
        part[0], part[1], part[2], part[3] = abs(x), abs(y), abs(x), abs(y)
        x -= partWidth
        if abs(x) == scrWidth:
            x = 0
            y -= partHeight

    def f(deltaMS):
        # draw generated parts
        if not effectFinished[0]:
            flag = True
            # here we just move generated parts according to the parabolic equation
            # with its extremum point at x0, y0, so the equation will be as follows
            # y = y0 + (0.2 * (x - x0) ^ 2) or in our terms
            # part[1] = part[3] + (0.2 * (part[0] - part[2]) ** 2)
            for part in parts:
                surf.blit(part[5], (part[0], part[1]))
                part[0] += part[4] * deltaMS
                part[1] = part[3] + (0.2 * (part[0] - part[2]) ** 2)
                if part[1] < scrHeight:
                    flag = False
            if flag:
                effectFinished[0] = True
            return True
        return False
    return f

def getFilesByMask(watch_dir, mask):
    pattern = os.path.join(watch_dir, mask) 
    output = []
    for f in glob.glob(pattern): 
        if not os.path.isfile(f): #already did the join in the pattern 
            continue
        output.append(f)
    return output
    
def AABBAABB_Overlap(aabb1, aabb2, k):
    # checks whether 2 aabbs intersect    
    ox1 = aabb1.coord_x + aabb1.radius + k
    ox2 = aabb2.coord_x + aabb2.radius + k
    if abs(ox2 - ox1) > aabb1.radius + aabb2.radius + 2 * k: return False
    oy1 = aabb1.coord_y + aabb1.radius + k
    oy2 = aabb2.coord_y + aabb2.radius + k
    if abs(oy2 - oy1) > aabb1.radius + aabb2.radius + 2 * k: return False
    return True

def circleCircleIntersect(x1, y1, x2, y2, r1, r2, v1, v2, deltaMS):
    
    # compute exact point of two circles intersection
            
    R = r1 + r2
    v_rel = sub(v1, v2)
    d = v_rel[0] * deltaMS, v_rel[1] * deltaMS
    f = x1 - x2, y1 - y2
    a = dot(d, d)
    
    if a <= epsilon:
        
        if dot(f, f) <= R * R:
            # check if we overlap already
            return True, 0
                
        return False, -1
        
    b = 2 * dot(f, d)

    if b > epsilon:
        return False, -1

    c = dot(f, f) - R * R
    
    D = b * b - 4 * a * c

    if D < 0:
        # no intersection
        pass
    else:
        # intersection
        D = math.sqrt(D)
        k = 2.0 * a
        t1 = (-b + D) / k
        t2 = (-b - D) / k
        t = min(t1, t2)

        if t >= 0 and t <= 1:
            return True, t * deltaMS
        
    return False, -1
    

def axisTest(min1, max1, min2, max2, v1, v2, a):
            
    v_rel = 1.0 * (v1 - v2)    
    
    # check if we don't have any realation movement on axis
    # and don't intersect
    if abs(v_rel) < epsilon:

        if min2 >= max1 or max2 <= min1:
            # no stationary intersection
            return False
        else:
            # stationary intersection
            return True
        
    else:
        
        t_min = (min2 - max1) / v_rel
        t_max = (max2 - min1) / v_rel
            
        if t_min > t_max:
            t_min, t_max = t_max, t_min
        
        if a[0] < t_min:
            a[0] = t_min
        if a[1] > t_max:
            a[1] = t_max

        if a[0] <= a[1]:
            return True
        
    return False

def AABB_IntersectTest(aabb1, aabb2, deltaMS):
    
    a = [0, huge]
            
    if not axisTest(aabb1.coord_x, aabb1.coord_x + aabb1.width, aabb2.coord_x, aabb2.coord_x + aabb2.width, aabb1.v_x, aabb2.v_x, a):
        return False, -1

    if not axisTest(aabb1.coord_y, aabb1.coord_y + aabb1.height, aabb2.coord_y, aabb2.coord_y + aabb2.height, aabb1.v_y, aabb2.v_y, a):
        return False, -1
        
    if a[0] <= deltaMS:
        # intersection
        return True, a[0]    
    return False, -1
    
def getCirclesReflection(c1, v1, c2, v2):
    """
        c1 - first circle center, v1 - first circle speed vector
        c2 - second circle center, v2 - second circle speed vector
        
        computes reflection of two circles and returns their
        result speeds
    """
    # compute normal
    n1 = normalize( ( c1[0] - c2[0], c1[1] - c2[1] ) )    
    v12 = getReflection(v1, n1)
    v22 = getReflection(v2, n1)
    return v12, v22

def circlesOverlap(c1, c2, r1, r2):
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]    
    a = (dx * dx + dy * dy)
    b = (r1 + r2) ** 2
    return a <= b, b - a

def normalize(v):
    # 2d-vector normalization
    m = math.sqrt(v[0] * v[0] + v[1] * v[1])
    inv_mag = 0
    if m != 0:
        inv_mag = 1.0 / m
    return ( v[0] * inv_mag, v[1] * inv_mag )

def projV(v, a):
    # vector projection of vector v to vector a
    n = normalize(a)
    return mul(n, dot(v, n))

def proj(v, a):
    # projects vector v to vector a
    n = normalize(a)
    return dot(v, n)

def dot(a, b):
    # computes dot product of two 2d vectors
    return a[0] * b[0] + a[1] * b[1]

def inv(a):
    return ( -a[0], -a[1] )

def sub(a, b):
    # substract vector b from vector a
    return ( a[0] - b[0], a[1] - b[1] )

def add(a, b):
    # add vector b to vector a
    return ( a[0] + b[0], a[1] + b[1] )

def magnitude(a):
    return ( a[0] * a[0] + a[1] * a[1] ) ** 0.5

def mul(a, n):
    # multiply vector a by number n
    return ( (a[0] * n, a[1] * n) )
    
def getReflection(v, n):
    """
        computes reflection of vector v assuming the n is
        a normal vector
        the formula is v1 = v - 2 * dot(n, v) * n
    """
    a = 2 * dot(n, v)
    b = mul(n, a)
    c = sub(v, b)    
    return c

def getLinearInterp(start, end, t_max):
    total = [0]
    def linearInterp(t):
        total[0] += t
        return start + ((end - start) * total[0]) / (1.0 * t_max)
    return linearInterp

def serialize(data):
    stream = BytesIO()
    pickle.dump(data, stream, pickle.HIGHEST_PROTOCOL)
    return stream

def generateRandomString():
    l = random.randint(50, 1000)
    output = StringIO()
    for i in range(l):
        output.write(chr(random.randint(32, 123)))
    return output

def xorEncrypt(data, password = 'default'):
    output = StringIO()
    idx = 0
    for c in data:              
        e = password[idx]
        output.write(chr(ord(c) ^ ord(e)))
        idx += 1
        if idx == len(password):
            idx = 0
    return output
