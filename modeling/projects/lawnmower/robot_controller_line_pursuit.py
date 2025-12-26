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

from eml4806.sensor.keyboard import key as read_heyboard

from eml4806.graphics.workspace import Workspace

from eml4806.robot.skidsteer import Robot, Chassis, Wheel, Motor 
from eml4806.robot.tool import Blade
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer

from eml4806.geometry.vector import vector, angle, unit, polar, dot, cross2d, norm
from eml4806.geometry.angle import radians, wrap
from eml4806.geometry.line import Line

def main():

    menu = ['Commands:',
            '[a] Autonomous (on/off)',
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

    # Robot dock_postion station
    dock_postion = vector(0.0, 0.0)
    dock_heading = radians(10.0)

    # Robot physics
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

    # Simulated robot
    robot = Robot(world, dock_postion, dock_heading, chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.set_debug(False)
    autonomous = False

    # Track line
    line = Line(start=(2.0, 4.0), end=(8.0, 8.5))
    
    # Graphics
    dock_point  = world.point(center=dock_postion, color='magenta')
    track_line  = world.ray(start=line.start, end=line.end, color='black')
    track_arrow = world.arrow(origin=line.start, direction=(line.end - line.start), color='red', width = 4)
    
    # Debug algorithm
    goal_point    = world.point(center=(0.0, 0.0), color='teal')
    distance_line = world.line(start=(0.0, 0.0), end=(0.0, 0.0), color='teal')
    
    if not robot.debug():
        goal_point.hide()
        distance_line.hide()
        
    # Control variables
    v = 0.0  # Linear speed (m/s)
    w = 0.0  # Angular speed (rad/s)

    # Controller saturation
    vmax = motors.maximum_angular_velocity*(0.5*wheels.diameter)
    wmax = radians(60.0) # rad/s
   
    # PID Controller
    error_integral = 0.0        
    error_previous = 0.0
 
    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    while True:
            
        key = read_heyboard()

        # Commands inside the microntroller
        if key == 'q':
            break
        elif key == 'a':
            autonomous = not autonomous
            v = 0.0
            w = 0.0
        elif key == 'b':
            robot.toggleBladeState()
        elif key == 'd':
            if robot.debug():
                robot.set_debug(False)
                goal_point.hide()
                distance_line.hide()
            else:
                robot.set_debug(True)
                goal_point.show()
                distance_line.show()
        elif key == 'r':
            line.start = vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            line.end = vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            track_arrow.set(origin=line.start, direction=(line.end - line.start))
            track_line.set(start=line.start, end=line.end)
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

            # PID controller: cross-track + robot_heading control
            kp = 2.0
            ki = 0.00
            kd = 0.00

            # Cross-track distance weight in robot_heading correction
            kc = 1.0 # rad/m 
        
            # Robot sensors
            robot_postion = robot.gps()
            robot_heading = robot.imu()

            # Cross-track error: signed distance from robot to the desired shape.Line
            goal_postion = line.closest(robot_postion)
            error_distance = norm(goal_postion - robot_postion)
            
            # Cross-track error signal
            if cross2d(goal_postion - robot_postion, line.end - line.start) > 0.0:
                error_distance = -error_distance

            # robot_heading error: difference between desired robot_heading and robot robot_heading
            line_heading = angle(line.end - line.start)
            error_heading = wrap(line_heading - robot_heading)

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
            goal_point.move(goal_postion)
            distance_line.set(robot_postion, goal_postion)
            
        # Actuator
        robot.move(v, w, dt)  # Actuator
        
        # Advance
        t += dt
            
        # Update scene
        world.update()
    
    print("Bye!")

if __name__ == "__main__":
    main()
