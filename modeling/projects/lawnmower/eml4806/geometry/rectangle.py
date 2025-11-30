import numpy as np

from eml4806.geometry.vector import Vector, toVector, toVectors

class Rectangle:

    """Axis-aligned rectangle defined by two corners p1 (bottom-left) and p2 (top-right)."""

    __slots__ = ("_p1", "_p2")

    def __init__(self, origin, size, centered: bool = False):
        '''Centered only reagene p1 and p2'''
        origin = toVector(origin)
        size = toVector(size)
        x, y = origin
        w, h = size
        if not centered:  
            p1 = Vector(x, y)
            p2 = Vector(x + w, y + h)
        else:  # origin = center
            p1 = Vector(x - 0.5*w, y - 0.5*h)
            p2 = Vector(y + 0.5*w, y + 0.5*h)
        self._p1 = p1
        self._p2 = p2
        self.normalize()

    def set(self, p1: Vector, p2: Vector):
        self._p1 = p1.copy()
        self._p2 = p2.copy()
        self.normalize()

    # p1 and p2 properties

    @property
    def p1(self) -> Vector:
        return self._p1

    @p1.setter
    def p1(self, p: Vector):
        self._p1 = p.copy()
        self.normalize()

    @property
    def p2(self) -> Vector:
        return self._p2

    @p2.setter
    def p2(self, p: Vector):
        self._p2 = p.copy()
        self.normalize()

    # Normalize such that:
    #  p1 = (left, bottom)
    #  p2 = (right, top)
    
    def normalize(self):
        x1, y1 = self._p1
        x2, y2 = self._p2
        self._p1.x = min(x1, x2)
        self._p1.y = min(y1, y2)
        self._p2.x = max(x1, x2)
        self._p2.y = max(y1, y2)

    def center(self) -> Vector:
        return 0.5*(self._p1 + self._p2)

    def setCenter(self, p: Vector):
        """Move rectangle so its center becomes (x, y)."""
        s = 0.5*self.size()
        self.p1 = p - s
        self.p2 = p + s
        self.normalize()
    
    # Dimensions
    
    def width(self):
        return self._p2.x - self._p1.x

    def height(self):
        return self._p2.y - self._p1.y

    def size(self):
        return Vector(self.width(), self.height())

    def area(self):
        return self.width() * self.height()

    # Tests
    
    def contains(self, p: Vector) -> bool:
        return (self._p1.x <= p.x <= self._p2.x and
                self._p1.y <= p.y <= self._p2.y)
    
    # Copy

    def copy(self):
        return Rectangle(self._p1, self.size(), centered=False)

    # Representation & iteration

    def __iter__(self):
        yield self._p1
        yield self._p2

    def __repr__(self):
        return f"Rectangle({self._p1}, {self._p2})"
