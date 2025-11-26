import math
import numpy as np
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch as ArrowPatch

from eml4806.geometry.vector import scalar, vector, ensure, unit, append
from eml4806.graphics.workspace import Workspace
from eml4806.graphics.style import Stroke, Fill, Style, pen, brush
from eml4806.geometry.transform import Transform

###############################################################


class Drawable(ABC):

    def __init__(self, transform, parent=None):
        self._transform = transform.clone()
        self._parent = parent

    def transform(self):
        return self._transform.clone()

    def setTransform(self, value):
        self._transform = value.clone()
        self._updateTransform()

    def move(self, position, relative=False):
        if relative: self._transform._position += position
        else: self._transform._position = position
        self._updateTransform()

    def rotate(self, angle, relative=False):
        if relative: self._transform._orientation += angle
        else: self._transform._orientation = float(angle)
        self._updateTransform()

    def scale(self, scaling, relative=False):
        if scalar(scaling): scaling = (scaling, scaling)
        if relative: self._transform._scaling += scaling
        else: self._transform._scale = scaling
        self._updateTransform()

    def setParent(self, parent):
        self._parent = parent

    @abstractmethod
    def _updateTransform(self): ...


###############################################################


class Group(Drawable):

    def __init__(self, children, transform=Transform()):
        super().__init__(transform)
        self._children = list(children)
        for child in self._children:
            child.setParent(self)

    def _updateTransform(self):
        for child in self._children:
            child._updateTransform()


###############################################################


class Shape(Drawable):

    def __init__(self, workspace, style, transform):
        super().__init__(transform)
        self._ax = workspace.axis
        self._style = style
        self._artist = None
        self._make()
        self._updateTransform()
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

    def _updateTransform(self):
        o = self._shape()
        if o is None:
            return
        if self._parent is None:
            T = self._transform
        else:
            T = Transform.compound(self._parent._transform, self._transform)
        o = T.apply(o)
        self._updateShape(o)

    @abstractmethod
    def _shape(self): ...

    @abstractmethod
    def _make(self): ...

    @abstractmethod
    def _updateShape(self, o): ...

    @abstractmethod
    def _updateStyle(self): ...


###############################################################


class Plot(Shape):

    def __init__(self, workspace, style, transform):
        super().__init__(workspace, style, transform)

    def _make(self):
        # use the provided axes instead of the global pyplot
        self._artist = self._ax.plot([], [])[0]

    def _updateShape(self, o):
        self._artist.set_data(o[:, 0], o[:, 1])

    def _updateStyle(self):
        s = self._style
        if s.stroke is not None:
            self._artist.set_color(s.stroke.color)
            self._artist.set_linewidth(s.stroke.width)
        self._artist.set_alpha(s.opacity)


###############################################################


class Fill(Shape):

    def __init__(self, workspace, style, transform):
        super().__init__(workspace, style, transform)

    def _make(self):
        self._artist = self._ax.fill([], [])[0]

    def _updateShape(self, o):
        # o is expected to be an (N, 2) array of vertices
        self._artist.set_xy(o)

    def _updateStyle(self):
        s = self._style
        if s.fill is not None:
            self._artist.set_facecolor(s.fill.color)
        if s.stroke is not None:
            self._artist.set_edgecolor(s.stroke.color)
            self._artist.set_linewidth(s.stroke.width)
        self._artist.set_alpha(s.opacity)


###############################################################


class Rectangle(Fill):

    def __init__(
        self, workspace, position, width, height, angle=0.0, style=brush()
    ):
        self.w = width
        self.h = height
        super().__init__(workspace, style, Transform(position=position, orientation=angle))

    def _shape(self):
        w = 0.5 * self.w
        h = 0.5 * self.h
        return np.array(
            [
                [-w, -h],
                [w, -h],
                [w, h],
                [-w, h],
            ]
        )


###############################################################


class Circle(Fill):

    def __init__(self, workspace, position, radious, style=brush()):
        self.r = radious
        super().__init__(workspace, style, Transform(position=position))

    def _shape(self):
        a = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
        x = self.r * np.cos(a)
        y = self.r * np.sin(a)
        return vector(x, y)


###############################################################


class Point(Circle):

    def __init__(self, workspace, position, style=brush()):
        super().__init__(workspace, position, 0.05, style)

    def _shape(self):
        a = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
        x = self.r * np.cos(a)
        y = self.r * np.sin(a)
        return vector(x, y)

###############################################################

class Polygon(Fill):

    def __init__(self, workspace, edges=None, style=brush()):
        self._points = edges
        super().__init__(workspace, style)

    def points(self):
        return self._points.copy()
    
    def setPoints(self, points):
        self._points = ensure(points)
    
    def append(self, edges):
        self._points = append(self._points, edges)

    def _shape(self):
        return self._points

###############################################################

class Polyline(Plot):

    def __init__(self, workspace, edges=None, style=pen()):
        self._points = ensure(edges)
        super().__init__(workspace, style, Transform())

    def points(self):
        return self._points.copy()
    
    def setPoints(self, points):
        self._points = ensure(points)
        self._updateShape(self._points)
    
    def append(self, edges):
        self._points = append(self._points, edges)
        self._updateShape(self._points)

    def last(self):
        return self._points[-1,:]

    def clear(self, edges):
        self._points = ensure([])

    def _shape(self):
        return self._points
    
###############################################################

class Line(Polyline):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, [start, end], style)

    def set(self, start, end):
        self.setPoints([start, end])

    def setStart(self, point):
        self.setPoints([point, self._points[1]])
    
    def setEnd(self, point):
        self.setPoints([self._points[0], point])

class Ray(Line):

    def __init__(self, workspace, start, end, style=pen()):
        super().__init__(workspace, start, end, style)
        self._makeInfity()

    def set(self, start, end):
        super().set(start, end)
        self._makeInfity()

    def setStart(self, point):
        super().setStart(point)
        self._makeInfity()
    
    def setEnd(self, point):
        super().setEnd(point)
        self._makeInfity()

    def _makeInfity(self, big = 1e8):
        p1 = self._points[0]
        p2 = self._points[1]
        u = unit(p2 - p1)
        p2 = p1 + u*big
        p1 = p1 - u*big
        super().set(p1, p2)



###############################################################

class Arrow(Shape):

    def __init__(self, workspace, position, direction, style = brush(), scaling = 1, magnification = 10):
        self._position = ensure(position)
        self._direction = ensure(direction)
        self._scaling = float(scaling)
        self._magnification = float(magnification)
        super().__init__(workspace, style, Transform())

    def setPosition(self, position):
        self._position = ensure(position)
        self._updateTransform()

    def setDirection(self, direction):
        self._direction = ensure(direction)
        self._updateTransform()

    def _make(self):
        self._artist = ArrowPatch(posA=(0.0, 0.0), posB=(0.0, 0.0), arrowstyle='->', mutation_scale=self._magnification)
        self._ax.add_patch(self._artist)
 
    def _updateShape(self, o):
        self._artist.set_positions((o[0,0], o[0,1]), (o[1,0], o[1,1]))

    def _updateStyle(self):
        s = self._style
        if s.fill is not None:
            self._artist.set_facecolor(s.fill.color)
        if s.stroke is not None:
            self._artist.set_edgecolor(s.stroke.color)
            self._artist.set_linewidth(s.stroke.width)
        self._artist.set_alpha(s.opacity)

    def _shape(self):
        return np.array([
                self._position,
                self._position + self._scaling*self._direction
        ])