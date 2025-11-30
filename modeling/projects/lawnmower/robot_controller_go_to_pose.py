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

    menu = '''Keyboard commands
    [a] Autonomous
    [r] Randomize
    [d] Debug on/off
    [q] Quit'''

    # Land
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = Workspace(xmin, ymin, xmin + (xmax-xmin), ymin + (ymax-ymin), menu)

    # Robot dock station
    dock = Vector(0.0, 0.0)
    docking_heading = radians(10.0)

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
    robot = Robot(world, dock, docking_heading, chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.setDebug(True)
    autonomous = True

    # Go pose
    goal = Vector(6.0, 4.0)
    goal_heading = radians(135.0)

    # Graphics
    
    docking_point = world.point(dock, 'magenta')
    robot_point = world.point(dock, 'teal')
    goal_point = world.point(goal, 'red')
    goal_arrow = world.arrow(goal, 0.8*polar(1.0,goal_heading), 'red', width=4)
    
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
        elif key == 'd':
            robot.setDebug( not robot.debug() )
        elif key == 'r':
            goal = Vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            goal_heading = random(0.0, 2*pi)
            goal_point.set(goal)
            goal_arrow.set(goal, 0.8*polar(1.0,goal_heading))
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

            # World frame
            position = robot.gps()
            heading = robot.imu()
            target = goal - position
            target_distance = length(target)

            # Heading selection
            if target_distance > heading_switch_radious: 
                target_heading = angle(target) # Point towards goal
            else: 
                target_heading = goal_heading # Enforce final pose heading
                        
            # Robot frame: error = rotation(heading).T @ target
            dx, dy = target
            ex =  cos(heading)*dx + sin(heading)*dy
            ey = -sin(heading)*dx + cos(heading)*dy
            eh = wrap(target_heading - heading)
            
            # Check goal tolerance
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