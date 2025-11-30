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

from eml4806.geometry.vector import Vector, length, angle, unit, polar, dot, cross
from eml4806.geometry.angle import radians, wrap
from eml4806.geometry.line import Line

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
    robot = Robot(world, dock, dock_heading, chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.setDebug(False)
    autonomous = False

    # Track line
    line = Line((2.0, 4.0), (8.0, 8.5))
    
    # Graphics
    dock_point = world.point(dock, 'magenta')
    track_line = world.ray(line.p1, line.p2, 'black')
    track_arrow = world.arrow(line.p1, line.p2 - line.p1, 'red', width = 4)
    
    # Debug algorithm
    robot_point = world.point(dock, 'teal')
    goal_point = world.point((0.0, 0.0), 'teal')
    distance_line = world.line((0.0, 0.0), (0.0, 0.0), 'teal')
    
    if not robot.debug():
        robot_point.hide()
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
            
        key = readKeyboard()

        # Commands inside the microntroller
        if key == 'q':
            break
        elif key == 'a':
            autonomous = not autonomous
            v = 0.0
            w = 0.0
        elif key == 'd':
            if robot.debug():
                robot.setDebug(False)
                robot_point.hide()
                goal_point.hide()
                distance_line.hide()
            else:
                robot.setDebug(True)
                robot_point.show()
                goal_point.show()
                distance_line.show()
        elif key == 'r':
            line.p1 = Vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            line.p2 = Vector(random(1.1*xmin, 0.9*xmax), random(1.1*ymin, 0.9*ymax))
            track_arrow.set(line.p1, line.p2 - line.p1)
            track_line.set(line.p1, line.p2)
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
            goal = line.closest(position)
            error_distance = length(goal - position)
            
            # Cross-track error signal
            if cross(goal - position, line.p2 - line.p1) > 0.0:
                error_distance = -error_distance

            # Heading error: difference between desired heading and robot heading
            line_heading = angle(line.p2 - line.p1)
            error_heading = wrap(line_heading - heading)

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
            robot_point.move(position)
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
