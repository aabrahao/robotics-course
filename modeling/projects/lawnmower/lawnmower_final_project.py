'''
Lawn mower robot modeling, control and simulation
https://youtu.be/2Rhsv8fFqCE


Florida International University
EML 4806 Modeling & EML 5808 Robot Control
Instructor: Anthony Abrahao
Fall 2025
Miami, FL 

Units are expressed in SI: 

    - Distance in meters (m)
    - Angles in radians (rad)
    - Time in seconds (s).
'''

team = ['Name roboticist 1', 
        'Name roboticist 2', 
        'Name roboticist 3']

import matplotlib.pyplot as plt
from math import sin, cos, pi
from numpy.random import uniform as random

from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade, BladeState
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

from eml4806.geometry.vector import Vector, toVector, toVectors, split, join, length, distance, angle, coincident
from eml4806.geometry.vector import unit, perpendicular, dot, cross, is_zero, project, reject, reflect
from eml4806.geometry.vector import clamp, lerp, midpoint, rotate, polar
from eml4806.geometry.angle import radians, wrap
from eml4806.geometry.line import Line

from eml4806.graphics.workspace import Workspace

from eml4806.sensor.keyboard import key as readKeyboard

from eml4806.task.context import Context
from eml4806.task.task import MoveToTask, RotateToTask, WaitTask, BladeControlTask, HaltTask
from eml4806.task.executor import Executor

from eml4806.robot.lawn import generateLawn

# -------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Mission planner
# -------------------------------------------------------------------------

def planMission(lawn, context, polyline):
    
    # Enviroment variables
    dock_position = context.dock_position
    dock_heading = context.dock_heading
    tool_diameter = context.robot.blade.diameter

    # -------------------------------------------------------------------------
    # TODO: STUDENTS — IMPLEMENT YOUR SCAN-PATTERN FUNCTION HERE
    # -------------------------------------------------------------------------
    #
    # Your task:
    #   • Write a function that takes the lawn polygon (4-corner or general)
    #     and produces an ordered list of scan-path waypoints.
    #   • Once implemented, you should call your function as:
    #
    #         waypoints = makeScanGrid(lawn, tool_diameter)
    #
    # IMPORTANT:
    #   • The placeholder below MUST be removed.
    #   • It exists only to allow the starter code to run without errors.
    #
    # DELETE the next line and replace it with your call to makeScanGrid(...):
    #

    waypoints = lawn        # REMOVE THIS LINE
    #waypoints = makeScanGrid(lawn, tool_diameter)   # Add your function call
    
    # -------------------------------------------------------------------------

    # Scanline
    points = toVectors(waypoints)
    n = len(points)
    if n < 2:
        return []
            
    # Show raser patter
    polyline.set(points)
    
    # Scheduling mowing tasks    
    tasks = []
    for i in range(n):

        # Postion
        position = points[i]

        # Heading
        if i % 2 == 0: # Even index!
            heading = angle(points[i+1] - position)
        else: # Odd index
            heading = angle(position - points[i-1]) 
                
        # Transect
        tasks.append( MoveToTask(position, heading) )
            
        # Turn blade on/off
        if i % 2 == 0: # Even index!
            tasks.append( BladeControlTask(BladeState.LOW) )
        else: # Odd index
            tasks.append( BladeControlTask(BladeState.OFF) )
        
    # Dock
    tasks.append( MoveToTask(dock_position, dock_heading + pi) )
    tasks.append( HaltTask() )

    return tasks

# =============================================================================
# Application
# =============================================================================

def main():

    menu = ['Commands:',
            '[r] Randomize',
            '[b] Blade (off/low/high)',
            '[d] Debug on/off',
            '[q] Quit']

    # World
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin), menu, team)
    
    # Robot intitial position
    dock_position = Vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # Robot model
    # ClearPath Husky A200 Ground Platform
    # https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a200/user_manual_husky/

    chassis = Chassis()
    chassis.length = 0.812  # m
    chassis.width = 0.421  # m
    chassis.wheelbase = 0.512  # m
    chassis.trackwidth = 0.550  # m

    wheels = Wheel()
    wheels.diameter = 0.330  # m
    wheels.width = 0.114  # m

    motors = Motor()
    motors.maximum_angular_velocity = 5.45  # rad/s (~52 rpm maximum)
    
    blade = Blade()
    blade.diameter = 0.9 * chassis.width  # m

    odometer = AnalyticalSkidDriveOdometer()
    odometer.track_width = chassis.trackwidth
    odometer.maximum_linear_velocity = None # 1.0  # m/s
    odometer.maximum_angular_velocity = None # 3.5  # rad/s

    # Robot
    robot = Robot(world, dock_position, dock_heading, chassis, wheels, motors, blade, odometer)

    # Simulation settings
    robot.setDebug(True)
    autonomous = True
    randomize = False

    # Controls
    v = 0.0  # Robot linear speed (m/s)
    w = 0.0  # Robot angular speed (rad/s)
    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = radians(60.0) # rad/s
    
    # Lawn
    n = 4
    border = 0.2
    lawn = generateLawn(xmin, ymin, (xmax-xmin), (ymax-ymin), border, n)
    
    # Graphics
    docking_rectangle  = world.rectangle(center=dock_position, size=(chassis.length, chassis.width), angle=dock_heading, color='gray')
    docking_point      = world.point(center=dock_position, color='gray')
    lawn_polyline      = world.polyline(lawn, color='gray', width=2, marker='o', closed=True)
    scan_polyline      = world.polyline(lawn, color='seagreen', width=1, marker='o', closed=False)

    # Remember mission enviromental variables
    context = Context()
    context.robot = robot
    context.vmax = vmax
    context.wmax = wmax
    context.dock_position = dock_position
    context.dock_heading = dock_heading

    # Plan mission
    mission = planMission(lawn, context, scan_polyline)

    # Task exectuter
    exercuter = Executor(context, mission)

    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    while True:
        
        # User imput
        key = readKeyboard()

        if key == 'q': # Quit
            break
        elif key == 'r': # Randomize worksapce
            randomize = True
        elif key == 'b':
            robot.toggleBladeState()
        elif key == 'd': # Debug mode (on/off)
            if robot.debug():
                scan_polyline.hide()
                robot.setDebug(False)
            else:
                scan_polyline.show()
                robot.setDebug(True)
                    
        # Shuffle things around...
        if randomize:
            robot.reset()
            n = len(lawn)
            lawn = generateLawn(xmin, ymin, (xmax-xmin), (ymax-ymin), border, n)
            lawn_polyline.set(lawn)
            mission = planMission(lawn, context, scan_polyline)
            exercuter.set(mission)
            randomize = False

        # Execute mission tasks
        exercuter.run(dt)

        # Simulation
        world.update()
        t += dt
    
    print('Bye!')

if __name__ == '__main__':
    main()