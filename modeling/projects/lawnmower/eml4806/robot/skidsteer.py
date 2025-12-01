from dataclasses import dataclass
import numpy as np

from eml4806.geometry.transform import Transform
from eml4806.geometry.vector import Vector, coincident
from eml4806.robot.tool import BladeState

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

class Robot:

    def __init__(self, world, position, theta, chassis, wheels, motors, blade, odometer, map_tool=True):
        # Body
        self.chassis = chassis
        self.wheels = wheels
        self.motors = motors
        self.blade = blade
        # Blade control
        self.blade_position = BladeState.OFF # BladeState.LOW and BladeState.HIGH
        # Odometry
        self.odometer = odometer
        self.odometer.initilize(position, theta)
        # Graphics
        self._makeBody(world)
        # Map
        if map_tool:
            self._map = world.map()
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

    def reset(self):
        self._path.set([self.odometer.position()])
        self._map.clear()

    def debug(self):
        return self._debug
    
    def setDebug(self, visible):
        if self._debug == visible:
            return
        if visible == True:
            self._position_point.show()
            self._path.show()
            self._vl_arrow.show()
            self._vr_arrow.show()
        else:
            self._position_point.hide()
            self._path.hide()
            self._vl_arrow.hide()
            self._vr_arrow.hide()
        self._debug = visible
    
    def bladState(self):
        return self.blade.state

    def setBlade(self, state):
        self.blade.state = state

    def toggleBladeState(self):
        self.blade.toggle()
    
    def _makeBody(self, world):
        # Parts
        cl = self.chassis.length
        cw = self.chassis.width
        wb = self.chassis.wheelbase
        tw = self.chassis.trackwidth
        wd = self.wheels.diameter
        ww = self.wheels.width
        bd = self.blade.diameter
        # Graphics
        self.body   = world.rectangle((0.0, 0.0), (cl, cw), 'orange')
        self.wheel1 = world.rectangle((-0.5*wb, -0.5*tw), (wd, ww), 'gray')
        self.wheel2 = world.rectangle(( 0.5*wb, -0.5*tw), (wd, ww), 'gray')
        self.wheel3 = world.rectangle((-0.5*wb,  0.5*tw), (wd, ww), 'gray')
        self.wheel4 = world.rectangle(( 0.5*wb,  0.5*tw), (wd, ww), 'gray')
        self.tool   = world.circle((0.0, 0.0), 0.5*bd, 'red')
        # Debug
        self._position_point = world.point(self.gps(), 'magenta')
        self._vl_arrow  = world.arrow((0.0,-0.5*tw), (0.0, 0.0), 'blue', width=3.0, scaling=1.25)
        self._vr_arrow  = world.arrow((0.0, 0.5*tw), (0.0, 0.0), 'blue', width=3.0, scaling=1.25)
        # Assembly
        self.body = world.group([self.body, 
                                 self.wheel1, self.wheel2, self.wheel3, self.wheel4, 
                                 self.tool, 
                                 self._vl_arrow, self._vr_arrow])
        # Path
        self._path = world.polyline([self.odometer.position()], 'magenta')
        # Update graphics
        self._update()

    def _update(self):
        self._updateBody()
        self._updatePath()
        self._updateDebug()

    def _updateBody(self):
        p, h = self.odometer.pose()
        tf = Transform(translation=p, rotation=h)
        self.body.setTransform(tf)
    
    def _updatePath(self):
        position = self.odometer.position()
        last = self._path.last()
        if last is None: # Empty
            self._path.append(position)
            self._updateMap(position)
            return
        if not coincident(position, last, tol=0.1): # Moved!
            self._path.append(position)
            self._updateMap(position)

    def _updateMap(self, position):
        c = self.blade.cut()
        if c == None:
            return
        x,y = position
        r = 0.5*self.blade.diameter
        self._map.circle(x, y, r, func=lambda x: c)
    
    def _updateDebug(self):
        vl, vr = self.odometer.wheelVelocities()
        self._position_point.set( self.gps() )
        self._vl_arrow.setDirection( (vl, 0.0) )
        self._vr_arrow.setDirection( (vr, 0.0) )