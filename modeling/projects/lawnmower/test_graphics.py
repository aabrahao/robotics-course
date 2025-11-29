# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt

from numpy import sin, cos, pi
from numpy.random import uniform as random

import eml4806.sensor.keyboard as keyboard
import eml4806.geometry.angle as angle
import eml4806.geometry.vector as vector
import eml4806.geometry.pose as pose

import eml4806.graphics.workspace as worksapce
import eml4806.graphics.shape as shape

from eml4806.graphics.style import pen, brush

def main():

    menu = '''Keyboard commands
    [m] Move
    [r] Rotate
    [s] Scale
    [ ] Reset
    [q] Quit'''

    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0
    world = worksapce.Workspace(xmin, xmax, ymin, ymax, menu)
    
    points = vector.ensure([
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [8.0, 4.0]
    ])

    rectangle = shape.Rectangle(world, (1,2), 1, 2, style=brush('blue'))
    circle = shape.Circle(world, (4, 5), 2, style=brush('orange'))
    polyline = shape.Polyline(world, points, style=pen('red', 2), marker='o')
    polygon = shape.Polygon(world, 2 + points, style=brush('green'))
    point = shape.Point(world, (4, 2), style=brush('red'))
    arrow = shape.Arrow(world, (2,1), (1,2), style=brush('magenta', 3))
    ray = shape.Ray(world, (1,1), (2,3), style=brush('red'))

    while True:
        
        key = keyboard.key()
        if key == 'q': 
            break
        elif key == 'm':
            polyline.move((0.1, 0.1), relative=True)
            rectangle.move((0.1, 0.1), relative=True)
            circle.move((0.1, 0.1), relative=True)
            polygon.move((0.1, 0.1), relative=True)
            point.move((0.1, 0.1), relative=True)
            arrow.move((0.1, 0.1), relative=True)
            ray.move((0.1, 0.1), relative=True)
        elif key == 'r':
            polyline.rotate(0.1, relative=True)
            rectangle.rotate(0.1, relative=True)
            circle.rotate(0.1, relative=True)
            polygon.rotate(0.1, relative=True)
            point.rotate(0.1, relative=True)
            arrow.rotate(0.1, relative=True)
            ray.rotate(0.1, relative=True)
        elif key == 's':
            polyline.scale(0.9, relative=True)
            rectangle.scale(0.9, relative=True)
            circle.scale(0.9, relative=True)
            polygon.scale(0.9, relative=True)
            point.scale(0.9, relative=True)
            arrow.scale(0.9, relative=True)
            ray.scale(0.9, relative=True)
        elif key == ' ':
            polyline.reset()
            rectangle.reset()
            circle.reset()
            polygon.reset()
            point.reset()
            arrow.reset()
            ray.reset()
    
        world.update()
    
    print('Bye!')

if __name__ == '__main__':
    main()