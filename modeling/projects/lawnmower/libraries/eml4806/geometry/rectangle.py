import numpy as np
from eml4806.geometry.vector import vector, vectors

Vector = np.ndarray

class Rectangle:

    """
    Axis-aligned rectangle defined by:
        _position = bottom-left corner (min x, min y)
        _size     = (width, height)
    """

    __slots__ = ("_position", "_size")

    def __init__(self, position, size):
        self._position = vector(position)
        self._size = vector(size)
        self.normalize()

    # -------------------------------------------------------------------------
    # Mutators
    # -------------------------------------------------------------------------

    def set(self, position, size):
        self._position = vector(position)
        self._size = vector(size)
        self.normalize()
        return self

    # -------------------------------------------------------------------------
    # Position & Size
    # -------------------------------------------------------------------------

    @property
    def position(self) -> Vector:
        return self._position.copy()

    @position.setter
    def position(self, p):
        self._position = vector(p)
        self.normalize()

    @property
    def size(self) -> Vector:
        return self._size.copy()

    @size.setter
    def size(self, s):
        self._size = vector(s)
        self.normalize()

    # -------------------------------------------------------------------------
    # Normalization
    # -------------------------------------------------------------------------

    def normalize(self):
        """Ensure width and height are non-negative."""
        x, y, w, h = self.rectangle()
        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            y = -h
        self._position = vector(x, y)
        self._size = vector(w, h)

    # -------------------------------------------------------------------------
    # Derived values
    # -------------------------------------------------------------------------

    def rectangle(self):
        return self._position[0], self._position[1], self._size[0], self._size[1]
    
    def extent(self):
        x, y, w, h = self.rectangle()
        return [x, x + w, y + h, y]
    
    def vertices(self):
        x, y, w, h = self.rectangle()
        return vectors([[  x, y],
                          [x+w, y],
                          [x+w, y+h],
                          [  x, y+h]])

    def center(self) -> Vector:
        return self._position + 0.5 * self._size

    def setCenter(self, c):
        c = vector(c)
        w, h = self._size
        self._position = vector(c.x - 0.5 * w, c.y - 0.5 * h)
        self.normalize()

    def width(self) -> float:
        return self._size[0]

    def height(self) -> float:
        return self._size[1]

    def area(self) -> float:
        return self._size[0] * self._size[1]

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def contains(self, point) -> bool:
        p = vector(point)
        x, y = self._position
        w, h = self._size
        return (x <= p.x <= x + w and
                y <= p.y <= y + h)

    # -------------------------------------------------------------------------
    # Copy, iteration, representation
    # -------------------------------------------------------------------------

    def copy(self) -> "Rectangle":
        return Rectangle(self._position, self._size)

    def __iter__(self):
        yield vector(self._position)
        yield vector(self._size)

    def __repr__(self):
        return f"Rectangle(position={self._position}, size={self._size})"
       
