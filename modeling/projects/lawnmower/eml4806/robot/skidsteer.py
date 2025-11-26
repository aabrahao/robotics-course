from dataclasses import dataclass
import numpy as np

from eml4806.geometry.vector import vector, coincident
from eml4806.geometry.transform import Transform
from eml4806.graphics.style import Style, Stroke, Fill, pen, brush
from eml4806.graphics.shape import Rectangle, Circle, Polyline, Group, Arrow

@dataclass
class Chassis:
    length    : float = 0.0 # m
    width     : float = 0.0 # m
    wheelbase : float = 0.0 # m
    trackwidth: float = 0.0 # m

@dataclass
class Wheel:
    diameter: float = 0.0  # m
    width: float = 0.0     # m

@dataclass
class Motor:
    maximum_angular_velocity: float = 0.0  # rad/s

@dataclass
class Blade:
    diameter : float = 0.0 # m
    on: bool = False
    height: float = 0.0 # m

class Robot:
    def __init__(self, workspace, position, theta, chassis, wheels, motors, blade, odometer):
        # Body
        self.chassis = chassis
        self.wheels = wheels
        self.motors = motors
        self.blade = blade
        # Odometry
        self.odometer = odometer
        x, y = position
        self.odometer.initilize((x, y, theta))
        # Graphics
        self._makeBody(workspace)
         # Debug
        self._debug = True

    def gps(self):
        return self.odometer.position()

    def imu(self):
        return self.odometer.orientation()

    # Control wheel shaft rotation (rad/s)
    def move(self, v, w, dt):
        self.odometer.integrate(v, w, dt, tol=0.001)
        self._update()

    def debug(self):
        return self._debug
    
    def setDebug(self, visible):
        if self._debug == visible:
            return
        if visible == True:
            self.path.show()
            self.arrow_vl.show()
            self.arrow_vr.show()
        else:
            self.path.hide()
            self.arrow_vl.hide()
            self.arrow_vr.hide()
        self._debug = visible
    
    def _makeBody(self, workspace):
        # Parts
        c = self.chassis
        w = self.wheels
        b = self.blade
        self.body   = Rectangle(workspace, (0.0, 0.0), c.length, c.width, style=brush('orange', 0.5))
        self.wheel1 = Rectangle(workspace, (-0.5*c.wheelbase, -0.5*c.trackwidth), w.diameter, w.width, style=brush('gray', 0.5))
        self.wheel2 = Rectangle(workspace, ( 0.5*c.wheelbase, -0.5*c.trackwidth), w.diameter, w.width, style=brush('gray', 0.5))
        self.wheel3 = Rectangle(workspace, (-0.5*c.wheelbase,  0.5*c.trackwidth), w.diameter, w.width, style=brush('gray', 0.5))
        self.wheel4 = Rectangle(workspace, ( 0.5*c.wheelbase,  0.5*c.trackwidth), w.diameter, w.width, style=brush('gray', 0.5))
        self.tool   = Circle(workspace, (0.0, 0.0), 0.5*b.diameter, brush('red', 0.5))
        # Debug
        self.arrow_vl = Arrow(workspace, (0.0,-0.5*c.trackwidth), (0.0, 0.0), style=brush('blue', 3.0), scaling=1.25)
        self.arrow_vr = Arrow(workspace, (0.0, 0.5*c.trackwidth), (0.0, 0.0), style=brush('blue', 3.0), scaling=1.25)
        # Assembly
        self.body = Group([self.body, self.wheel1, self.wheel2, self.wheel3, self.wheel4, self.tool, self.arrow_vl, self.arrow_vr])
        # Path
        self.path = Polyline(workspace, [self.odometer.position()], style=pen('magenta'))
        # Update graphics
        self._update()

    def _update(self):
        self._updateBody()
        self._updatePath()
        self._updateDebug()

    def _updateBody(self):
        x, y, theta = self.odometer.pose()
        tf = Transform(position=(x, y), orientation=theta)
        self.body.setTransform(tf)
    
    def _updatePath(self):
        position = self.odometer.position()
        last = self.path.last()
        if not coincident(position, last, tol=0.2):
            self.path.append( position )

    def _updateDebug(self):
        vl, vr = self.odometer.wheelVelocities()
        self.arrow_vl.setDirection( (vl, 0.0) )
        self.arrow_vr.setDirection( (vr, 0.0) )