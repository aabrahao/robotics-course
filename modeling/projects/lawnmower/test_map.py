# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt

from numpy import sin, cos, pi
from numpy.random import uniform as random

import eml4806.sensor.keyboard as keyboard
import eml4806.geometry.angle as angle

import eml4806.graphics.workspace as worksapce
import eml4806.graphics.shape as shape

from eml4806.graphics.style import pen, brush

from eml4806.geometry.vector import Vector, toVector, toVectors, join

from eml4806.graphics.map import Map

def main():

    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = worksapce.Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin))
    
    image = Map.load("eml4806/data/baboon.bmp")
    print(image.dtype)
    print(image.shape)

    map = world.map((xmin, ymin), (xmax-xmin, ymax-ymin), image)

    x, y, w, h = map.rectangle()
    map.circle(      x,       y, 0.1*w)
    map.circle(x+0.5*w, y+0.5*h, 0.1*w)
    map.circle(x+0.5*w,       y, 0.1*w)
    map.circle(    x+w,     y+h, 0.1*w)

    while True:
        
        key = keyboard.key()
        if key == 'q': 
            break
    
        world.update()
    
    print('Bye!')

if __name__ == '__main__':
    main()