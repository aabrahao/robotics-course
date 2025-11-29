# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt

from numpy.random import uniform as random
from numpy import pi

from enum import Enum

import eml4806.sensor.keyboard as keyboard

import eml4806.geometry.angle as angle
import eml4806.geometry.line as line
import eml4806.geometry.vector as vector
import eml4806.geometry.transform as transform
import eml4806.geometry.pose as pose

import eml4806.graphics.workspace as worksapce
import eml4806.graphics.shape as shape
import eml4806.graphics.style as style

import eml4806.robot.skidsteer as lawnmower
import eml4806.robot.odometry as odometry
import eml4806.robot.tool as tool

def info():
    print("=== Menu ===")
    print("a : autonomous drive (on/off)")
    print("r : randomize")
    print("d : debug (on/off)")
    print("q : quit")
    print()

def main():

    info()
   
    # Land
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = worksapce.Workspace(xmin, xmax, ymin, ymax)

    # Robot docking station
    docking = pose.new(0.0, 0.0, angle.radians(10.0))

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

    # Simulated robot
    robot = lawnmower.Robot(world, pose.position(docking), pose.heading(docking), chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.setDebug(False)
    autonomous = False

    # Track line
    line_start = vector.new(2.0, 4.0)
    line_end = vector.new(8.0, 8.5)
    
    # Debug graphics

    # docking
    docking_point = shape.Point(world, pose.position(docking), style=style.brush('magenta'))
            
    # Pursuit line
    track_line = shape.Ray(world, line_start, line_end, style=style.pen('black', 1))
    track_arrow = shape.Arrow(world, line_start, line_end-line_start, style=style.brush('red', 4))
    
    # Debug
    position_point = shape.Point(world, pose.position(docking), style=style.brush('teal'))
    goal_point = shape.Point(world, (0.0, 0.0), style=style.brush('teal'))
    distance_line = shape.Line(world, (0.0, 0.0), (0.0, 0.0), style=style.pen('teal'))
    if not robot.debug():
        position_point.hide()
        goal_point.hide()
        distance_line.hide()
    
    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    # Robot control variables
    v = 0.0  # Left track linear velocity (m/s)
    w = 0.0  # Left track linear velocity (m/s)

    # Controller saturation
    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = angle.radians(60.0) # rad/s
   
    # PID Controller
    error_integral = 0.0        
    error_previous = 0.0
 
    while True:

        #######################################################################
        # Controller
    
        key = keyboard.key()

        # Commands inside the microntroller
        if key == 'q':
            break
        elif key == 'a':
            autonomous = not autonomous
            v = 0.0
            w = 0.0
        elif key == 'd':
            if robot.debug():
                robot.setDebug( False )
                position_point.hide()
                goal_point.hide()
                distance_line.hide()
            else:
                robot.setDebug( True )
                position_point.show()
                goal_point.show()
                distance_line.show()
        elif key == 'r':
            line_start = vector.new(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            line_end   = vector.new(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            track_arrow.set(line_start, line_end-line_start)
            track_line.set(line_start, line_end)
            v = 0.0
            w = 0.0

        #######################################################################
        # Manual drive

        if not autonomous:
     
            # Controller sensitivity
            dv = 0.07  # m/s, Linear velocity increase
            dw = 0.04  # m/s, Angular velocity increse 
     
            # Joytick controls
            if key == "up":
                v += dv
                w = 0.0
            elif key == "down":
                v -= dv
                w = 0.0
            elif key == "left":
                w += dw
            elif key == "right":
                w -= dw
            elif key == " ":
                v = 0.0
                w = 0.0
            
            # Motors physical limits
            v = np.clip(v, -vmax, vmax)
            w = np.clip(w, -wmax, wmax)

        #######################################################################
        # Autonmous drive (Line pursit)

        if autonomous: 
            
            # Chassis geometry
            l = chassis.trackwidth

            # PID controller: cross track + heading control
            kp = 2.0
            ki = 0.00
            kd = 0.00

            # Cross-track distance weight in heading correction
            kc = 1.0 # rad/m 
        
            # Sensors
            position = robot.gps()
            heading = robot.imu()

            # Cross-track error: signed distance from robot to the desired shape.Line
            goal = line.closest(line_start, line_end, position)
            error_distance = vector.length(goal - position)
            
            # Cross-track error signal
            if vector.cross(goal - position, line_end - line_start) > 0.0:
                error_distance = -error_distance

            # Heading error: difference between desired heading and robot heading
            line_heading = vector.angle(line_end - line_start)
            error_heading = angle.wrap(line_heading - heading)

            # Angular velocity PID controller
            error = kc*error_distance + error_heading
            error_integral += error*dt        
            error_derivative = (error - error_previous)/dt
            error_previous = error_previous

            # Angular corrections
            w = kp*error + ki*error_integral + kd*error_derivative 
            
            # Keep robot moving forward if far from line
            if abs(error_distance) > 2.0:
                v = 1.0*vmax
            else:
                v = 0.8*vmax

            # Motors physical limits
            v = np.clip(v, -vmax, vmax)
            w = np.clip(w, -wmax, wmax)

            # Updated Graphics
            position_point.move(position)
            goal_point.move(goal)
            distance_line.set(position, goal)
            
        # Actuator
        robot.move(v, w, dt)  # Actuator
        
        # Advance
        t += dt
            
        # Update scene
        world.update()
    
    print("Bye!")

if __name__ == "__main__":
    main()
