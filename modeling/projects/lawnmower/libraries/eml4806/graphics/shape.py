from abc import ABC, abstractmethod

import numpy as np

from eml4806.geometry.transform import Transform
from eml4806.geometry.vector import vector, vectors, unit, append
from eml4806.geometry.angle import wrap

from eml4806.graphics.style import pen, brush
from eml4806.graphics.renderer import PlotRenderer, FillRenderer, ArrowRenderer

from numpy import sin, cos, pi

Vector = np.ndarray
Vectors = np.ndarray

# ---------------------------------------------------------------------------
# Abstract base: Drawable with a Transform
# ---------------------------------------------------------------------------

class AbstractDrawable(ABC):

    """Base drawable object with a local Transform and optional parent."""

    __slots__ = ('_transform', '_parent')

    def __init__(self, transform: Transform, parent=None):
        self._transform = transform.copy()
        self._parent = parent

    def position(self) -> Vector:
        return self._transform.translation()

    def set_position(self, p):
        self._transform.translate(p)
        self._update_geometry()

    def orientation(self) -> float:
        return self._transform.rotation()

    def set_orientation(self, a):
        self._transform.rotate(a)
        self._update_geometry()

    def transform(self) -> Transform:
        return self._transform.copy()

    def set_transform(self, tf: Transform):
        self._transform = tf.copy()
        self._update_geometry()

    def reset(self):
        self._transform = Transform()
        self._update_geometry()

    def move(self, p: Vector, *, relative: bool = False):
        self.translate(p, relative=relative)

    def translate(self, p: Vector, *, relative: bool = False):
        self._transform.translate(p, relative=relative)
        self._update_geometry()

    def rotate(self, r: Vector, *, relative: bool = False):
        self._transform.rotate(r, relative=relative)
        self._update_geometry()

    def scale(self, s: float, *, relative: bool = False):
        self._transform.scale(s, relative=relative)
        self._update_geometry()

    def set_parent(self, parent):
        self._parent = parent

    @abstractmethod
    def _update_geometry(self):
        ...

# ---------------------------------------------------------------------------
# GroupShape of drawables
# ---------------------------------------------------------------------------

class GroupShape(AbstractDrawable):

    """Just a collection of Drawables that share a parent transform."""

    __slots__ = ('_shapes',)

    def __init__(self, workspace, shapes, transform: Transform = Transform()):
        super().__init__(transform)
        self._shapes = list(shapes)
        for shape in self._shapes:
            shape.set_parent(self)

    def _update_geometry(self):
        for shape in self._shapes:
            shape._update_geometry()


# ---------------------------------------------------------------------------
# AbstractShape – connects geometry with renderer and style
# ---------------------------------------------------------------------------

class AbstractShape(AbstractDrawable):

    """Base class for shapes that define a _geometry() method."""

    __slots__ = ('_ax', '_style', '_artist', '_renderer')

    def __init__(self, workspace, style, transform: Transform, renderer):
        super().__init__(transform)
        self._ax = workspace._ax
        self._style = style
        self._artist = None
        self._renderer = renderer
        self._make()
        self._update_geometry()
        self._update_style()

    def hide(self):
        self._artist.set_visible(False)

    def show(self):
        self._artist.set_visible(True)

    def style(self):
        return self._style.copy()

    def set_style(self, value):
        self._style = value.copy()
        self._update_style()

    def _update_geometry(self):
        vertices = self._geometry()
        # print(vertices)
        if vertices.size == 0:
            return
        if self._parent is None:
            T = self._transform
        else:
            T = self._parent._transform @ self._transform
        vertices = T.apply(vertices)
        self._renderer.update_geometry(self, vertices)

    @abstractmethod
    def _geometry(self):
        ...

    def _make(self):
        self._renderer.make(self)

    def _update_style(self):
        self._renderer.update_style(self)

# ---------------------------------------------------------------------------
# RectangleShape
# ---------------------------------------------------------------------------

class RectangleShape(AbstractShape):

    __slots__ = ('_size', '_angle')

    def __init__(self, workspace, center, size, angle=0.0, style=brush()):
        self._size = vector(size)
        angle = wrap(angle)
        super().__init__(
            workspace,
            style,
            transform=Transform(translation=center, rotation=vector(0, 0, angle)),
            renderer=FillRenderer()
        )

    def set(self, center, size):
        self.set_center(center)
        self.set_size(size)

    def set_center(self, center):
        self.translate(center, relative=False)

    def set_size(self, size):
        self._size = vector(size)
        self._update_geometry()

    def _geometry(self):
        w, h, _ = 0.5 * self._size
        return vectors([
            [-w, -h],
            [+w, -h],
            [+w, +h],
            [-w, +h]
        ])

