from eml4806.geometry.vector import Vector, toVector, toVectors

class Rectangle:

    """
    Axis-aligned rectangle defined by:
        _position = bottom-left corner (min x, min y)
        _size     = (width, height)
    """

    __slots__ = ("_position", "_size")

    def __init__(self, position, size):
        self._position = toVector(position)
        self._size = toVector(size)
        self.normalize()

    # -------------------------------------------------------------------------
    # Mutators
    # -------------------------------------------------------------------------

    def set(self, position, size):
        self._position = toVector(position)
        self._size = toVector(size)
        self.normalize()
        return self

    # -------------------------------------------------------------------------
    # Position & Size
    # -------------------------------------------------------------------------

    @property
    def position(self) -> Vector:
        return Vector(self._position)   # return a copy

    @position.setter
    def position(self, p):
        self._position = toVector(p)
        self.normalize()

    @property
    def size(self) -> Vector:
        return Vector(self._size)       # return a copy

    @size.setter
    def size(self, s):
        self._size = toVector(s)
        self.normalize()

    # -------------------------------------------------------------------------
    # Normalization
    # -------------------------------------------------------------------------

    def normalize(self):
        """Ensure width and height are non-negative."""
        if self._size.x < 0:
            self._position.x += self._size.x
            self._size.x = -self._size.x

        if self._size.y < 0:
            self._position.y += self._size.y
            self._size.y = -self._size.y

    # -------------------------------------------------------------------------
    # Derived values
    # -------------------------------------------------------------------------

    def rectangle(self):
        x, y = self.position
        w, h = self.size
        return x, y, w, h
    
    def extent(self):
        x, y, w, h = self.rectangle()
        return [x, x + w, y + h, y]
    
    def vertices(self):
        x, y, w, h = self.rectangle()
        return toVectors([[  x, y],
                          [x+w, y],
                          [x+w, y+h],
                          [  x, y+h]])

    def center(self) -> Vector:
        return self._position + 0.5 * self._size

    def setCenter(self, c):
        c = toVector(c)
        w, h = self._size
        self._position = Vector(c.x - 0.5 * w, c.y - 0.5 * h)
        self.normalize()

    def width(self) -> float:
        return self._size.x

    def height(self) -> float:
        return self._size.y

    def area(self) -> float:
        return self._size.x * self._size.y

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def contains(self, point) -> bool:
        p = toVector(point)
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
        yield Vector(self._position)
        yield Vector(self._size)

    def __repr__(self):
        return f"Rectangle(position={self._position}, size={self._size})"
       
