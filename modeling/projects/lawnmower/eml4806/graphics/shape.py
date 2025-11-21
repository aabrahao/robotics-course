import math
import numpy as np
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch as ArrowPatch

from eml4806.geometry.vector import vector, ensure, append
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

    def move(self, x, y, relative=False):
        if relative:
            self._transform.position += (x, y)
        else:
            self._transform.position = (x, y)
        self._updateTransform()

    def rotate(self, angle, relative=False):
        if relative:
            self._transform.orientation += float(angle)
        else:
            self._transform.orientation = float(angle)
        self._updateTransform()

    def scale(self, sx, sy=None, relative=False):
        if sy is None:
            sy = sx
        if relative:
            self._transform.scale += (sx, sy)
        else:
            self._transform.scale = (sx, sy)
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
        if self._parent is None:
            T = self._transform
        else:
            T = Transform.compound(self._parent._transform, self._transform)
        o = T.apply(self._shape())
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
        self, workspace, x, y, width, height, angle=0.0, style=brush()
    ):
        self.w = width
        self.h = height
        super().__init__(workspace, style, Transform(position=(x, y), orientation=angle))

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

    def __init__(self, workspace, x, y, radious, style=brush()):
        self.r = radious
        super().__init__(workspace, style, Transform(position=(x, y)))

    def _shape(self):
        a = np.linspace(0.0, 2 * np.pi, 72, endpoint=False)
        x = self.r * np.cos(a)
        y = self.r * np.sin(a)
        return vector(x, y)


###############################################################

class Polygon(Fill):

    def __init__(self, workspace, edges, style=brush()):
        self._points = ensure(edges)
        super().__init__(workspace, style)

    def points(self):
        return self._points.copy()
    
    def setPoints(self, points):
        self._parent = ensure(points)
    
    def append(self, edges):
        self._points = np.vstack([self._points, edges.ensure()])

    def _shape(self):
        return self._points

###############################################################

class Polyline(Plot):

    def __init__(self, workspace, edges=[], style=pen()):
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

class Arrow(Shape):

    def __init__(self, workspace, x, y, dx, dy, style = brush(), scaling = 1):
        self._x = float(x)
        self._y = float(y)
        self._dx = float(dx)
        self._dy = float(dy)
        self._scaling = float(scaling)
        super().__init__(workspace, style, Transform())

    def setPosition(self, x, y):
        self._x = x
        self._y = y
        self._updateTransform()

    def setSize(self, dx, dy):
        self._dx = dx
        self._dy = dy
        self._updateTransform()

    def _make(self):
        self._artist = ArrowPatch(posA=(0.0, 0.0), posB=(0.0, 0.0), arrowstyle='->', mutation_scale=self._scaling)
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
                [self._x, self._y],
                [self._x + self._scaling*self._dx, self._y + self._scaling*self._dy]
            ]
        )