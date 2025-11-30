from abc import ABC, abstractmethod

import numpy as np

from eml4806.geometry.transform import Transform
from eml4806.geometry.vector import Vector, toVector, toVectors, angle, length, polar, unit

from eml4806.graphics.style import pen, brush
from eml4806.graphics.renderer import PlotRenderer, FillRenderer, ArrowRenderer

from numpy import sin, cos, pi

# ---------------------------------------------------------------------------
# Abstract base: Drawable with a Transform
# ---------------------------------------------------------------------------

class AbstractDrawable(ABC):

    """Base drawable object with a local Transform and optional parent."""

    def __init__(self, transform: Transform, parent=None):
        self._transform = transform.clone()
        self._parent = parent

    def position(self) -> Vector:
        return self._transform.translation()

    def setPosition(self, p):
        self._transform.translate(p)
        self._updateGeometry()

    def orientation(self) -> float:
        return self._transform.rotation()

    def setOrientation(self, a):
        self._transform.rotate(a)
        self._updateGeometry()

    def transform(self) -> Transform:
        return self._transform.clone()

    def setTransform(self, tf: Transform):
        self._transform = tf.clone()
        self._updateGeometry()

    def reset(self):
        self._transform = Transform()
        self._updateGeometry()

    def move(self, p, relative: bool = False):
        self.translate(p, relative)

    def translate(self, p, relative: bool = False):
        self._transform.translate(p, relative)
        self._updateGeometry()

    def rotate(self, a, relative: bool = False):
        self._transform.rotate(a, relative)
        self._updateGeometry()

    def scale(self, s, relative: bool = False):
        self._transform.scale(s, relative)
        self._updateGeometry()

    def setParent(self, parent):
        self._parent = parent

    @abstractmethod
    def _updateGeometry(self):
        ...

# ---------------------------------------------------------------------------
# GroupShape of drawables
# ---------------------------------------------------------------------------

class GroupShape(AbstractDrawable):

    """Just a collection of Drawables that share a parent transform."""

    def __init__(self, workspace: 'Workspace', shapes, transform: Transform = Transform()):
        super().__init__(transform)
        self._shapes = list(shapes)
        for shape in self._shapes:
            shape.setParent(self)

    def _updateGeometry(self):
        for shape in self._shapes:
            shape._updateGeometry()


# ---------------------------------------------------------------------------
# AbstractShape – connects geometry with renderer and style
# ---------------------------------------------------------------------------

class AbstractShape(AbstractDrawable):

    """Base class for shapes that define a _geometry() method."""

    def __init__(self, workspace: 'Workspace', style, transform: Transform, renderer):
        super().__init__(transform)
        self._ax = workspace.axis
        self._style = style
        self._artist = None
        self._renderer = renderer
        self._make()
        self._updateGeometry()
        self._updateStyle()

    def hide(self):
        self._artist.set_visible(False)

    def show(self):
        self._artist.set_visible(True)

    def style(self):
        return self._style.clone()

    def setStyle(self, value):
        self._style = value.clone()
        self._updateStyle()

    def _updateGeometry(self):
        vertices = self._geometry()
        if not vertices:
            return
        if self._parent is None:
            T = self._transform
        else:
            T = Transform.compound(self._parent._transform, self._transform)
        vertices = T.apply(vertices)
        self._renderer.updateGeometry(self, vertices)

    @abstractmethod
    def _geometry(self):
        ...

    def _make(self):
        self._renderer.make(self)

    def _updateStyle(self):
        self._renderer.updateStyle(self)


# ---------------------------------------------------------------------------
# RectangleShape
# ---------------------------------------------------------------------------

class RectangleShape(AbstractShape):

    def __init__(self, workspace, center, size, angle=0.0, style=brush()):
        self._size = toVector(size)
        super().__init__(
            workspace,
            style,
            transform=Transform(translation=center, rotation=angle),
            renderer=FillRenderer()
        )

    def set(self, c, s):
        self.setCenter(c)
        self.setSize(s)

    def setCenter(self, c):
        self.translate(c, relative=False)

    def setSize(self, s):
        self._size = toVector(s)
        self._updateGeometry()

    def _geometry(self):
        w, h = 0.5*self._size
        return [
            Vector(-w, -h),
            Vector(+w, -h),
            Vector(+w, +h),
            Vector(-w, +h)
        ]

