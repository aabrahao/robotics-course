import numpy as np
from eml4806.geometry.vector import Vector, toVector

class Line:
    """Line segment defined by two Vector objects."""

    __slots__ = ("_start", "_end")

    def __init__(self, start: Vector, end: Vector):
        self._start = toVector(start)
        self._end   = toVector(end)

    # -------------------------------------------------------------------------
    # End point properties
    # -------------------------------------------------------------------------

    @property
    def start(self) -> Vector:
        """First end point (copy)."""
        return Vector(self._start)

    @start.setter
    def start(self, value: Vector) -> None:
        self._start = toVector(value)

    @property
    def end(self) -> Vector:
        """Second end point (copy)."""
        return Vector(self._end)

    @end.setter
    def end(self, value: Vector) -> None:
        self._end = toVector(value)

    def set(self, start: Vector, end: Vector):
        """Replace both end points."""
        self._start = toVector(start)
        self._end   = toVector(end)
        return self

    # -------------------------------------------------------------------------
    # Basic geometry
    # -------------------------------------------------------------------------

    def dx(self) -> float:
        """Δx = end.x - start.x"""
        return self._end.x - self._start.x

    def dy(self) -> float:
        """Δy = end.y - start.y"""
        return self._end.y - self._start.y

    def vector(self) -> Vector:
        """Return the direction vector end - start."""
        return self._end - self._start

    def length(self) -> float:
        """Segment length |end - start|."""
        return self.vector().norm()

    def middle(self) -> Vector:
        """Midpoint of the segment."""
        return (self._start + self._end) * 0.5

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
        return Line(self._start, self._end)

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
        """Return parametric point: t=0 → start, t=1 → end."""
        v = self.vector()
        return self._start + v * t

    # -------------------------------------------------------------------------
    # Geometric helpers (infinite line & segment logic)
    # -------------------------------------------------------------------------

    def intersect(self, other: "Line", tol: float = 1e-9) -> Vector | None:
        """
        Intersection point of two INFINITE lines, or None if (almost) parallel.
        """
        p = self._start            # base on line 1
        r = self.vector()          # direction of line 1
        q = other._start           # base on line 2
        s = other.vector()         # direction of line 2

        r_cross_s = r.cross(s)
        if abs(r_cross_s) <= tol:
            return None

        qp = q - p
        t = qp.cross(s) / r_cross_s
        return p + r * t

    def coincident(self, p: Vector, tol: float = 1e-9) -> bool:
        """Check if a point lies on the infinite line through start → end."""
        p = toVector(p)
        v1 = p - self._start         # p - start
        v2 = self._end - self._start # end - start
        return abs(v1.cross(v2)) <= tol

    def inside(self, p: Vector, tol: float = 1e-9) -> bool:
        """True if point lies on the segment (colinear + between endpoints)."""
        p = toVector(p)

        if not self.coincident(p, tol):
            return False

        v = self.vector()          # end - start
        w = p - self._start        # p - start

        dot = v.dot(w)
        if dot < -tol:
            return False

        seg_len2 = v.dot(v)
        return dot <= seg_len2 + tol

    def closest(self, p: Vector, tol: float = 1e-9) -> Vector:
        """
        Closest point on the INFINITE line (through start → end) to point p.
        If the line is degenerate (start ≈ end), returns a copy of start.
        """
        p = toVector(p)
        v = self.vector()
        seg_len2 = v.dot(v)

        if seg_len2 <= tol:  # degenerate line
            return self.start  # property, returns a copy

        w = p - self._start
        t = v.dot(w) / seg_len2
        return self._start + v * t

    # -------------------------------------------------------------------------
    # Convenience
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"Line({self._start!r}, {self._end!r}, "
            f"length={self.length():.3f}, slope={self.slope()})"
        )

    def __iter__(self):
        """Allow: start, end = line."""
        yield Vector(self._start)
        yield Vector(self._end)
