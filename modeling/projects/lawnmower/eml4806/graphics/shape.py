from abc import ABC, abstractmethod

import math
import numpy as np
import matplotlib.pyplot as plt

import eml4806.geometry.vector as vector
from eml4806.geometry.transform import Transform

from eml4806.graphics.workspace import Workspace
from eml4806.graphics.style import pen, brush
from eml4806.graphics.renderer import PlotRenderer, FillRenderer, ArrowRenderer

###############################################################


class AbstractDrawable(ABC):
    """No _geometry yet!"""

    def __init__(self, transform, parent=None):
        self._transform = transform.clone()
        self._parent = parent

    def transform(self):
        return self._transform.clone()

    def setTransform(self, value):
        self._transform = value.clone()
        self._updateGeometry()

    def move(self, position, relative=False):
        if relative:
            self._transform._position += position
        else:
            self._transform._position = position
        self._updateGeometry()

    def rotate(self, angle, relative=False):
        if relative:
            self._transform._orientation += angle
        else:
            self._transform._orientation = float(angle)
        self._updateGeometry()

    def scale(self, scaling, relative=False):
        if np.isscalar(scaling):
            scaling = (scaling, scaling)
        if relative:
            self._transform._scaling += scaling
        else:
            self._transform._scaling = scaling
        self._updateGeometry()

    def setParent(self, parent):
        self._parent = parent

    @abstractmethod
    def _updateGeometry(self): ...


###############################################################


class Group(AbstractDrawable):
    """Just a collection of Drawables"""

    def __init__(self, children, transform=Transform()):
        super().__init__(transform)
        self._children = list(children)
        for child in self._children:
            child.setParent(self)

    def _updateGeometry(self):
        for child in self._children:
            child._updateGeometry()


###############################################################


class AbstractShape(AbstractDrawable):
    """Define _geometry"""

    def __init__(self, workspace, style, transform, renderer):
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
        if vector.isEmpty(vertices):
            return
        if self._parent is None:
            T = self._transform
        else:
            T = Transform.compound(self._parent._transform, self._transform)
        vertices = T.apply(vertices)
        self._renderer.updateGeometry(self, vertices)

    @abstractmethod
    def _geometry(self):
        """Create the shape's vertices"""
        pass

    def _make(self):
        self._renderer.make(self)

    def _updateStyle(self):
        self._renderer.updateStyle(self)


###############################################################


class Rectangle(AbstractShape):

    def __init__(self, workspace, position, width, height, angle=0.0, style=brush()):
        self.w = width
        self.h = height
        super().__init__(
            workspace,
            style,
            transform=Transform(position=position, orientation=angle),
            renderer=FillRenderer(),
        )

    def _geometry(self):
        w = 0.5 * self.w
        h = 0.5 * self.h
        return vector.ensureMany([[-w, -h], [w, -h], [w, h], [-w, h]])

###############################################################

class Circle(AbstractShape):

    def __init__(self, workspace, position, radious, style=brush()):
        self._radious = radious
        super().__init__(
            workspace, 
            style, 
            transform=Transform(position=position), 
            renderer=FillRenderer()
        )

    def set(self, p, r):
        self._radious = r
        self.move(p)

    def setRadious(self, r):
        self._radious = r
        self._updateGeometry()

    def _geometry(self):
        a = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
        x = self._radious * np.cos(a)
        y = self._radious * np.sin(a)
        return vector.new(x, y)

###############################################################

class Point(Circle):

    def __init__(self, workspace, position, style=brush()):
        super().__init__(workspace, position, 0.05, style)

    def set(self, p, r=None):
        if r is None: 
            r = self._radious
        super().set(p, r)

###############################################################

class Polygon(AbstractShape):

    def __init__(self, workspace, edges=[], style=brush(), renderer=FillRenderer()):
        self._points = vector.ensureMany(edges)
        super().__init__(workspace, style, Transform(), renderer)

    def set(self, edges):
        self.setPoints(edges)

    def isEmpty(self):
        return vector.isEmpty(self._points)

    def points(self):
        return self._points.copy()

    def setPoints(self, points):
        self._points = vector.ensureMany(points)
        self._updateGeometry()

    def clear(self):
        self.setPoints([])
        self._updateGeometry()

    def last(self):
        if self.isEmpty():
            return None
        return self._points[-1, :]

    def append(self, edges):
        self._points = vector.append(self._points, edges)
        self._updateGeometry()

    def _geometry(self):
        return self._points

###############################################################

class Polyline(Polygon):

    def __init__(self, workspace, edges=[], style=pen(), marker=None, renderer=PlotRenderer()):
        self._marker = marker
        super().__init__(workspace, edges, style, renderer)

###############################################################

class Line(Polyline):

    def __init__(self, workspace, start, end, style=pen(), marker=None):
        super().__init__(workspace, [start, end], style, marker)

    def set(self, start, end):
        super().set([start, end])

    def setStart(self, point):
        self.set([point, self._points[1]])

    def setEnd(self, point):
        self.set([self._points[0], point])


class Ray(Line):

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

    def makeInfity(self, big=1e8):
        p1 = self._points[0]
        p2 = self._points[1]
        u = vector.unit(p2 - p1)
        p2 = p1 + u * big
        p1 = p1 - u * big
        super().set(p1, p2)

###############################################################

class Arrow(AbstractShape):

    def __init__(self, workspace, origin, direction, style=brush(), scaling=1.0, magnification=10.0):
        self._origin = vector.ensureOne(origin)
        self._direction = vector.ensureOne(direction)
        self._scaling = float(scaling)
        self._magnification = float(magnification)
        super().__init__(
            workspace, 
            style, 
            transform=Transform(), 
            renderer=ArrowRenderer()
        )

    def set(self, o, d):
        self.setOrigin(o)
        self.setDirection(d)
        
    def setOrigin(self, o):
        self._origin = vector.ensureOne(o)
        self._updateGeometry()

    def setDirection(self, d):
        self._direction = vector.ensureOne(d)
        self._updateGeometry()
    
    def _geometry(self):
        return np.array([self._origin, self._origin + self._scaling*self._direction])
