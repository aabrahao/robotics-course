from eml4806.geometry.vector import Vector, toVector


class Rectangle:
    """
    Axis-aligned rectangle defined by two corners:
        _p1 = bottom-left  (min x, min y)
        _p2 = top-right    (max x, max y)
    """

    __slots__ = ("_p1", "_p2")

    def __init__(self, origin, size, centered: bool = False):
        """
        origin: Vector-like
            If centered=False: bottom-left corner of the rectangle.
            If centered=True:  center of the rectangle.
        size: Vector-like (width, height)
        """
        origin = toVector(origin)
        size = toVector(size)
        x, y = origin
        w, h = size

        if not centered:
            p1 = Vector(x, y)
            p2 = Vector(x + w, y + h)
        else:
            # origin = center
            p1 = Vector(x - 0.5 * w, y - 0.5 * h)
            p2 = Vector(x + 0.5 * w, y + 0.5 * h)

        self._p1 = p1
        self._p2 = p2
        self.normalize()

    # -------------------------------------------------------------------------
    # Mutators
    # -------------------------------------------------------------------------

    def set(self, p1, p2):
        """Set corners from any two vector-like objects."""
        self._p1 = toVector(p1)
        self._p2 = toVector(p2)
        self.normalize()
        return self

    # -------------------------------------------------------------------------
    # Corner properties
    # -------------------------------------------------------------------------

    @property
    def p1(self) -> Vector:
        """Bottom-left corner (copy)."""
        return Vector(self._p1)

    @p1.setter
    def p1(self, p):
        self._p1 = toVector(p)
        self.normalize()

    @property
    def p2(self) -> Vector:
        """Top-right corner (copy)."""
        return Vector(self._p2)

    @p2.setter
    def p2(self, p):
        self._p2 = toVector(p)
        self.normalize()

    # -------------------------------------------------------------------------
    # Normalization
    # -------------------------------------------------------------------------

    def normalize(self):
        """
        Ensure:
            _p1 = (min x, min y)
            _p2 = (max x, max y)
        """
        x1, y1 = self._p1
        x2, y2 = self._p2
        self._p1.x = min(x1, x2)
        self._p1.y = min(y1, y2)
        self._p2.x = max(x1, x2)
        self._p2.y = max(y1, y2)

    # -------------------------------------------------------------------------
    # Derived points
    # -------------------------------------------------------------------------

    def center(self) -> Vector:
        """Return the center of the rectangle."""
        return (self._p1 + self._p2) * 0.5

    def setCenter(self, p):
        """Move rectangle so its center becomes p (vector-like)."""
        c = toVector(p)
        half_size = 0.5 * self.size()
        self.p1 = c - half_size
        self.p2 = c + half_size
        # setter already normalizes

    # -------------------------------------------------------------------------
    # Dimensions
    # -------------------------------------------------------------------------

    def width(self) -> float:
        return self._p2.x - self._p1.x

    def height(self) -> float:
        return self._p2.y - self._p1.y

    def size(self) -> Vector:
        """Return (width, height) as a Vector."""
        return Vector(self.width(), self.height())

    def area(self) -> float:
        return self.width() * self.height()

    # -------------------------------------------------------------------------
    # Tests
    # -------------------------------------------------------------------------

    def contains(self, p) -> bool:
        """
        True if a point p (vector-like) lies inside or on the boundary
        of the rectangle.
        """
        p = toVector(p)
        return (self._p1.x <= p.x <= self._p2.x and
                self._p1.y <= p.y <= self._p2.y)

    # -------------------------------------------------------------------------
    # Copy / iteration / representation
    # -------------------------------------------------------------------------

    def copy(self) -> "Rectangle":
        """Return a copy of this rectangle."""
        return Rectangle(self._p1, self.size(), centered=False)

    def __iter__(self):
        """Allow: p1, p2 = rect."""
        yield Vector(self._p1)
        yield Vector(self._p2)

    def __repr__(self):
        return f"Rectangle({self._p1}, {self._p2})"
