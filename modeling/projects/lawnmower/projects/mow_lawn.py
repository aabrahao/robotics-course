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

import numpy as np
import matplotlib.pyplot as plt
from math import sin, cos, pi
from numpy.random import uniform as random

from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade, BladeState
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

from eml4806.geometry.vector import vector, vectors, angle
from eml4806.geometry.angle import radians
from eml4806.geometry.line import Line

from eml4806.graphics.scene import Workspace

from eml4806.sensor.keyboard import key as read_keyboard

from eml4806.task.context import Context
from eml4806.task.task import MoveToTask, RotateToTask, WaitTask, BladeControlTask, HaltTask
from eml4806.task.executor import Executor

from eml4806.robot.lawn import generate_convex_polygon
from eml4806.robot.path import generate_raster_path

# -------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# Mission planner
# -------------------------------------------------------------------------

def plan_mission(lawn, context, polyline):
    
    # Environment variables
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
    #         waypoints = make_scan_grid(lawn, tool_diameter)
    #
    # IMPORTANT:
    #   • The placeholder below MUST be removed.
    #   • It exists only to allow the starter code to run without errors.
    #
    # DELETE the next line and replace it with your call to make_scan_grid(...):
    #

    #waypoints = lawn        # REMOVE THIS LINE
    waypoints = generate_raster_path(lawn, tool_diameter)   # Add your function call
    
    # -------------------------------------------------------------------------

    # Scan grid
    points = vectors(waypoints)
    n = len(points)
    if n < 2:
        return []
            
    # Show raster pattern
    polyline.set(points)
    
    # Scheduling mowing tasks    
    tasks = []
    for i in range(n):

        # Position
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
    x_min = -2.0
    x_max = 10.0
    y_min = -1.0
    y_max = 10.0

    world = Workspace(x_min, y_min, x_min + (x_max - x_min), y_min + (y_max - y_min), menu, team)
    
    # Robot initial position
    dock_position = vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # Robot model
    # ClearPath Husky A200 Ground Platform
    # https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a200/user_manual_husky/

    chassis = Chassis(
        length = 0.812,
        width = 0.421,
        wheelbase = 0.512,
        trackwidth = 0.550
    )

    wheels = Wheel(
        diameter = 0.330,
        width = 0.114
    )

    motors = Motor(
        maximum_angular_velocity = 5.45
    )
    
    blade = Blade(
        diameter = 0.9 * chassis.width
    )

    odometer = AnalyticalSkidDriveOdometer(
        track_width = chassis.trackwidth,
        maximum_linear_velocity = None, # 1.0  # m/s
        maximum_angular_velocity = None # 3.5  # rad/s
    )

    # Robot
    robot = Robot(world, dock_position, dock_heading, chassis, wheels, motors, blade, odometer)

    # Simulation settings
    robot.set_debug(True)
    autonomous = True
    randomize = False

    # Controls
    v = 0.0  # Robot linear speed (m/s)
    w = 0.0  # Robot angular speed (rad/s)
    v_max = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    w_max = radians(60.0) # rad/s
    
    # Lawn
    n = 4
    border = 0.2*(x_max-x_min)
    lawn = generate_convex_polygon(n, x_min, y_min, x_max-x_min, y_max-y_min, randomness=0.1, padding=border)
    
    # Graphics
    docking_rectangle  = world.rectangle(center=dock_position, size=(chassis.length, chassis.width), angle=dock_heading, color='gray')
    docking_point      = world.point(center=dock_position, color='gray')
    lawn_polyline      = world.polyline(lawn, color='gray', width=2, marker='o', closed=True)
    scan_polyline      = world.polyline(lawn, color='seagreen', width=1, marker='o', closed=False)

    # Remember mission environmental variables
    context = Context()
    context.robot = robot
    context.v_max = v_max
    context.w_max = w_max
    context.dock_position = dock_position
    context.dock_heading = dock_heading

    # Plan mission
    mission = plan_mission(lawn, context, scan_polyline)

    # Task executor
    executor = Executor(context, mission)

    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    while True:
        
        # User input
        key = read_keyboard()

        if key == 'q': # Quit
            break
        elif key == 'r': # Randomize workspace
            randomize = True
        elif key == 'b':
            robot.toggleBladeState()
        elif key == 'd': # Debug mode (on/off)
            if robot.debug():
                scan_polyline.hide()
                robot.set_debug(False)
            else:
                scan_polyline.show()
                robot.set_debug(True)
                    
        # Shuffle things around...
        if randomize:
            robot.reset()
            n = len(lawn)
            lawn = lawn = generate_convex_polygon(n, x_min, y_min, x_max-x_min, y_max-y_min, randomness=0.9, padding=border)
            lawn_polyline.set(lawn)
            mission = plan_mission(lawn, context, scan_polyline)
            executor.set(mission)
            randomize = False

        # Execute mission tasks
        executor.run(dt)

        # Simulation
        world.update()
        t += dt
    
    print('Bye!')

if __name__ == '__main__':
    main()