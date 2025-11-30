from eml4806.geometry.vector import Vector, toVector

class Circle:

    """
    Geometric circle defined by:
        _center : Vector
        _radius : float (>= 0)
    """

    __slots__ = ("_center", "_radius")

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------

    def __init__(self, center, radius: float):
        self._center = toVector(center)
        self._radius = float(radius)
        if self._radius < 0:
            raise ValueError("Radius must be non-negative")

    # -------------------------------------------------------------------------
    # Core getters / setters
    # -------------------------------------------------------------------------

    @property
    def center(self) -> Vector:
        """Return the center as a copy."""
        return Vector(self._center)

    @center.setter
    def center(self, c):
        self._center = toVector(c)

    @property
    def radius(self) -> float:
        """Return the radius."""
        return float(self._radius)

    @radius.setter
    def radius(self, r: float):
        r = float(r)
        if r < 0:
            raise ValueError("Radius must be non-negative")
        self._radius = r

    # -------------------------------------------------------------------------
    # Derived geometric values
    # -------------------------------------------------------------------------

    def diameter(self) -> float:
        return 2.0 * self._radius

    def area(self) -> float:
        return 3.141592653589793 * self._radius * self._radius

    def perimeter(self) -> float:
        return 2.0 * 3.141592653589793 * self._radius

    # -------------------------------------------------------------------------
    # Transform-like operations
    # -------------------------------------------------------------------------

    def move(self, v):
        """Translate the circle by a vector-like displacement."""
        self._center = self._center + toVector(v)
        return self

    def setCenter(self, c):
        """Set the center (vector-like)."""
        self._center = toVector(c)
        return self

    def setRadius(self, r):
        """Set the radius."""
        self.radius = r
        return self

    # -------------------------------------------------------------------------
    # Geometric tests
    # -------------------------------------------------------------------------

    def contains(self, p) -> bool:
        """
        True if point p (vector-like) lies inside or on the circle.
        """
        p = toVector(p)
        return (p - self._center).norm() <= self._radius

    def distanceToCenter(self, p) -> float:
        """Euclidean distance from the circle's center to p."""
        p = toVector(p)
        return (p - self._center).norm()

    def distanceToBoundary(self, p) -> float:
        """
        Signed distance from point p to the circle boundary:
            negative → inside
            zero     → on boundary
            positive → outside
        """
        return self.distanceToCenter(p) - self._radius

    def intersects(self, other: "Circle") -> bool:
        """
        True if two circles intersect (touch or overlap).
        """
        if not isinstance(other, Circle):
            raise TypeError("Expected a Circle")

        d = (other._center - self._center).norm()
        return d <= (self._radius + other._radius)

    def intersectionType(self, other: "Circle") -> str:
        """
        Classification of circle-circle relation:
          - 'separate'
          - 'externally tangent'
          - 'overlapping'
          - 'internally tangent'
          - 'inside' (one inside the other)
        """
        d = (other._center - self._center).norm()
        r1 = self._radius
        r2 = other._radius

        if d > r1 + r2:
            return "separate"
        if abs(d - (r1 + r2)) < 1e-9:
            return "externally tangent"
        if abs(d - abs(r1 - r2)) < 1e-9:
            return "internally tangent"
        if d < abs(r1 - r2):
            return "inside"
        return "overlapping"

    # -------------------------------------------------------------------------
    # Copy and representation
    # -------------------------------------------------------------------------

    def copy(self) -> "Circle":
        """Return a copy of this circle."""
        return Circle(self._center, self._radius)

    def __iter__(self):
        """Allow: center, radius = circle."""
        yield Vector(self._center)
        yield float(self._radius)

    def __repr__(self):
        return f"Circle(center={self._center}, radius={self._radius})"
