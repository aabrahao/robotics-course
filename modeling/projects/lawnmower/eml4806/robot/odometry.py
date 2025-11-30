from abc import ABC, abstractmethod
from dataclasses import dataclass
from numpy import pi, sin, cos, clip, array

from eml4806.geometry.vector import Vector

##############################################################################################

@dataclass
class SkidDriveOdometer(ABC):
    track_width             : float = 0.0 # Effective_track_width # Distance between the left and right wheel contact lines
    maximum_linear_velocity : float = None # Impose safety speed limites in the internal controller
    maximum_angular_velocity: float = None # Impose safety rotation limites in the internal controller
    
    def initilize(self, pose):
        self._x = float(pose[0])
        self._y = float(pose[1])
        self._theta = float(pose[2])
        self._v = 0.0
        self._w = 0.0

    def position(self):
        return Vector(self._x, self._y)
    
    def orientation(self):
        return self._theta
    
    def pose(self):
        return self.position(), self.orientation()
    
    def wheelVelocities(self):
        vl = self._v - (0.5*self.track_width)*self._w
        vr = self._v + (0.5*self.track_width)*self._w
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
    
    def _integrate(self, v, w, dt, tol):
        ds = v*dt # Forward linear displacement
        da = w*dt # Change in heading (yaw)
        self._x += ds*cos(self._theta)
        self._y += ds*sin(self._theta)
        self._theta += da

##############################################################################################

@dataclass
class SecondOrderSkidDriveOdometer(SkidDriveOdometer):
    
    def _integrate(self, v, w, dt, tol):
        ds = v*dt # Forward linear displacement
        da = w*dt # Change in heading (yaw)
        a = self._theta + 0.5*da # Midpoint heading
        self._x += ds * cos(a)
        self._y += ds * sin(a)
        self._theta += da
        
##############################################################################################

@dataclass
class AnalyticalSkidDriveOdometer(SkidDriveOdometer):
        
    def _integrate(self, v, w, dt, tol):
        ds = v*dt # Forward linear displacement
        da = w*dt # Change in heading (yaw)
        # Straigth line (small-angle) case 
        if abs(da) < tol:
            a = self._theta + 0.5*da # Midpoint heading
            self._x += ds * cos(a)
            self._y += ds * sin(a)
            self._theta += da
        else:
            # General analytic case
            r = ds/da  # instantaneous turning radius
            a = self._theta + da # Heading
            self._x += r * (sin(a) - sin(self._theta))
            self._y -= r * (cos(a) - cos(self._theta))
            self._theta += da
