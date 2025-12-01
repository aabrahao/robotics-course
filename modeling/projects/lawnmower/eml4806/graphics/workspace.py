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

from eml4806.graphics.map import Map

from eml4806.graphics.style import pen, brush


class Workspace:

    """Convenience wrapper around a Matplotlib axis with shape factories."""

    def __init__(self, x, y, w, h, menu=None, names=None):
        """
        Initialize an interactive workspace.
        x, y : lower-left corner of visible region
        w, h : width and height of visible region
        menu : optional text shown under the title and printed to stdout
        """
        plt.ion()
        self.figure, self.axis = plt.subplots(figsize=(10, 10))
        self.axis.set_xlim(x, x + w)
        self.axis.set_ylim(y, y + h)
        self.axis.set_aspect("equal", adjustable="box")
        self.axis.grid(True)
        # Title
        title = self.title()
        if names:
            title += "\n\n" + ", ".join(names[:-1]) + f", and {names[-1]}"  
        self.figure.suptitle(title)
        # Menu
        if menu:
            menu = ", ".join(menu[:-1]) + f", and {menu[-1]}"  
            self.figure.supxlabel(menu)
            print(menu)
            print()

    def title(self):
        return ("Florida International University\n"
                "EML 4806 Modeling & EML 5808 Robot Control\n"
                "Miami, FL (Fall 2025)")

    def update(self):
        self.figure.canvas.draw_idle()
        self.figure.canvas.flush_events()

    def __del__(self):
        plt.ioff()
        plt.show()

    # Shape collection

    def group(self, shapes):
        return Group(self, shapes)
    
    # Filled shapes (use brush → color)
    
    def rectangle(self, center, size, color="C0", angle: float = 0.0):
        return Rectangle(
            self,
            center=center,
            size=size,
            angle=angle,
            style=brush(color)
        )

    def circle(self, center, radius: float, color="C1"):
        return Circle(
            self,
            center=center,
            radious=radius,
            style=brush(color)
        )

    def polygon(self, points, color="C2"):
        return Polygon(
            self,
            edges=points,
            style=brush(color)
        )

    # Stroked shapes (use pen → color + width)
    
    def polyline(self, points, color="C3", width: float = 1.0, marker=None):
        return Polyline(
            self,
            edges=points,
            style=pen(color=color, width=width),
            marker=marker
        )

    def line(self, start, end, color="C4", width: float = 1.0):
        return Line(
            self,
            start=start,
            end=end,
            style=pen(color=color, width=width)
        )

    def point(self, center, color="C5", width: float = 1.0, marker="o"):
        return Point(
            self,
            center=center,
            style=pen(color=color, width=width)
        )

    def ray(self, start, end, color="C6", width: float = 1.0):
        return Ray(
            self,
            start=start,
            end=end,
            style=pen(color=color, width=width)
        )

    # Arrow (vector visualization)
    
    def arrow(self, origin, direction, color="C0", width: float = 1.0, scaling: float = 1.0, magnification: float = 10.0):
        return Arrow(
            self,
            origin=origin,
            direction=direction,
            style=brush(color, width),
            scaling=scaling,
            magnification=magnification
        )
    
    # Map (image visualization)

    def map(self, position, size, image):
        return Map(self, position, size, image)