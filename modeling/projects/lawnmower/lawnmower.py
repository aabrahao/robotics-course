# Simulate a particle moving around a circle.
# Lawn mower robot
# https://youtu.be/2Rhsv8fFqCE

import numpy as np
import matplotlib.pyplot as plt

import eml4806.geometry.angle as angle

import eml4806.sensor.keyboard as keyboard

from eml4806.geometry.line import closest
from eml4806.geometry.vector import vector
from eml4806.graphics.workspace import Workspace
from eml4806.graphics.shape import Rectangle, Circle, Polyline, Group, Arrow
from eml4806.graphics.style import Style, pen, brush 
from eml4806.geometry.transform import Transform
from eml4806.robot.odometry import AnalyticalSkidDriveOdometer
from eml4806.robot.skidsteer import Chassis, Wheel, Motor, Blade, Robot

def main():

    # Land
    xmin = -1.0
    xmax = 10.0
    ymin = -1.0
    ymax = 10.0

    workspace = Workspace(xmin, xmax, ymin, ymax)

    # Robot docking station
    x0 = 0.0  # m
    y0 = 0.0  # m
    theta0 = np.deg2rad(10.0)  # rad

    dock = Circle(workspace, x0, y0, 0.1, style=brush('magenta'))

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
    blade.height = 0.05  # m (~2 inches)

    odometer = AnalyticalSkidDriveOdometer()
    odometer.track_width = chassis.trackwidth
    odometer.maximum_linear_velocity = 1.0  # m/s
    odometer.maximum_angular_velocity = 3.5  # rad/s

    # Simulated robot
    robot = Robot(workspace, x0, y0, theta0, chassis, wheels, motors, blade, odometer)
    robot.setDebug(True)

    # Direct wheel-speed control modeling a microcontroller-style PWM motor driver
    # v = omega*r_wheel
    vl = 0.0  # Left track linear velocity (m/s)
    vr = 0.0  # Left track linear velocity (m/s)
    vmax = motors.maximum_angular_velocity * (0.5* wheels.diameter)

    # Controller sensitivity
    dv = 0.07  # m/s, Linear velocity increase
    dw = 0.04  # m/s, Angular velocity increse 

    # PID Controller
    kp = 1.00
    ki = 0.00
    kd = 0.00
    
    # Error
    e = 0.0
    e_integral = 0.0    
    e_previous = 0.0

    # Line to follow
    x1 = 2.0
    y1 = 4.0
    x2 = 8.0
    y2 = 8.5
    
    line = Polyline(workspace, style=pen('red', 3))
    line.append((x1, y1))
    line.append((x2, y2))

    # Line pursuit point
    xl = 0.0
    yl = 0.0
    follower = Circle(workspace, xl, yl, 0.05, style=brush('teal'))

    # Simulation
    t = 0.0 # s
    dt = 0.02 # s (~50 Hz)
    
    while True:

        # User controller
        key = keyboard.key()

        # Commands inside the microntroller
        if key == "q":
            break
        elif key == "up":
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
            robot.setDebug( robot.debug() )
          
        # Motors physical limits
        vl = np.clip(vl, -vmax, vmax)
        vr = np.clip(vr, -vmax, vmax)

        ###################################################################################
        # Controller

        # Sensor
        x, y = robot.gps()

        # Controller
        
        # Point in line closest to the robot
        xl,  yl = closest(x, y, x1, y1, x2, y2)
        follower.move(xl, yl)



        # Actuator
        robot.move(vl, vr, dt)  # Actuator

        # Advance
        t += dt
    
        ###################################################################################

        # Update scene
        workspace.update()

    
    print("Bye!")

if __name__ == "__main__":
    main()
