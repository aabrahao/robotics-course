from eml4806.geometry.vector import Vector, toVector


class Line:
    
    """Geometric line segment between two points."""

    __slots__ = ("_start", "_end")

    def __init__(self, start: Vector, end: Vector):
        self._start = toVector(start)
        self._end = toVector(end)

    # -------------------------------------------------------------------------
    # Endpoints
    # -------------------------------------------------------------------------

    @property
    def start(self) -> Vector:
        return Vector(self._start)

    @start.setter
    def start(self, value: Vector) -> None:
        self._start = toVector(value)

    @property
    def end(self) -> Vector:
        return Vector(self._end)

    @end.setter
    def end(self, value: Vector) -> None:
        self._end = toVector(value)

    def set(self, start: Vector, end: Vector):
        self._start = toVector(start)
        self._end = toVector(end)
        return self

    # -------------------------------------------------------------------------
    # Basic geometry
    # -------------------------------------------------------------------------

    def vector(self) -> Vector:
        """Return end - start."""
        return self._end - self._start

    def length(self) -> float:
        return self.vector().norm()

    def direction(self, tol: float = 1e-9) -> Vector:
        """Unit direction or (0,0) if degenerate."""
        v = self.vector()
        n = v.norm()
        if n <= tol:
            return Vector(0.0, 0.0)
        return v / n

    def at(self, t: float) -> Vector:
        """Parametric: t=0 → start, t=1 → end."""
        v = self.vector()
        return self._start + v * t

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def is_degenerate(self, tol: float = 1e-9) -> bool:
        v = self.vector()
        seg_len2 = v.dot(v)
        if seg_len2 <= tol:
            return True
        return False

    # -------------------------------------------------------------------------
    # Geometric relationships
    # -------------------------------------------------------------------------

    def coincident(self, p: Vector, tol: float = 1e-9) -> bool:
        """Check if a point lies on the infinite line."""
        p = toVector(p)
        v = self.vector()
        seg_len2 = v.dot(v)
        if seg_len2 <= tol:
            dist = (p - self._start).norm()
            if dist <= tol:
                return True
            return False
        v1 = p - self._start
        cross_val = v1.cross(v)
        if abs(cross_val) <= tol:
            return True
        return False

    def inside(self, p: Vector, tol: float = 1e-9) -> bool:
        """Check if a point lies on the finite segment."""
        p = toVector(p)
        v = self.vector()
        seg_len2 = v.dot(v)
        if seg_len2 <= tol:
            dist = (p - self._start).norm()
            if dist <= tol:
                return True
            return False
        is_on_line = self.coincident(p, tol=tol)
        if not is_on_line:
            return False
        w = p - self._start
        dot = v.dot(w)
        if dot < -tol:
            return False
        if dot > seg_len2 + tol:
            return False
        return True

    def contains(self, p: Vector, infinity_line: bool = False, tol: float = 1e-9) -> bool:
        """Segment containment (default) or infinite-line containment."""
        if infinity_line:
            return self.coincident(p, tol=tol)
        return self.inside(p, tol=tol)

    def closest(self, p: Vector, infinity_line: bool = True, tol: float = 1e-9) -> Vector:
        """Closest point on the infinite line (default) or on the segment."""
        p = toVector(p)
        v = self.vector()
        seg_len2 = v.dot(v)
        if seg_len2 <= tol:
            return self.start
        w = p - self._start
        t = v.dot(w) / seg_len2
        if infinity_line:
            t_clamped = t
        else:
            t_clamped = t
            if t_clamped < 0.0:
                t_clamped = 0.0
            if t_clamped > 1.0:
                t_clamped = 1.0
        return self._start + v * t_clamped

    def intersect(self, other: "Line", infinity_line: bool = True, tol: float = 1e-9) -> Vector | None:
        """Intersection on infinite lines or on finite segments."""
        p = self._start
        r = self.vector()
        q = other._start
        s = other.vector()

        r_len2 = r.dot(r)
        s_len2 = s.dot(s)
        
        # Case 1 — Both segments are degenerate (points)
        if r_len2 <= tol and s_len2 <= tol:
            pq = p - q
            dist = pq.norm()
            if dist <= tol:
                return self.start
            return None

        # Case 2 — Only self is a point
        if r_len2 <= tol:
            self_point = self.start
            if infinity_line:
                on_other_line = other.coincident(self_point, tol=tol)
                if on_other_line:
                    return self_point
                return None
            on_other_segment = other.inside(self_point, tol=tol)
            if on_other_segment:
                return self_point
            return None

        # Case 3 — Only other is a point
        if s_len2 <= tol:
            other_point = other.start
            if infinity_line:
                on_self_line = self.coincident(other_point, tol=tol)
                if on_self_line:
                    return other_point
                return None
            on_self_segment = self.inside(other_point, tol=tol)
            if on_self_segment:
                return other_point
            return None

        # Case 4 — Proper line–line intersection
        rxs = r.cross(s)
        if abs(rxs) <= tol:
            return None
        qp = q - p
        t = qp.cross(s) / rxs
        u = qp.cross(r) / rxs
        if infinity_line:
            intersection_point = p + r * t
            return intersection_point
        t_ok = -tol <= t <= 1.0 + tol
        u_ok = -tol <= u <= 1.0 + tol
        if not t_ok:
            return None
        if not u_ok:
            return None
        intersection_point = p + r * t
        return intersection_point

    # -------------------------------------------------------------------------
    # Convenience
    # -------------------------------------------------------------------------

    def clone(self) -> "Line":
        return Line(self._start, self._end)

    def __repr__(self):
        return f"Line({self._start!r}, {self._end!r})"

    def __iter__(self):
        yield Vector(self._start)
        yield Vector(self._end)
