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

def main():

    menu = '''Keyboard commands
    [m] translate
    [r] Rotate
    [s] Scale
    [ ] Reset
    [q] Quit'''

    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = worksapce.Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin), menu)
    
    points1 = [
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [8.0, 4.0]
    ]

    x = random(0, 8, 5)
    y = random(0, 8, 5)
    print(x)
    print(y)
    points2 = join(x, y)

    rectangle = world.rectangle((4,4), (1, 2),'blue')
    circle = world.circle((4, 5), 2, 'orange')
    polyline = world.polyline(points1,'red', width=2, marker='o')
    polygon = world.polygon(points2, 'green')
    point = world.point((4, 2), 'red')
    arrow = world.arrow((2,1), (1,2), 'magenta', width=3)
    ray = world.ray((1,1), (2,3), 'red')

    r1 = world.rectangle((1,1), (1, 2),'pink')
    r2 = world.rectangle((3,1), (1, 2),'pink')
    g = world.group([r1, r2, circle])

    while True:
        
        key = keyboard.key()
        if key == 'q': 
            break
        elif key == 't':
            rectangle.translate((0.1, 0.1), relative=True)
            circle.translate((0.1, 0.1), relative=True)
            polyline.translate((0.1, 0.1), relative=True)
            polygon.translate((0.1, 0.1), relative=True)
            point.translate((0.1, 0.1), relative=True)
            arrow.translate((0.1, 0.1), relative=True)
            ray.translate((0.1, 0.1), relative=True)
            g.translate((0.1, 0.1), relative=True)
        elif key == 'r':
            rectangle.rotate(0.1, relative=True)
            circle.rotate(0.1, relative=True)
            polyline.rotate(0.1, relative=True)
            polygon.rotate(0.1, relative=True)
            point.rotate(0.1, relative=True)
            arrow.rotate(0.1, relative=True)
            ray.rotate(0.1, relative=True)
            g.rotate(0.1, relative=True)
        elif key == 's':
            rectangle.scale(0.9, relative=True)
            circle.scale(0.9, relative=True)
            polyline.scale(0.9, relative=True)
            polygon.scale(0.9, relative=True)
            point.scale(0.9, relative=True)
            arrow.scale(0.9, relative=True)
            ray.scale(0.9, relative=True)
            g.scale(0.9, relative=True)
        elif key == ' ':
            rectangle.reset()
            circle.reset()
            polyline.reset()
            polygon.reset()
            point.reset()
            arrow.reset()
            ray.reset()
            g.reset()
    
        world.update()
    
    print('Bye!')

if __name__ == '__main__':
    main()