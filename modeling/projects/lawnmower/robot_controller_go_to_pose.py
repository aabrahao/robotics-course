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
import numpy as np
import matplotlib.pyplot as plt

from enum import Enum

from numpy import sin, cos, pi
from numpy.random import uniform as random

from eml4806.sensor.keyboard import key as readKeyboard

from eml4806.graphics.workspace import Workspace

from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

from eml4806.geometry.vector import Vector, length, angle, unit, polar
from eml4806.geometry.angle import radians, wrap

def main():

    menu = ['Commands:',
            '[r] Randomize',
            '[b] Blade (off/low/high)',
            '[d] Debug on/off',
            '[q] Quit']

    # Land
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin), menu)

    # Robot dock pose
    dock_position = Vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # Robot physics
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

    # Simulated robot
    robot = Robot(world, dock_position, dock_heading, chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.setDebug(True)
    autonomous = True

    # Goal pose
    goal_position = Vector(6.0, 4.0)
    goal_heading = radians(135.0)

    # Graphics
    dock_point  = world.point(center=dock_position, color='magenta')
    goal_point  = world.point(center=goal_position, color='red')
    goal_arrow  = world.arrow(origin=goal_position, direction=0.8*polar(1.0,goal_heading), color='red', width=4)
    
    # Robot control variables
    v = 0.0  # Linear speed (m/s)
    w = 0.0  # Angular speed (rad/s)

    # Controller saturation
    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = radians(60.0) # rad/s

    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)
 
    while True:
    
        key = readKeyboard()

        if key == 'q':
            break
        elif key == 'a':
            autonomous = not autonomous
            v = 0.0
            w = 0.0
        elif key == 'b':
            robot.toggleBladeState()
        elif key == 'd':
            robot.setDebug( not robot.debug() )
        elif key == 'r':
            goal_position = Vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            goal_heading = random(0.0, 2*pi)
            goal_point.set(center=goal_position)
            goal_arrow.set(origin=goal_position, direction=0.8*polar(1.0,goal_heading))
            v = 0.0
            w = 0.0

        # ---------------------------------------------------------------------------
        # Manual drive
        # ---------------------------------------------------------------------------

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

        # ---------------------------------------------------------------------------
        # Autonmous drive (Go-to-pose Controller)
        # ---------------------------------------------------------------------------

        if autonomous: 
            
            # Distance behaviour
            heading_switch_radious = 3.0 # m distance at which we switch from "approach" heading to final heading
            posistion_tolerance = 0.02 # m (~1 inch), arrived?
            heading_tolerance = radians(5.0) # aligned?

            # Control gains (>0, k_beta < 0)
            k_rho   =  1.0  # k1 > 0
            k_alpha =  2.0  # k2 > 0
            k_beta  = -1.5  # k3 < 0

            # Robot pose
            position = robot.gps()
            heading = robot.imu()

            # Target pose
            target_postion = goal_position - position
            target_distance = length(target_postion)

            # Heading selection
            if target_distance > heading_switch_radious: 
                target_heading = angle(target_postion) # Point towards goal_position
            else: 
                target_heading = goal_heading # Enforce final pose heading
                        
            # Robot frame
            dx, dy = target_postion

            # Error in robot frame = Rotation (heading).T @ target_postion
            ex =  cos(heading)*dx + sin(heading)*dy
            ey = -sin(heading)*dx + cos(heading)*dy
            
            eh = wrap(target_heading - heading)
            
            # Check goal_position tolerance
            if target_distance < posistion_tolerance and abs(eh) < heading_tolerance:
                v = 0.0
                w = 0.0
            else:
                # Robot frame
                error = Vector(ex, ey)

                # Polar error coordinates
                rho = length(error)
                alpha = angle(error)
                beta = wrap( eh - alpha )

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