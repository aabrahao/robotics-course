import numpy as np

from eml4806.geometry.vector import Vector, toVector

class Line:
    
    """Line segment defined by two Vector objects."""

    __slots__ = ("_p1", "_p2")

    def __init__(self, p1: Vector, p2: Vector):
        self._p1 = toVector(p1)
        self._p2 = toVector(p2)

    # -------------------------------------------------------------------------
    # End point properties
    # -------------------------------------------------------------------------

    @property
    def p1(self) -> Vector:
        """First end point (copy)."""
        return Vector(self._p1)

    @p1.setter
    def p1(self, value: Vector) -> None:
        self._p1 = toVector(value)

    @property
    def p2(self) -> Vector:
        """Second end point (copy)."""
        return Vector(self._p2)

    @p2.setter
    def p2(self, value: Vector) -> None:
        self._p2 = toVector(value)

    def set(self, p1: Vector, p2: Vector):
        """Replace both end points."""
        self._p1 = toVector(p1)
        self._p2 = toVector(p2)
        return self

    # -------------------------------------------------------------------------
    # Basic geometry
    # -------------------------------------------------------------------------

    def dx(self) -> float:
        """Δx = p2.x - p1.x"""
        return self._p2.x - self._p1.x

    def dy(self) -> float:
        """Δy = p2.y - p1.y"""
        return self._p2.y - self._p1.y

    def vector(self) -> Vector:
        """Return the direction vector p2 - p1."""
        return self._p2 - self._p1

    def length(self) -> float:
        """Segment length |p2 - p1|."""
        return self.vector().norm()

    def middle(self) -> Vector:
        """Midpoint of the segment."""
        return (self._p1 + self._p2) * 0.5

    def slope(self, tol: float = 1e-9) -> float | None:
        """Return dy/dx or None if (almost) vertical."""
        dx = self.dx()
        if abs(dx) <= tol:
            return None
        return self.dy() / dx

    # -------------------------------------------------------------------------
    # Transformations
    # -------------------------------------------------------------------------

    def clone(self) -> "Line":
        """Return a copy of this line segment."""
        return Line(self._p1, self._p2)

    # -------------------------------------------------------------------------
    # Parametric + direction
    # -------------------------------------------------------------------------

    def direction(self, tol: float = 1e-9) -> Vector:
        """Return a unit vector along the segment (0,0) if degenerate."""
        v = self.vector()
        n = v.norm()
        if n <= tol:
            return Vector(0.0, 0.0)
        return v / n

    def at(self, t: float) -> Vector:
        """Return parametric point: t=0 → p1, t=1 → p2."""
        v = self.vector()
        return self._p1 + v * t

    # -------------------------------------------------------------------------
    # Geometric helpers (infinite line & segment logic)
    # -------------------------------------------------------------------------

    def intersect(self, other: "Line", tol: float = 1e-9) -> Vector | None:
        """
        Intersection point of two INFINITE lines, or None if (almost) parallel.

        Uses 2D cross product (scalar z-component).
        """
        p = self._p1          # base on line 1
        r = self.vector()     # direction of line 1
        q = other._p1         # base on line 2
        s = other.vector()    # direction of line 2

        r_cross_s = r.cross(s)  # scalar
        if abs(r_cross_s) <= tol:
            # Parallel or coincident (we treat both as 'no unique intersection')
            return None

        qp = q - p
        t = qp.cross(s) / r_cross_s  # parameter along line 1

        return p + r * t

    def coincident(self, p: Vector, tol: float = 1e-9) -> bool:
        """
        Check if a point lies on the infinite line through p1 → p2
        (colinearity test).
        """
        p = toVector(p)
        v1 = p - self._p1       # p - p1
        v2 = self._p2 - self._p1  # p2 - p1
        return abs(v1.cross(v2)) <= tol

    def inside(self, p: Vector, tol: float = 1e-9) -> bool:
        """
        True if point lies on the segment (colinear + between endpoints).
        """
        p = toVector(p)

        # Must be on the infinite line first.
        if not self.coincident(p, tol):
            return False

        v = self.vector()        # p2 - p1
        w = p - self._p1         # p - p1

        dot = v.dot(w)
        if dot < -tol:
            return False

        seg_len2 = v.dot(v)
        return dot <= seg_len2 + tol

    def closest(self, p: Vector, tol: float = 1e-9) -> Vector:
        """
        Closest point on the INFINITE line (through p1 → p2) to point p.
        If the line is degenerate (p1 ≈ p2), returns a copy of p1.
        """
        p = toVector(p)
        v = self.vector()
        seg_len2 = v.dot(v)

        if seg_len2 <= tol:  # degenerate line
            return self.p1

        w = p - self._p1
        t = v.dot(w) / seg_len2
        return self._p1 + v * t

    # -------------------------------------------------------------------------
    # Convenience
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"Line({self._p1!r}, {self._p2!r}, "
            f"length={self.length():.3f}, slope={self.slope()})"
        )

    def __iter__(self):
        """Allow: p1, p2 = line."""
        yield Vector(self._p1)
        yield Vector(self._p2)
