import numpy as np
import matplotlib.pyplot as plt

from eml4806.graphics.shape import GroupShape as Group

from eml4806.graphics.shape import RectangleShape as Rectangle
from eml4806.graphics.shape import CircleShape as Circle

from eml4806.graphics.shape import PointShape as Point
from eml4806.graphics.shape import LineShape as Line
from eml4806.graphics.shape import RayShape as Ray

from eml4806.graphics.shape import PolylineShape as Polyline
from eml4806.graphics.shape import PolygonShape as Polygon

from eml4806.graphics.shape import ArrowShape as Arrow

from eml4806.graphics.map import RasterMap

from eml4806.graphics.style import pen, brush

Vector = np.ndarray   # (,3)
Vectors = np.ndarray  # (N,3)

class Workspace:

    """Convenience wrapper around a Matplotlib _ax with shape factories."""

    __slots__ = ('_figure', '_ax' )

    def __init__(self, x: float, y: float, w: float, h: float, menu=None, names=None):
        """
        Initialize an interactive workspace.
        x, y : lower-left corner of visible region
        w, h : width and height of visible region
        menu : optional text shown under the title and printed to stdout
        """
        plt.ion()
        self._figure, self._ax = plt.subplots(figsize=(10, 10))
        self._ax.set_xlim(x, x + w)
        self._ax.set_ylim(y, y + h)
        self._ax.set_aspect("equal", adjustable="box")
        self._ax.grid(True)
        self._ax.set_autoscale_on(False)
        # Title
        title = self.title()
        if names:
            title += "\n\n" + ", ".join(names[:-1]) + f", and {names[-1]}"  
        self._figure.suptitle(title)
        # Menu
        if menu:
            menu = ", ".join(menu[:-1]) + f", and {menu[-1]}"  
            self._figure.supxlabel(menu)
            print(menu)
            print()

    def viewport(self):
        """Actual artist rectangle"""
        xmin, xmax = self._ax.get_xlim()
        ymin, ymax = self._ax.get_ylim()
        return xmin, ymin, xmax-xmin, ymax-ymin

    def title(self):
        return ("Florida International University\n"
                "EML 4806 Modeling & EML 5808 Robot Control\n"
                "Miami, FL (Fall 2025)")

    def update(self):
        self._figure.canvas.draw_idle()
        self._figure.canvas.flush_events()

    def __del__(self):
        plt.ioff()
        plt.show()

    # Shape collection

    def group(self, shapes):
        return Group(self, shapes)
    
    # Filled shapes (use brush → color)
    
    def rectangle(self, center: Vector, size: Vector, *, color="C0", angle: float = 0.0):
        return Rectangle(
            self,
            center=center,
            size=size,
            angle=angle,
            style=brush(color=color)
        )

    def circle(self, center: Vector, radius: float, *, color="C1"):
        return Circle(
            self,
            center=center,
            radius=radius,
            style=brush(color=color)
        )

    def polygon(self, points: Vectors, *, color="C2"):
        return Polygon(
            self,
            edges=points,
            style=brush(color=color)
        )

    # Stroked shapes (use pen → color + width)
    
    def polyline(self, points: Vectors, *, color="C3", width: float = 1.0, marker=None, closed=False):
        return Polyline(
            self,
            edges=points,
            style=pen(color=color, width=width),
            marker=marker,
            closed=closed
        )

    def line(self, start: Vector, end: Vector, *, color="C4", width: float = 1.0):
        return Line(
            self,
            start=start,
            end=end,
            style=pen(color=color, width=width)
        )

    def point(self, center: Vector, *, color="C5", width: float = 1.0, marker="o"):
        return Point(
            self,
            center=center,
            style=pen(color=color, width=width)
        )

    def ray(self, start: Vector, end: Vector, *, color="C6", width: float = 1.0):
        return Ray(
            self,
            start=start,
            end=end,
            style=pen(color=color, width=width)
        )

    # Arrow (vector visualization)
    
    def arrow(self, origin: Vector, direction: Vector, *, color="C0", width: float = 0.0, scaling: float = 1.0):
        return Arrow(
            self,
            origin=origin,
            direction=direction,
            style=brush(color=color, stroke_width=width),
            scaling=scaling
        )
    
    # Map (image visualization)

    def map(self, position=None, size=None, image=None, *, pixels=500):
        return RasterMap(self, position, size, image, pixels)
 
