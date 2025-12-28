from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from numpy import pi, sin, cos, clip

from eml4806.geometry.vector import vector
from eml4806.geometry.angle import wrap

##############################################################################################

class SkidDriveOdometer(ABC):

    __slots__ = ('track_width', 'maximum_linear_velocity', 'maximum_angular_velocity', 
                 '_x', '_y', '_theta', '_v', '_w')
    
    def __init__(self, track_width, maximum_linear_velocity, maximum_angular_velocity):

        self.track_width = track_width  # Distance between the left and right wheel contact lines
        self.maximum_linear_velocity = maximum_linear_velocity  # Impose safety speed limits in the internal controller
        self.maximum_angular_velocity = maximum_angular_velocity  # Impose safety rotation limits in the internal controller
    
    def initialize(self, position, heading):
        position = vector(position)
        heading = wrap(heading)
        self._x = position[0]
        self._y = position[1]
        self._theta = heading
        self._v = 0.0
        self._w = 0.0

    def position(self):
        return vector(self._x, self._y)
    
    def orientation(self):
        return self._theta
    
    def pose(self):
        return self.position(), self.orientation()
    
    def wheel_velocities(self):
        vl = self._v - (0.5 * self.track_width) * self._w
        vr = self._v + (0.5 * self.track_width) * self._w
        return vr, vl

    def integrate(self, v, w, dt, tol=1e-3):
        vmax = self.maximum_linear_velocity
        wmax = self.maximum_angular_velocity
        # Remember
        self._v = v
        self._w = w
        # Imposed safety limits
        if vmax is not None:
            v = clip(v, -vmax, vmax)
        if wmax is not None:
            w = clip(w, -wmax, wmax)
        # Update pose
        self._integrate(v, w, dt, tol)

    @abstractmethod
    def _integrate(self, v, w, dt, tol): ...

##############################################################################################

@dataclass
class FirstOrderSkidDriveOdometer(SkidDriveOdometer):

    def __init__(self, track_width, maximum_linear_velocity, maximum_angular_velocity):
        super().__init__(track_width, maximum_linear_velocity, maximum_angular_velocity)
    
    def _integrate(self, v, w, dt, tol):
        ds = v * dt  # Forward linear displacement
        da = w * dt  # Change in heading (yaw)
        self._x += ds * cos(self._theta)
        self._y += ds * sin(self._theta)
        self._theta += da

##############################################################################################

@dataclass
class SecondOrderSkidDriveOdometer(SkidDriveOdometer):

    def __init__(self, track_width, maximum_linear_velocity, maximum_angular_velocity):
        super().__init__(track_width, maximum_linear_velocity, maximum_angular_velocity)
    
    def _integrate(self, v, w, dt, tol):
        ds = v * dt  # Forward linear displacement
        da = w * dt  # Change in heading (yaw)
        a = self._theta + 0.5 * da  # Midpoint heading
        self._x += ds * cos(a)
        self._y += ds * sin(a)
        self._theta += da
        
##############################################################################################

@dataclass
class AnalyticalSkidDriveOdometer(SkidDriveOdometer):

    def __init__(self, track_width, maximum_linear_velocity, maximum_angular_velocity):
        super().__init__(track_width, maximum_linear_velocity, maximum_angular_velocity)
        
    def _integrate(self, v, w, dt, tol):
        ds = v * dt  # Forward linear displacement
        da = w * dt  # Change in heading (yaw)
        # Straight line (small-angle) case 
        if abs(da) < tol:
            a = self._theta + 0.5 * da  # Midpoint heading
            self._x += ds * cos(a)
            self._y += ds * sin(a)
            self._theta += da
        else:
            # General analytic case
            r = ds / da  # instantaneous turning radius
            a = self._theta + da  # Heading
            self._x += r * (sin(a) - sin(self._theta))
            self._y -= r * (cos(a) - cos(self._theta))
            self._theta += da