# ---------------------------------------------------------------------------
# CircleShape
# ---------------------------------------------------------------------------

class CircleShape(AbstractShape):

    def __init__(self, workspace, center, radious, style=brush()):
        self._radious = float(radious)
        super().__init__(
            workspace,
            style,
            transform=Transform(translation=center),
            renderer=FillRenderer()
        )

    def set(self, c, r):
        self.setCenter(c)
        self.setRadious(r)

    def setCenter(self, c):
        self.translate(c)

    def setRadious(self, r):
        self._radious = float(r)
        self._updateGeometry()

    def _geometry(self):
        r = self._radious
        a = np.linspace(0.0, 2 * pi, 72, endpoint=False)
        return [Vector(r * cos(t), r * sin(t)) for t in a]

# ---------------------------------------------------------------------------
# PolygonShape & PolylineShape
# ---------------------------------------------------------------------------

class PolygonShape(AbstractShape):

    def __init__(self, workspace, edges=[], style=brush(), renderer=FillRenderer()):
        self._points = toVectors(edges)
        super().__init__(workspace, style, Transform(), renderer)

    def set(self, edges):
        self.setPoints(edges)

    def points(self) -> list[Vector]:
        """Return a copy of the internal points list."""
        return [Vector(p) for p in self._points]

    def setPoints(self, points):
        self._points = toVectors(points)
        self._updateGeometry()

    def clear(self):
        self._points = []
        self._updateGeometry()

    def last(self) -> Vector | None:
        if not self._points:
            return None
        return self._points[-1]

    def append(self, edges):
        self._points.extend(toVectors(edges))
        self._updateGeometry()

    def _geometry(self):
        return self._points

class PolylineShape(PolygonShape):

    def __init__(self, workspace, edges=[], style=pen(), marker=None, renderer=PlotRenderer()):
        self._marker = marker
        super().__init__(workspace, edges, style, renderer)

# ---------------------------------------------------------------------------
# LineShape
# ---------------------------------------------------------------------------

class LineShape(PolylineShape):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, [start, end], style)

    def set(self, start, end):
        super().set([start, end])

    def setStart(self, point):
        self.set([point, self._points[1]])

    def setEnd(self, point):
        self.set([self._points[0], point])

# ---------------------------------------------------------------------------
# PointShape (as a single-vertex PolylineShape)
# ---------------------------------------------------------------------------

class PointShape(PolylineShape):

    def __init__(self, workspace, center, style=brush()):
        super().__init__(workspace, [center], style=style, marker='o')

    def set(self, c):
        self.setPoints([c])

# ---------------------------------------------------------------------------
# RayShape (infinite-ish line)
# ---------------------------------------------------------------------------

class RayShape(LineShape):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, start, end, style)
        self.makeInfity()

    def set(self, start, end):
        super().set(start, end)
        self.makeInfity()

    def setStart(self, point):
        super().setStart(point)
        self.makeInfity()

    def setEnd(self, point):
        super().setEnd(point)
        self.makeInfity()

    def makeInfity(self, big=1e9):
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

    def __init__(self, workspace, origin, direction, style=brush(),
                 scaling=1.0, magnification=10.0):
        self._origin = toVector(origin)
        self._direction = toVector(direction)
        self._scaling = float(scaling)
        self._magnification = float(magnification)
        super().__init__(
            workspace,
            style,
            transform=Transform(),
            renderer=ArrowRenderer(),
        )

    def set(self, o, d):
        self.setOrigin(o)
        self.setDirection(d)

    def setOrigin(self, o):
        self._origin = toVector(o)
        self._updateGeometry()

    def setDirection(self, d):
        self._direction = toVector(d)
        self._updateGeometry()

    def _geometry(self):
        return [self._origin, self._origin + self._scaling*self._direction]
