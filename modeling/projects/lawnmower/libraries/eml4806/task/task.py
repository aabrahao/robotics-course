from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from math import sin, cos
from typing import Any, Optional

from numpy import clip as clamp

from eml4806.geometry.vector import vector, norm, angle
from eml4806.geometry.angle import wrap, radians


class TaskState(Enum):
    READY = auto()
    RUNNING = auto()
    DONE = auto()
    FAILED = auto()


###########################################################

class AbstractTask:

    def __init__(self, name: str, arguments: str) -> None:
        self.name: str = name
        self.arguments: str = arguments
        self.state: TaskState = TaskState.READY

    def setup(self, context: Any, dt: float) -> None:
        """Called once before the first run()."""
        print(f"[{self.name}] {self.arguments}")

    def run(self, context: Any, dt: float) -> TaskState:
        """Do one non-blocking step. Return new state."""
        return TaskState.DONE

    def cleanup(self, context: Any, dt: float) -> None:
        """Called once when DONE or FAILED."""
        print(f"[{self.name}] done!\n")


###########################################################

class TeleopTask(AbstractTask):
    """Placeholder for teleoperation task logic."""
    pass


###########################################################

class WaitTask(AbstractTask):

    def __init__(self, duration: float) -> None:
        duration = float(duration)
        super().__init__("Wait", f"duration: {duration}")
        self.duration: float = duration
        self.elapsed: float = 0.0

    def setup(self, context: Any, dt: float) -> None:
        super().setup(context, dt)
        self.elapsed = 0.0

    def run(self, context: Any, dt: float) -> TaskState:
        self.elapsed += dt
        print(f"\r[{self.name}] {self.elapsed:.2f}/{self.duration:.2f}", end="")

        if self.elapsed >= self.duration:
            print()
            return TaskState.DONE

        return TaskState.RUNNING


###########################################################

@dataclass
class MoveToTaskSettings:

    heading_switch_radius: float = 3.0   # m
    distance_tolerance: float = 0.05     # m
    angle_tolerance: float = radians(10.0)
    k_rho: float = 1.0
    k_alpha: float = 2.0
    k_beta: float = -1.5


class MoveToTask(AbstractTask):

    """Move to a desired pose (position + heading)."""

    def __init__(self, position: vector, heading: float, settings=MoveToTaskSettings()) -> None:
        goal_position = vector(position)
        goal_heading = wrap(heading)
        super().__init__("MoveToTask", f"position: {goal_position}, heading: {goal_heading:.3f}")
        self.goal_position = goal_position
        self.goal_heading = goal_heading
        self.settings = settings

    def setup(self, context: Any, dt: float) -> None:
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context: Any, dt: float) -> TaskState:
        robot = context.robot
        goal_position = self.goal_position
        goal_heading = self.goal_heading
        vmax = context.v_max
        wmax = context.w_max

        k_rho = self.settings.k_rho
        k_alpha = self.settings.k_alpha
        k_beta = self.settings.k_beta

        dtol = self.settings.distance_tolerance
        htol = self.settings.angle_tolerance
        hdist = self.settings.heading_switch_radius

        robot_position = robot.gps()
        robot_heading = robot.imu()

        target_position = goal_position - robot_position
        target_distance = norm(target_position)

        # Heading selection
        if target_distance > hdist:
            target_heading = angle(target_position)
        else:
            target_heading = goal_heading

        dx, dy, _ = target_position

        # Robot-frame error
        ex = cos(robot_heading) * dx + sin(robot_heading) * dy
        ey = -sin(robot_heading) * dx + cos(robot_heading) * dy

        eh = wrap(target_heading - robot_heading)

        # Check goal tolerance
        if (target_distance < dtol) and (abs(eh) < htol):
            robot.move(0.0, 0.0, dt)
            return TaskState.DONE

        error_vec = vector(ex, ey)
        rho = norm(error_vec)
        alpha = angle(error_vec)
        beta = wrap(eh - alpha)

        # Lyapunov-based control
        v = k_rho * rho * cos(alpha)

        if abs(alpha) < 1e-6:
            C = 1.0
        else:
            C = (sin(alpha) * cos(alpha)) / alpha

        w = k_alpha * alpha + k_rho * C * (alpha + k_beta * beta)

        # Saturation
        v = float(clamp(v, 0.0, vmax))
        w = float(clamp(w, -wmax, wmax))

        robot.move(v, w, dt)

        return TaskState.RUNNING


###########################################################

@dataclass
class RotateToTaskSettings:

    angle_tolerance: float = radians(10.0)
    kp: float = 1.0

class RotateToTask(AbstractTask):

    """Rotate to a desired heading."""

    def __init__(self, heading: float, settings = RotateToTaskSettings() ) -> None:
        desired_heading = wrap(heading)
        super().__init__("RotateToTask", f"heading: {desired_heading:.3f}")
        self.heading = desired_heading
        self.settings = settings

    def setup(self, context: Any, dt: float) -> None:
        super().setup(context, dt)
        context.robot.move(0.0, 0.0, dt)

    def run(self, context: Any, dt: float) -> TaskState:
        robot = context.robot
        target_heading = self.heading
        wmax = context.w_max

        kp = self.settings.kp
        htol = self.settings.angle_tolerance

        robot_heading = robot.imu()
        error = wrap(target_heading - robot_heading)

        if abs(error) < htol:
            robot.move(0.0, 0.0, dt)
            return TaskState.DONE

        w = kp * error
        w = float(clamp(w, -wmax, wmax))

        robot.move(0.0, w, dt)

        return TaskState.RUNNING

###########################################################

class HaltTask(AbstractTask):

    def __init__(self) -> None:
        super().__init__("HaltTask", "v: 0.0, w: 0.0")

    def cleanup(self, context: Any, dt: float) -> None:
        super().cleanup(context, dt)
        context.robot.move(0.0, 0.0, dt)

###########################################################

class BladeControlTask(AbstractTask):
    
    def __init__(self, state: int) -> None:
        states = ["off", "low", "high"]
        super().__init__("BladeControlTask", f"state: {states[state]}")

        # DO NOT overwrite AbstractTask.state
        self.blade_state: int = state

    def cleanup(self, context: Any, dt: float) -> None:
        super().cleanup(context, dt)
        context.robot.set_blade(self.blade_state)