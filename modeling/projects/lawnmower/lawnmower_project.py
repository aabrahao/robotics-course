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

-------------------------------------------------------------------

Team:

    - Name roboticist 1
    - Name roboticist 2
    - Name roboticist 3

'''

# -------------------------------------------------------------------------
# Modules
# -------------------------------------------------------------------------

# SciPi
import matplotlib.pyplot as plt
from math import sin, cos, pi
from numpy.random import uniform as random

# Robotics
from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade, BladeState
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

# Geometric
from eml4806.geometry.vector import Vector, toVector, toVectors, split, join, length, distance, angle, coincident
from eml4806.geometry.vector import unit, perpendicular, dot, cross, is_zero, project, reject, reflect
from eml4806.geometry.vector import clamp, lerp, midpoint, rotate, polar
from eml4806.geometry.angle import radians, wrap
from eml4806.geometry.line import Line

# Graphics
from eml4806.graphics.workspace import Workspace

# User interface
from eml4806.sensor.keyboard import key as readKeyboard

# Task exectuion
from eml4806.task.context import Context
from eml4806.task.task import MoveToTask, RotateToTask, WaitTask, BladeControlTask, HaltTask
from eml4806.task.executor import Executor

# -------------------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------------------

def randomizeWaypints(xmin, xmax, ymin, ymax, n):
    x = random(1.1*xmin, 0.9*xmax, n)
    y = random(1.1*ymin, 0.9*ymax, n)
    return join(x, y)

# -------------------------------------------------------------------------
# First mission
# -------------------------------------------------------------------------

def planMission1(waypoints, context):
    
    # Enviroment variables
    dock_position = context.dock_position
    dock_heading = context.dock_heading
    tool_diameter = context.robot.blade.diameter

    # Motion planner
    points = toVectors(waypoints)
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
# Second mission
# -------------------------------------------------------------------------

# Mission Planner 2
def planMission2(waypoints, context):

    # Enviroment variables
    dock_position = context.dock_position
    dock_heading = context.dock_heading
    tool_diameter = context.robot.blade.diameter

    # Motion planner
    
    points = toVectors(waypoints)
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

    menu = '''Keyboard commands
    [r] Randomize
    [d] Debug on/off
    [1] Mission 1
    [2] Mission 2
    [q] Quit'''

    # -------------------------------------------------------------------------
    # World
    # -------------------------------------------------------------------------
     
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin), menu)
    
    # -------------------------------------------------------------------------
    # Robot docking station
    # -------------------------------------------------------------------------
    
    dock_position = Vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # -------------------------------------------------------------------------
    # Robot model
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # Robot
    # -------------------------------------------------------------------------
    
    robot = Robot(world, dock_position, dock_heading, chassis, wheels, motors, blade, odometer)

    # -------------------------------------------------------------------------
    # Simulation settings
    # -------------------------------------------------------------------------

    robot.setDebug(True)
    autonomous = True
    plan = planMission1
    randomize = False
        
    # -------------------------------------------------------------------------
    # Controls
    # -------------------------------------------------------------------------
    
    v = 0.0  # Robot linear speed (m/s)
    w = 0.0  # Robot angular speed (rad/s)

    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = radians(60.0) # rad/s
    
    # -------------------------------------------------------------------------
    # Missions
    # -------------------------------------------------------------------------
    
    waypoints = toVectors([
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [6.0, 4.0]
    ])

    # -------------------------------------------------------------------------
    # Graphics
    # -------------------------------------------------------------------------

    docking_rectangle = world.rectangle(center=dock_position, size=(chassis.length, chassis.width), angle=dock_heading, color='gray')
    docking_point     = world.point(center=dock_position, color='magenta')
    waypoints_ployline = world.polyline(waypoints, color='gray', width=2.0, marker='o')
      
    # -------------------------------------------------------------------------
    # Task executer
    # -------------------------------------------------------------------------

    # Remember enviromental variables
    context = Context()
    context.robot = robot
    context.vmax = vmax
    context.wmax = wmax
    context.dock_position = dock_position
    context.dock_heading = dock_heading

    # Plan mission
    mission = plan(waypoints, context)

    # Schedule
    exercuter = Executor(context, mission)

    # -------------------------------------------------------------------------
    # Simulation
    # -------------------------------------------------------------------------

    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    while True:
        
        # User imput
        key = readKeyboard()

        if key == 'q': # Quit
            break
        elif key == 'd': # Debug mode (on/off)
            robot.setDebug( not robot.debug() )
        elif key == 'r': # Randomize worksapce
            randomize = True
        elif key == '1': # Change to mission 1
            plan = planMission1
            randomize = True
        elif key == '2': # Change to mission 2
            plan = planMission2
            randomize = True

        # Shuffle things around...
        if randomize:
            robot.reset()
            n = len(waypoints)
            waypoints = randomizeWaypints(xmin, xmax, ymin, ymax, n)
            waypoints_ployline.set(waypoints)
            mission = plan(waypoints, context)
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