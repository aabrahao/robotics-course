# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt

from enum import Enum

from numpy import sin, cos, pi
from numpy.random import uniform as random

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
    robot.setDebug(True)
    autonomous = True

    # Go pose
    goal = pose.new(6.0, 4.0, angle.radians(135.0))

    # Debug graphics
    # docking
    docking_point = shape.Point(world, pose.position(docking), style=style.brush('magenta'))
    # Robot
    position_point = shape.Point(world, pose.position(docking), style=style.brush('teal'))
    # Goal pose
    goal_point = shape.Point(world, pose.position(goal), style=style.brush('red'))
    goal_arrow = shape.Arrow(world, pose.position(goal), 0.8*pose.direction(goal), style=style.brush('red', 4))
    
    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    # Robot control variables
    v = 0.0  # Linear speed (m/s)
    w = 0.0  # Angular speed (m/s)

    # Controller saturation
    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = angle.radians(60.0) # rad/s
 
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
            robot.setDebug( not robot.debug() )
        elif key == 'r':
            goal = pose.new(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax), random(0.0, 2*pi))
            goal_point.set(pose.position(goal))
            goal_arrow.set(pose.position(goal), 0.8*pose.direction(goal))
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
        # Autonmous drive (Go-to-pose Controller)

        if autonomous: 
            
            # Distance behaviour
            heading_switch_radious = 3.0 # m distance at which we switch from "approach" heading to final heading
            posistion_tolerance = 0.02 # m (~1 inch), arrived?
            heading_tolerance = angle.radians(5.0) # aligned?

            # Control gains (>0, k_beta < 0)
            k_rho   =  1.0  # k1 > 0
            k_alpha =  2.0  # k2 > 0
            k_beta  = -1.5  # k3 < 0

            # World frame
            position = robot.gps()
            heading = robot.imu()
            target = pose.position(goal) - position
            target_distance = vector.length(target)

            # Heading selection
            if target_distance > heading_switch_radious: 
                target_heading = vector.angle(target) # Point towards goal
            else: 
                target_heading = pose.heading(goal) # Enforce final pose heading
                        
            # Robot frame: error = rotation(heading).T @ target
            dx, dy = target
            ex =  cos(heading)*dx + sin(heading)*dy
            ey = -sin(heading)*dx + cos(heading)*dy
            eh = angle.wrap(target_heading - heading)
            
            # Check goal tolerance
            if (target_distance < posistion_tolerance) and (abs(eh) < heading_tolerance):
                v = 0.0
                w = 0.0
            else:
                # Robot frame
                error = vector.new(ex, ey)

                # Polar error coordinates
                rho = vector.length(error)
                alpha = vector.angle(error)
                beta = angle.wrap( eh - alpha )

                # Lyapunov-based control law (saturated)
                v = k_rho*rho*cos(alpha)

                # Angular velocity
                if abs(alpha) < 1e-6:
                    C = 1.0  # limit of sin(alpha)*cos(alpha)/alpha as alpha -> 0
                else:
                    C = (sin(alpha)*cos(alpha))/alpha

                w = k_alpha*alpha + k_rho*C*(alpha + k_beta*beta)

                # Saturation
                v = np.clip(v, 0.0, vmax)
                w = np.clip(w, -wmax, wmax)
  
        # Actuator
        robot.move(v, w, dt)  # Actuator
        
        # Advance
        t += dt
            
        # Update scene
        world.update()
    
    print("Bye!")

if __name__ == "__main__":
    main()