from dataclasses import dataclass
from enum import Enum, auto

from math import sin, cos
from numpy import clip as clamp

import eml4806.geometry.angle as angle
import eml4806.geometry.math as math
import eml4806.geometry.pose as pose

class State(Enum):
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()

###########################################################

class Task:

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
        self.state = State.READY

    def setup(self, context, dt):
        """Called once before the first run()."""
        print(f"[{self.name}] {self.arguments}")

    def run(self, context, dt):
        """Do one non-blocking step. Return new state."""
        return State.DONE

    def cleanup(self, context, dt):
        """Called once when DONE or FAILED."""
        print(f"[{self.name}] done!\n")

###########################################################

class Teleop(Task):
    pass

###########################################################

class Wait(Task):

    def __init__(self, duration):
        super().__init__('Wait', f'duration: {duration}')
        self.duration = duration
        self.elapsed = 0.0

    def setup(self, context, dt):
        super().setup(context, dt)
        self.elapsed = 0.0

    def run(self, context, dt):
        self.elapsed += dt
        print(f"\r[{self.name}] {self.elapsed:.2f}/{self.duration:.2f}", end='')
        if self.elapsed >= self.duration:
            print()
            return State.DONE
        return State.RUNNING

###########################################################

@dataclass
class GoToSettings:

    # Distance behaviour
    heading_switch_radious = 3.0 # m distance at which we switch from "approach" heading to final heading

    # Solution tolerance
    distance_tolerance = 0.05 # m (~1 inch), arrived?
    angle_tolerance = angle.radians(10.0) # aligned?

    # Control gains (>0, k_beta < 0)
    k_rho   =  1.0  # k1 > 0
    k_alpha =  2.0  # k2 > 0
    k_beta  = -1.5  # k3 < 0

class MoveTo(Task):

    '''Move to a desired pose'''

    def __init__(self, p, settings=GoToSettings()):
        self.goal = pose.ensureOne(p)
        self.settings = settings
        super().__init__('MoveTo', f'pose: [{p[0]:.2f}, {p[1]:.2f}, {p[2]:.3f}]')

    def setup(self, context, dt):
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context, dt):
        # Alias
        robot = context.robot
        goal = self.goal
        vmax = context.vmax
        wmax = context.wmax

        # Controller gains
        k_rho = self.settings.k_rho
        k_alpha = self.settings.k_alpha
        k_beta = self.settings.k_beta
        
        # Solution tollerances
        dtol = self.settings.distance_tolerance
        htol = self.settings.angle_tolerance

        # Final heading approch
        hdist = self.settings.heading_switch_radious

        # World frame
        position = robot.gps()
        heading = robot.imu()
        target = pose.position(goal) - position
        target_distance = math.length(target)

        # Heading selection
        if target_distance > hdist: 
            target_heading = math.angle(target) # Point towards goal
        else: 
            target_heading = pose.heading(goal) # Enforce final pose heading
                        
        # Robot frame: error = rotation(heading).T @ target
        dx, dy = target
        ex =  cos(heading)*dx + sin(heading)*dy
        ey = -sin(heading)*dx + cos(heading)*dy
        eh = angle.wrap(target_heading - heading)
            
        # Check goal tolerance
        if (target_distance < dtol) and (abs(eh) < htol):
                v = 0.0
                w = 0.0
                return State.DONE

        # Robot frame
        error = math.new(ex, ey)

        # Polar error coordinates
        rho = math.length(error)
        alpha = math.angle(error)
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
        v = clamp(v, 0.0, vmax)
        w = clamp(w, -wmax, wmax)

        # Update robot
        robot.move(v, w, dt)

###########################################################
@dataclass
class AlignSettings:

    # Solution tolerance
    angle_tolerance = angle.radians(10.0) # aligned?

    # Control gains
    kp  = 1.0

class RotateTo(Task):

    '''Rotate to a desired heading'''

    def __init__(self, heading, settings=AlignSettings()):
        self.heading = angle.wrap(heading)
        self.settings = settings
        super().__init__('RotateTo', f'heading: [{heading:.3f}]')

    def setup(self, context, dt):
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context, dt):
        # Alias
        robot = context.robot
        heading = robot.imu()
        target_heading = self.heading
        wmax = context.wmax

        # Controller gains
        kp = self.settings.kp
        
        # Solution tollerances
        htol = self.settings.angle_tolerance
        
        # World frame
        heading = robot.imu()

        # Error
        error = target_heading - heading
        error = angle.wrap(error)
            
        # Check goal tolerance
        if abs(error) < htol:
            w = 0.0
            return State.DONE

        # Control law
        v = 0.0
        w = kp * error
        
        # Saturation
        w = clamp(w, -wmax, wmax)

        # Update robot
        robot.move(v, w, dt)

###########################################################

class Halt(Task):
    def __init__(self):
        super().__init__('Halt', 'v: 0.0, w: 0.0')
    def cleanup(self, context, dt):
        super().cleanup(context, dt)
        context.robot.move(0.0, 0.0, dt)

###########################################################

class Blade(Task):
    def __init__(self, state):
        self.state = state
        positions = ['off', 'low', 'high']
        super().__init__('Blade', f'{positions[state]}')
    def cleanup(self, context, dt):
        super().cleanup(context, dt)
        context.robot.setBlade(self.state)
