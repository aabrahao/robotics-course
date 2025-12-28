from eml4806.geometry.transform import Transform
from eml4806.geometry.vector import coincident

from eml4806.robot.tool import BladeState

from eml4806.graphics.map import CoverageMap

class Chassis:

    __slots__ = ('length', 'width', 'wheelbase', 'trackwidth')
    
    def __init__(self, *, length, width, wheelbase, trackwidth):
        self.length = length          # m
        self.width = width            # m
        self.wheelbase = wheelbase    # m
        self.trackwidth = trackwidth  # m

class Wheel:

    __slots__ = ('diameter', 'width')
    
    def __init__(self, *, diameter, width):
        self.diameter = diameter  # m
        self.width = width        # m

class Motor:

    __slots__ = ('maximum_angular_velocity',)
    
    def __init__(self, *, maximum_angular_velocity):
        self.maximum_angular_velocity = maximum_angular_velocity  # rad/s

class Robot:

    __slots__ = (
        'chassis', 'wheels', 'motors', 'blade', 
        'odometer', 'body', 'wheel1', 'wheel2', 'wheel3', 'wheel4',
        'tool', '_coverage_map', '_debug', '_position_point', '_vl_arrow',
        '_vr_arrow', '_path', '_path_sampling_resolution'
    )

    def __init__(self, world, position, theta, chassis, wheels, motors, blade, odometer):
        # Body
        self.chassis = chassis
        self.wheels = wheels
        self.motors = motors
        self.blade = blade
        # Blade coverage
        self._coverage_map = CoverageMap(world)
        # Distance between recorded points along the path
        self._path_sampling_resolution = 0.1 # m 
        # Odometry
        self.odometer = odometer
        self.odometer.initialize(position, theta)
        # Graphics
        self._make_body(world)
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
        self._coverage_map.clear()

    def debug(self):
        return self._debug
    
    def set_debug(self, visible):
        if self._debug == visible:
            return
        if visible:
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
    
    def blade_state(self):
        return self.blade.state

    def set_blade(self, state):
        self.blade.state = state

    def toggle_blade_state(self):
        self.blade.toggle()
    
    def _make_body(self, world):
        # Parts
        cl = self.chassis.length
        cw = self.chassis.width
        wb = self.chassis.wheelbase
        tw = self.chassis.trackwidth
        wd = self.wheels.diameter
        ww = self.wheels.width
        bd = self.blade.diameter
        # Graphics
        self.body   = world.rectangle((0.0, 0.0), (cl, cw), color='orange')
        self.wheel1 = world.rectangle((-0.5*wb, -0.5*tw), (wd, ww), color='gray')
        self.wheel2 = world.rectangle(( 0.5*wb, -0.5*tw), (wd, ww), color='gray')
        self.wheel3 = world.rectangle((-0.5*wb,  0.5*tw), (wd, ww), color='gray')
        self.wheel4 = world.rectangle(( 0.5*wb,  0.5*tw), (wd, ww), color='gray')
        self.tool   = world.circle((0.0, 0.0), 0.5*bd, color='red')
        # Debug
        self._position_point = world.point(self.gps(), color='magenta')
        self._vl_arrow  = world.arrow((0.0,-0.5*tw), (0.0, 0.0), color='blue', scaling=1.25)
        self._vr_arrow  = world.arrow((0.0, 0.5*tw), (0.0, 0.0), color='blue', scaling=1.25)
        # Assembly
        self.body = world.group([self.body, 
                                 self.wheel1, self.wheel2, self.wheel3, self.wheel4, 
                                 self.tool, 
                                 self._vl_arrow, self._vr_arrow])
        # Path
        self._path = world.polyline([self.odometer.position()], color='magenta')
        # Update graphics
        self._update()

    def _update(self):
        self._update_body()
        self._update_path()
        self._update_debug()

    def _update_body(self):
        p, h = self.odometer.pose()
        tf = Transform(translation=p, rotation=(0.0, 0.0, h))
        self.body.set_transform(tf)
    
    def _update_path(self):
        position = self.odometer.position()
        last = self._path.last()
        if last is None: # Empty
            self._path.append(position)
            self._update_coverage_map(position)
            return
        if not coincident(position, last, tol=self._path_sampling_resolution): # Moved!
            self._path.append(position)
            self._update_coverage_map(position)

    def _update_coverage_map(self, position):
        s = self.blade.state
        if s == BladeState.OFF:
            return
        x, y, _ = position
        r = 0.5 * self.blade.diameter
        self._coverage_map.cut(x, y, r, s)
   
    def _update_debug(self):
        vl, vr = self.odometer.wheel_velocities()
        self._position_point.set(self.gps())
        self._vl_arrow.set_direction((vl, 0.0))
        self._vr_arrow.set_direction((vr, 0.0))