# ---------------------------------------------------------------------------
# CircleShape
# ---------------------------------------------------------------------------

class CircleShape(AbstractShape):

    __slots__ = ('_radius',)

    def __init__(self, workspace, center, radius, style=brush()):
        self._radius = float(radius)
        super().__init__(
            workspace,
            style,
            transform=Transform(translation=center),
            renderer=FillRenderer()
        )

    def set(self, center, radius):
        self.set_center(center)
        self.set_radius(radius)

    def set_center(self, center):
        self.translate(center)

    def set_radius(self, radius):
        self._radius = float(radius)
        self._update_geometry()

    def _geometry(self):
        r = self._radius
        a = np.linspace(0.0, 2 * pi, 72, endpoint=False)
        x = r * cos(a)
        y = r * sin(a)
        return vectors(x, y)

# ---------------------------------------------------------------------------
# PolygonShape & PolylineShape
# ---------------------------------------------------------------------------

class PolygonShape(AbstractShape):

    __slots__ = ('_points',)

    def __init__(self, workspace, edges=None, style=brush(), renderer=FillRenderer()):
        if edges is None:
            edges = []
        self._points = vectors(edges)
        super().__init__(workspace, style, Transform(), renderer)

    def set(self, edges):
        self.set_points(edges)

    def points(self) -> Vectors:
        """Return a copy of the internal points list."""
        return self._points

    def set_points(self, edges):
        self._points = vectors(edges)
        self._update_geometry()

    def clear(self):
        self._points = vectors()
        self._update_geometry()

    def first(self) -> Vector | None:
        if self._points.size == 0:
            return None
        return self._points[0]

    def last(self) -> Vector | None:
        if self._points.size == 0:
            return None
        return self._points[-1]

    def append(self, edges):
        self._points = append(self._points, edges)
        self._update_geometry()

    def _geometry(self):
        return self._points

class PolylineShape(PolygonShape):

    __slots__ = ('_marker', '_closed')

    def __init__(self, workspace, edges=None, style=pen(), marker=None, renderer=PlotRenderer(), closed=False):
        self._marker = marker
        self._closed = closed
        super().__init__(workspace, edges, style, renderer)

    def _geometry(self):
        points = self._points
        first = self.first()
        if self._closed and first is not None:
            points = append(points, first)
        return points

# ---------------------------------------------------------------------------
# LineShape
# ---------------------------------------------------------------------------

class LineShape(PolylineShape):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, [start, end], style)

    def set(self, start, end):
        super().set([start, end])

    def set_start(self, start):
        self.set([start, self._points[1]])

    def set_end(self, end):
        self.set([self._points[0], end])

# ---------------------------------------------------------------------------
# PointShape (as a single-vertex PolylineShape)
# ---------------------------------------------------------------------------

class PointShape(PolylineShape):

    def __init__(self, workspace, center, style=brush()):
        super().__init__(workspace, [center], style=style, marker='o')

    def set(self, center):
        self.set_points([center])

# ---------------------------------------------------------------------------
# RayShape (infinite-ish line)
# ---------------------------------------------------------------------------

class RayShape(LineShape):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, start, end, style)
        self.make_infinity()

    def set(self, start, end):
        super().set(start, end)
        self.make_infinity()

    def set_start(self, start):
        super().set_start(start)
        self.make_infinity()

    def set_end(self, point):
        super().set_end(point)
        self.make_infinity()

    def make_infinity(self, big=1e9):
        p1 = self._points[0]
        p2 = self._points[1]
        u = unit(p2 - p1)
        p_far = p1 + u * big
        p_near = p1 - u * big
        super().set(p_near, p_far)

# ---------------------------------------------------------------------------
# ArrowShape
# ---------------------------------------------------------------------------

class ArrowShape(AbstractShape):

    __slots__ = ('_origin', '_direction', '_scaling', '_magnification')

    def __init__(self, workspace, origin, direction, style=brush(), scaling=1.0):
        self._origin = vector(origin)
        self._direction = vector(direction)
        self._scaling = float(scaling)
        super().__init__(
            workspace,
            style,
            transform=Transform(),
            renderer=ArrowRenderer(),
        )

    def set(self, origin, direction):
        self.set_origin(origin)
        self.set_direction(direction)

    def set_origin(self, origin):
        self._origin = vector(origin)
        self._update_geometry()

    def set_direction(self, direction):
        self._direction = vector(direction)
        self._update_geometry()

    def _geometry(self):
        return vectors([self._origin, self._origin + self._scaling * self._direction])