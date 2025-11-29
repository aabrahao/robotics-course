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
import eml4806.graphics.style as style

import eml4806.robot.skidsteer as lawnmower
import eml4806.robot.tool as tool
import eml4806.robot.odometry as odometry

import eml4806.task.task as task
import eml4806.task.executor as executer
import eml4806.task.context as context

def main():

    menu = '''Keyboard commands
    [r] Randomize
    [d] Debug on/off
    [q] Quit'''

    ############################################################################################################
    # World
     
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = worksapce.Workspace(xmin, xmax, ymin, ymax, menu)
    
    ############################################################################################################
    # Robot docking station
    
    docking = pose.new(0.0, 0.0, angle.radians(10.0))

    ############################################################################################################
    # Robot physics

    # ClearPath Husky A200 Ground Platform
    # https://docs.clearpathrobotics.com/docs_robots/outdoor_robots/husky/a200/user_manual_husky/

    chassis = lawnmower.Chassis()
    chassis.length = 0.812  # m
    chassis.width = 0.421  # m
    chassis.wheelbase = 0.512  # m
    chassis.trackwidth = 0.550  # m

    wheels = lawnmower.Wheel()
    wheels.diameter = 0.330  # m
    wheels.width = 0.114  # m

    motors = lawnmower.Motor()
    motors.maximum_angular_velocity = 5.45  # rad/s (~52 rpm maximum)
    
    blade = tool.Blade()
    blade.diameter = 0.9 * chassis.width  # m

    odometer = odometry.AnalyticalSkidDriveOdometer()
    odometer.track_width = chassis.trackwidth
    odometer.maximum_linear_velocity = None # 1.0  # m/s
    odometer.maximum_angular_velocity = None # 3.5  # rad/s

    ############################################################################################################
    # Robot
    
    robot = lawnmower.Robot(world, pose.position(docking), pose.heading(docking), chassis, wheels, motors, blade, odometer)

    ############################################################################################################
    # Settings

    robot.setDebug(True)
    autonomous = True

    docking_rectangle = shape.Rectangle(world, pose.position(docking), chassis.length, chassis.width, angle=pose.heading(docking), style=style.brush('gray'))
    docking_point = shape.Point(world, pose.position(docking), style=style.brush('magenta'))
    
    ############################################################################################################
    # Simulation

    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    ############################################################################################################
    # Controls
    
    v = 0.0  # Left track linear velocity (m/s)
    w = 0.0  # Left track linear velocity (m/s)

    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = angle.radians(60.0) # rad/s
    
    ############################################################################################################
    # Missions
    
    waypoints = vector.ensure([
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [8.0, 4.0]
    ])

    # Graphics
    waypoints_ployline = shape.Polyline(world, waypoints, style=style.pen('gray', 2), marker='o')

    # Mission Planner 1
    def planMission1(points):

        n = len(points)
        if n < 2:
            return []
        
        tasks = []
        for i in range(n):
            if i == n-1: # Last point
                h = vector.angle(points[i] - points[i-1])
            else: # All others
                h = vector.angle(points[i+1] - points[i]) 
            p = pose.set(points[i], h)
            tasks.append( task.MoveTo(p) )
            # Turn blade on/off
            if i % 2 == 0:
                tasks.append( task.Blade(tool.State.LOW) )
            else:
                tasks.append( task.Blade(tool.State.OFF) )
        # Dock
        tasks.append( task.MoveTo(docking + (0,0,pi)) )
        tasks.append( task.Halt() )
        return tasks
    
    # Mission Planner 2
    def planMission2(points):

        n = len(points)
        if n < 2:
            return []

        tasks = []
        for i in range(n):
            if i == 0: # First
                h = vector.angle(points[i+1] - points[i])
                p = pose.set(points[i], h)
                tasks.append( task.MoveTo(p) )
            elif i == n-1: # Last
                h = vector.angle(points[i] - points[i-1])
                p = pose.set(points[i], h)
                tasks.append( task.MoveTo(p) )
                tasks.append( task.MoveTo(docking + (0,0,pi)) )
            else: # All others
                h = vector.angle(points[i] - points[i-1]) 
                p = pose.set(points[i], h)
                tasks.append( task.MoveTo(p) )
                h = vector.angle( points[i+1] - points[i] )
                tasks.append( task.RotateTo( h ) )
        tasks.append( task.Halt() )   
        return tasks

    plan = planMission1
    mission = plan(waypoints)
    

    ############################################################################################################
    # Mission context

    enviroment = context.Context()
    enviroment.robot = robot
    enviroment.vmax = vmax
    enviroment.wmax = wmax
    
    ############################################################################################################
    # Task executer

    scheduler = executer.Executor(enviroment, mission)

    while True:

        # Controller
        key = keyboard.key()
        if key == 'q': 
            break
        elif key == 'd': 
            robot.setDebug( not robot.debug() )
        elif key == '1':
            plan = planMission1
        elif key == '2':
            plan = planMission2
        elif key == 'r':
            robot.reset()
            n = len(waypoints)
            waypoints = vector.new(random(xmin, xmax, n), random(ymin, ymax, n))
            waypoints_ployline.set(waypoints)
            mission = plan(waypoints)
            scheduler.set(mission)

        # Mission
        scheduler.run(dt)

        # Simulation
        world.update()
        t += dt
    
    print('Bye!')

if __name__ == '__main__':
    main()