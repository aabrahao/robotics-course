from dataclasses import dataclass
from enum import Enum, auto

from math import sin, cos
from numpy import clip as clamp

from eml4806.geometry.vector import Vector, toVector, toVectors, length, angle, unit, polar, dot, cross
from eml4806.geometry.angle import wrap, radians

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

class TeleopTask(Task):
    pass

###########################################################

class WaitTask(Task):

    def __init__(self, duration):
        super().__init__('Wait', f'duration: {duration}')
        self.duration = float(duration)
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
class MoveToTaskSettings:

    # Switch distance from "approach" robot_heading to final robot_heading
    heading_switch_radious = 3.0 # m 

    # Solution tolerance
    distance_tolerance = 0.05 # m (~1 inch), arrived?
    angle_tolerance = radians(10.0) # aligned?

    # Control gains (>0, k_beta < 0)
    k_rho   =  1.0  # k1 > 0
    k_alpha =  2.0  # k2 > 0
    k_beta  = -1.5  # k3 < 0

class MoveToTask(Task):

    '''Move to a desired pose'''

    def __init__(self, position, heading, settings=MoveToTaskSettings()):
        self.goal_position = Vector(position)
        self.goal_heading = wrap(heading)
        self.settings = settings
        super().__init__('MoveToTask', f'position: {self.goal_position}, heading: {self.goal_heading:.3f}]')

    def setup(self, context, dt):
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context, dt):
        # Alias
        robot = context.robot
        goal_position = self.goal_position
        goal_heading = self.goal_heading
        vmax = context.vmax
        wmax = context.wmax

        # Controller gains
        k_rho = self.settings.k_rho
        k_alpha = self.settings.k_alpha
        k_beta = self.settings.k_beta
        
        # Solution tollerances
        dtol = self.settings.distance_tolerance
        htol = self.settings.angle_tolerance

        # Final robot_heading approch
        hdist = self.settings.heading_switch_radious

        # World frame
        robot_position = robot.gps()
        robot_heading = robot.imu()
        target_position = goal_position - robot_position
        target_distance = length(target_position)

        # Heading selection
        if target_distance > hdist: 
            target_heading = angle(target_position) # Point towards goal
        else: 
            target_heading = goal_heading # Enforce final pose robot_heading
                        
        # Distance
        dx, dy = target_position

        # Error in robot frame rotation(robot_heading).T @ target_position
        ex =  cos(robot_heading)*dx + sin(robot_heading)*dy
        ey = -sin(robot_heading)*dx + cos(robot_heading)*dy
        
        eh = wrap(target_heading - robot_heading)
            
        # Check goal tolerance
        if (target_distance < dtol) and (abs(eh) < htol):
            v = 0.0
            w = 0.0
            return State.DONE

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
        v = clamp(v, 0.0, vmax)
        w = clamp(w, -wmax, wmax)

        # Update robot
        robot.move(v, w, dt)

###########################################################
@dataclass
class RotateToTaskSettings:

    # Solution tolerance
    angle_tolerance = radians(10.0) # aligned?

    # Control gains
    kp  = 1.0

class RotateToTask(Task):

    '''Rotate to a desired robot_heading'''

    def __init__(self, robot_heading, settings=RotateToTaskSettings()):
        self.robot_heading = wrap(robot_heading)
        self.settings = settings
        super().__init__('RotateToTask', f'robot_heading: [{robot_heading:.3f}]')

    def setup(self, context, dt):
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context, dt):
        # Alias
        robot = context.robot
        robot_heading = robot.imu()
        target_heading = self.robot_heading
        wmax = context.wmax

        # Controller gains
        kp = self.settings.kp
        
        # Solution tollerances
        htol = self.settings.angle_tolerance
        
        # World frame
        robot_heading = robot.imu()

        # Error
        error = target_heading - robot_heading
        error = wrap(error)
            
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

class HaltTask(Task):

    def __init__(self):
        super().__init__('HaltTask', 'v: 0.0, w: 0.0')

    def cleanup(self, context, dt):
        super().cleanup(context, dt)
        context.robot.move(0.0, 0.0, dt)

###########################################################

class BladeControlTask(Task):

    def __init__(self, state):
        self.state = state
        positions = ['off', 'low', 'high']
        super().__init__('BladeControlTask', f'{positions[state]}')
    
    def cleanup(self, context, dt):
        super().cleanup(context, dt)
        context.robot.setBlade(self.state)
