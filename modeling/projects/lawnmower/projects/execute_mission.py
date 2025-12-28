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

# -------------------------------------------------------------------------
# Modules
# -------------------------------------------------------------------------

# SciPy
import matplotlib.pyplot as plt
from math import sin, cos, pi
from numpy.random import uniform as random

# Robotics
from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade, BladeState
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

# Geometric
from eml4806.geometry.vector import vector, vectors, angle
from eml4806.geometry.angle import radians
from eml4806.geometry.line import Line

# Graphics
from eml4806.graphics.workspace import Workspace

# User interface
from eml4806.sensor.keyboard import key as read_keyboard

# Task execution
from eml4806.task.context import Context
from eml4806.task.task import MoveToTask, RotateToTask, WaitTask, BladeControlTask, HaltTask
from eml4806.task.executor import Executor

# -------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------

def randomize_waypoints(x_min, x_max, y_min, y_max, n):
    x = random(1.1*x_min, 0.9*x_max, n)
    y = random(1.1*y_min, 0.9*y_max, n)
    return vectors(x, y)

# -------------------------------------------------------------------------
# Mission planner
# -------------------------------------------------------------------------

def plan_mission_1(waypoints, context):
    
    # Environment variables
    dock_position = context.dock_position
    dock_heading = context.dock_heading
    tool_diameter = context.robot.blade.diameter

    # Motion planner
    points = vectors(waypoints)
    n = len(points)
    if n < 2:
        return []
        
    tasks = []
    for i in range(n):

        if i == n-1: # Last point
            h = angle(points[i] - points[i-1])
        else: # All others
            h = angle(points[i+1] - points[i]) 
            
        p = points[i]
        tasks.append( MoveToTask(p, h) )
            
        # Turn blade on/off
        if i % 2 == 0: # Even index!
            tasks.append( BladeControlTask(BladeState.LOW) )
        else: # Odd index
            tasks.append( BladeControlTask(BladeState.OFF) )
        
    # Dock
    tasks.append( MoveToTask(dock_position, dock_heading + pi) )
    tasks.append( HaltTask() )

    return tasks

# -------------------------------------------------------------------------

def plan_mission_2(waypoints, context):

    # Environment variables
    dock_position = context.dock_position
    dock_heading = context.dock_heading
    tool_diameter = context.robot.blade.diameter

    # Motion planner
    
    points = vectors(waypoints)
    n = len(points)
    if n < 2:
        return []

    tasks = []
    for i in range(n):

        if i == 0: # First
            h = angle(points[i+1] - points[i])
            p = points[i]
            tasks.append( MoveToTask(p, h) )
        elif i == n-1: # Last
            h = angle(points[i] - points[i-1])
            p = points[i]
            tasks.append( MoveToTask(p, h) )
            tasks.append( MoveToTask(dock_position, dock_heading + pi) )
        else: # All others
            h = angle(points[i] - points[i-1]) 
            p = points[i]
            tasks.append( MoveToTask(p, h) )
            h = angle( points[i+1] - points[i] )
            tasks.append( RotateToTask( h ) )
        
    tasks.append( HaltTask() )   
        
    return tasks

# =============================================================================
# Simulation
# =============================================================================

def main():

    menu = ['Commands:',
            '[r] Randomize',
            '[b] Blade (off/low/high)',
            '[d] Debug on/off',
            '[1] Mission 1',
            '[2] Mission 2',
            '[q] Quit']

    # -------------------------------------------------------------------------
    # World
    # -------------------------------------------------------------------------
     
    x_min = -2.0
    x_max = 10.0
    y_min = -1.0
    y_max = 10.0

    world = Workspace(x_min, y_min, x_min + (x_max - x_min), y_min + (y_max - y_min), menu)
    
    # -------------------------------------------------------------------------
    # Robot docking station
    # -------------------------------------------------------------------------
    
    dock_position = vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # -------------------------------------------------------------------------
    # Robot model
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Robot
    # -------------------------------------------------------------------------
    
    robot = Robot(world, dock_position, dock_heading, chassis, wheels, motors, blade, odometer)

    # -------------------------------------------------------------------------
    # Simulation settings
    # -------------------------------------------------------------------------

    robot.set_debug(True)
    autonomous = True
    plan = plan_mission_1
    randomize = False
        
    # -------------------------------------------------------------------------
    # Controls
    # -------------------------------------------------------------------------
    
    v = 0.0  # Robot linear speed (m/s)
    w = 0.0  # Robot angular speed (rad/s)

    v_max = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    w_max = radians(60.0) # rad/s
    
    # -------------------------------------------------------------------------
    # Missions
    # -------------------------------------------------------------------------
    
    waypoints = vectors([
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [6.0, 4.0]
    ])

    # -------------------------------------------------------------------------
    # Graphics
    # -------------------------------------------------------------------------

    docking_rectangle  = world.rectangle(center=dock_position, size=(chassis.length, chassis.width), angle=dock_heading, color='gray')
    docking_point      = world.point(center=dock_position, color='gray')
    waypoints_polyline = world.polyline(waypoints, color='gray', width=2.0, marker='o')
      
    # -------------------------------------------------------------------------
    # Task executor
    # -------------------------------------------------------------------------

    # Remember environmental variables
    context = Context()
    context.robot = robot
    context.v_max = v_max
    context.w_max = w_max
    context.dock_position = dock_position
    context.dock_heading = dock_heading

    # Plan mission
    mission = plan(waypoints, context)

    # Schedule
    executor = Executor(context, mission)

    # -------------------------------------------------------------------------
    # Simulation
    # -------------------------------------------------------------------------

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
        elif key == '1': # Change to mission 1
            plan = plan_mission_1
            randomize = True
        elif key == '2': # Change to mission 2
            plan = plan_mission_2
            randomize = True
        elif key == 'd': # Debug mode (on/off)
            robot.set_debug( not robot.debug() )
        
        # Shuffle things around...
        if randomize:
            robot.reset()
            n = len(waypoints)
            waypoints = randomize_waypoints(x_min, x_max, y_min, y_max, n)
            waypoints_polyline.set(waypoints)
            mission = plan(waypoints, context)
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