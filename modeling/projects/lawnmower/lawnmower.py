# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt
import random as rnd

from enum import Enum

import eml4806.sensor.keyboard as keyboard

import eml4806.geometry.angle as angle
import eml4806.geometry.line as line
import eml4806.geometry.vector as vector
import eml4806.geometry.transform as transform

import eml4806.graphics.workspace as worksapce
import eml4806.graphics.shape as shape
import eml4806.graphics.style as style

import eml4806.robot.skidsteer as lawnmower
import eml4806.robot.odometry as odometry

def rand(start, end):
    return rnd.uniform(start, end)

def main():
   
    # Land
    xmin = -2.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    world = worksapce.Workspace(xmin, xmax, ymin, ymax)

    # Robot docking station
    docking_location = vector.vector(0.0, 0.0)
    docking_orientation = np.pi/36

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
    
    blade = lawnmower.Blade()
    blade.diameter = 0.9 * chassis.width  # m
    blade.height = 0.05  # m (~2 inches)

    odometer = odometry.AnalyticalSkidDriveOdometer()
    odometer.track_width = chassis.trackwidth
    odometer.maximum_linear_velocity = None # 1.0  # m/s
    odometer.maximum_angular_velocity = None # 3.5  # rad/s

    # Simulated robot
    robot = lawnmower.Robot(world, docking_location, docking_orientation, chassis, wheels, motors, blade, odometer)

    # Settings    
    robot.setDebug(True)

    ''''
    class Mode(Enum):
        remote_control = 0
        go_to_point = 1
        follow_line = 2
        dock = 3
        stop = 4
    
    mode = Mode.remote_control
    '''

    autonomous = False

    # Track line
    line_start = vector.vector(2.0, 4.0)
    line_end = vector.vector(8.0, 8.5)
    
    # Debug graphics

    # docking
    docking_point = shape.Point(world, docking_location, style=style.brush('magenta'))
    
    # Robot
    position_point = shape.Point(world, docking_location, style=style.brush('teal'))
    
    # shape.Line
    track_line = shape.Line(world, line_start, line_end, style=style.pen('red', 3))
    track_ray = shape.Ray(world, line_start, line_end, style=style.pen('gray', 1))
    track_start_point = shape.Point(world, line_start, style=style.pen('blue'))
    track_end_point = shape.Point(world, line_end, style=style.pen('green'))
    
    # PID controller
    goal_point = shape.Point(world, (0.0, 0.0), style=style.brush('teal'))
    distance_line = shape.Line(world, (0.0, 0.0), (0.0, 0.0), style=style.pen('teal'))
    
    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)

    # Robot control variables
    vl = 0.0  # Left track linear velocity (m/s)
    vr = 0.0  # Left track linear velocity (m/s)
    vmax = motors.maximum_angular_velocity*(0.5* wheels.diameter)
   
    # PID
    error_integral = 0.0        
    error_previous = 0.0
 
    while True:

        # User controller
        key = keyboard.key()

        # Commands inside the microntroller
        if key == 'q':
            break
        elif key == 'a':
            autonomous = not autonomous
            vl = 0.0
            vr = 0.0
        elif key == 'l':
            line_start = vector.vector( rand(xmin, xmax), rand(ymin, ymax) )
            line_end   = vector.vector( rand(xmin, xmax), rand(ymin, ymax) )
            track_line.set(line_start, line_end)
            track_ray.set(line_start, line_end)
            track_start_point.move(line_start)
            track_end_point.move(line_end)
            vl = 0.0
            vr = 0.0

        # Operation mode
        if not autonomous:
     
            # Controller sensitivity
            dv = 0.07  # m/s, Linear velocity increase
            dw = 0.04  # m/s, Angular velocity increse 
     
            # Joytick controls
            if key == "up":
                vl += dv
                vr += dv
            elif key == "down":
                vl -= dv
                vr -= dv
            elif key == "left":
                vl -= dw
                vr += dw
            elif key == "right":
                vl += dw
                vr -= dw
            elif key == " ":
                vl = 0.0
                vr = 0.0
            elif key == "d":
                robot.setDebug( not robot.debug() )
        
        else: # Autonmous drive in line pursuit mode
            
            # Chassis geometry
            l = chassis.wheelbase

            # PID controller: cross track + heading control
            kp = 2.0
            ki = 0.00
            kd = 0.00

            # Cross-track distance weight in heading correction
            kc = 1.0 # rad/m 
        
            # Sensors
            position = robot.gps()
            heading = robot.imu()
        
            # Heading error: difference between desired heading and robot heading
            line_heading = vector.angle(line_end - line_start)
            error_heading = angle.wrap(line_heading - heading)

            # Cross-track error: signed distance from robot to the desired shape.Line
            goal = line.closest(line_start, line_end, position)
            error_distance = vector.length(goal - position)
            
            # Cross-track error signal
            if vector.cross(goal - position, line_end - line_start) > 0.0:
                error_distance = -error_distance

            # PID
            error = kc*error_distance + error_heading
            error_integral += error*dt        
            error_derivative = (error - error_previous)/dt
            error_previous = error_previous

            # Angular corrections
            w = kp*error + ki*error_integral + kd*error_derivative 

            # Handle large distances
            w = np.clip(w, -1.0, 1.0) # Limit rotation

            # Keep robot moving forward if far from line
            if abs(error_distance) > 0.25:
                v = 1.0*vmax
            else:
                v = 0.8*vmax

            # Wheel velocities            
            vl = v - 0.5*l*w
            vr = v + 0.5*l*w

            # Display controller results
            print(f'e: {error} ei: {error_integral} ed: {error_derivative} -> vl: {vl} vr: {vr}')

            # Updated Graphics
            if robot.debug():
                position_point.move(position)
                goal_point.move(goal)
                distance_line.set(position, goal)
        

        # Motors physical limits
        vl = np.clip(vl, -vmax, vmax)
        vr = np.clip(vr, -vmax, vmax)

        # Actuator
        robot.move(vl, vr, dt)  # Actuator
        
        # Advance
        t += dt
            
        # Update scene
        world.update()
    
    print("Bye!")

if __name__ == "__main__":
    main()
