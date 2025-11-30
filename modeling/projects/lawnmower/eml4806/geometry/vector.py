from __future__ import annotations
from typing import Union, Iterable

import numpy as np
import math

Number = Union[int, float]

class Vector:
    """
    Strict 2D float vector (x, y) behaving like a mathematical vector.
    Fully interoperable with NumPy.

    Valid constructors:
        Vector()                -> (0.0, 0.0)
        Vector(x, y)            -> two numeric scalars
        Vector([x, y])          -> sequence of length 2
        Vector((x, y))
        Vector(np.array([x, y]))
        Vector(other_vector)
        Vector(point_like)      -> object with numeric .x and .y

    Invalid:
        Vector(0)
        Vector(1)
        Vector([1])
        Vector([])
        Vector(None)
    """

    __slots__ = ("_data",)

    # ---------------------------
    # CONSTRUCTOR
    # ---------------------------

    def __init__(self, *args):
        # CASE 0: Vector() -> zero vector
        if len(args) == 0:
            self._data = np.array([0.0, 0.0], dtype=float)
            return
        # CASE 1: Vector(x, y)
        if len(args) == 2:
            x, y = args
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise TypeError("Vector(x, y) requires numeric values")
            self._data = np.array([float(x), float(y)], dtype=float)
            return
        # CASE 2: Vector(arg)
        if len(args) == 1:
            arg = args[0]
            if arg is None:
                raise TypeError("Vector(None) is not allowed")
            # Vector(existing Vector)
            if isinstance(arg, Vector):
                self._data = np.array([arg.x, arg.y], dtype=float)
                return
            # Vector(point_like)
            if hasattr(arg, "x") and hasattr(arg, "y"):
                xv, yv = arg.x, arg.y
                if isinstance(xv, (int, float)) and isinstance(yv, (int, float)):
                    self._data = np.array([float(xv), float(yv)], dtype=float)
                    return
                raise TypeError("Point-like object must have numeric x and y")
            # Vector(sequence of length 2)
            if isinstance(arg, Iterable) and not isinstance(arg, (str, bytes)):
                vals = list(arg)
                if len(vals) != 2:
                    raise ValueError("Iterable must have exactly 2 numeric values")
                if not all(isinstance(v, (int, float)) for v in vals):
                    raise TypeError("Iterable values must be numeric")
                self._data = np.array([float(vals[0]), float(vals[1])], dtype=float)
                return
            # Single numeric NOT allowed
            if isinstance(arg, (int, float)):
                raise TypeError("Vector(x) with a single numeric is not allowed")
            raise TypeError("Invalid argument for Vector constructor")
        raise TypeError("Vector constructor takes 0, 1, or 2 arguments")

    # ---------------------------
    # INTERNAL HELPER
    # ---------------------------

    @staticmethod
    def _to_vector(other) -> "Vector":
        """Convert any vector-like object into a Vector."""
        if isinstance(other, Vector):
            return other
        if hasattr(other, "x") and hasattr(other, "y"):
            xv, yv = other.x, other.y
            if isinstance(xv, (int, float)) and isinstance(yv, (int, float)):
                return Vector(xv, yv)
        if isinstance(other, Iterable) and not isinstance(other, (str, bytes)):
            vals = list(other)
            if len(vals) == 2 and all(isinstance(v, (int, float)) for v in vals):
                return Vector(vals[0], vals[1])
        if isinstance(other, (int, float)):
            raise TypeError("Single numeric value cannot be converted to Vector")
        raise TypeError(f"Cannot convert {other!r} to Vector")

    # ---------------------------
    # UNPACKING SUPPORT
    # ---------------------------

    def __iter__(self):
        yield self.x
        yield self.y

    # ---------------------------
    # PROPERTIES
    # ---------------------------

    @property
    def x(self) -> float:
        return float(self._data[0])

    @x.setter
    def x(self, value: Number):
        if not isinstance(value, (int, float)):
            raise TypeError("x must be numeric")
        self._data[0] = float(value)

    @property
    def y(self) -> float:
        return float(self._data[1])

    @y.setter
    def y(self, value: Number):
        if not isinstance(value, (int, float)):
            raise TypeError("y must be numeric")
        self._data[1] = float(value)

    @property
    def data(self) -> np.ndarray:
        return self._data

    # ---------------------------
    # NUMPY INTEROPERABILITY
    # ---------------------------

    __array_priority__ = 100.0

    def __array__(self, dtype=None):
        return np.asarray(self._data, dtype=dtype)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        raw = [v._data if isinstance(v, Vector) else v for v in inputs]
        result = getattr(ufunc, method)(*raw, **kwargs)

        if isinstance(result, np.ndarray) and result.ndim == 1 and result.size == 2:
            return Vector(result[0], result[1])

        if isinstance(result, tuple):
            return tuple(
                Vector(r[0], r[1])
                if isinstance(r, np.ndarray) and r.ndim == 1 and r.size == 2
                else r
                for r in result
            )

        return result

    # ---------------------------
    # ARITHMETIC
    # ---------------------------
    
    def __add__(self, other):
        try:
            v = self._to_vector(other)
        except TypeError:
            return NotImplemented
        r = self._data + v._data
        return Vector(r[0], r[1])

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        try:
            v = self._to_vector(other)
        except TypeError:
            return NotImplemented
        r = self._data - v._data
        return Vector(r[0], r[1])

    def __rsub__(self, other):
        v = self._to_vector(other)
        r = v._data - self._data
        return Vector(r[0], r[1])

    def __mul__(self, scalar: Number):
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        r = self._data * float(scalar)
        return Vector(r[0], r[1])

    __rmul__ = __mul__

    def __truediv__(self, scalar: Number):
        if not isinstance(scalar, (int, float)):
            raise TypeError("Scalar must be numeric")
        r = self._data / float(scalar)
        return Vector(r[0], r[1])

    # ---------------------------
    # VECTOR MATH
    # ---------------------------

    def dot(self, other: "Vector") -> float:
        if not isinstance(other, Vector):
            raise TypeError("dot() requires a Vector")
        return float(self._data @ other._data)

    def cross(self, other: "Vector") -> float:
        if not isinstance(other, Vector):
            raise TypeError("cross() requires a Vector")
        return float(self.x * other.y - self.y * other.x)

    def norm(self) -> float:
        return float(np.linalg.norm(self._data))

    def normalized(self) -> "Vector":
        n = self.norm()
        if n == 0:
           return self
        return self / n

    # ---------------------------
    # NEW MATHEMATICAL OPERATORS
    # ---------------------------
    
    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __eq__(self, other):
        try:
            v = self._to_vector(other)
        except TypeError:
            return False
        return self.x == v.x and self.y == v.y

    def __abs__(self):
        """abs(v) == v.norm()"""
        return self.norm()

    # ---------------------------
    # REPR
    # ---------------------------
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


# -----------------------------------------------------------------------------
# INTERNAL: type enforcement
# -----------------------------------------------------------------------------

def toVector(v) -> Vector:
    """Convert any vector-like object into a Vector or raise TypeError."""
    try:
        return Vector._to_vector(v)
    except Exception:
        raise TypeError(f"Expected a Vector-like object, got {v!r}")

def toVectors(obj):
    """
    Convert a single vector-like object or an iterable of such objects
    into a list of Vector instances.
    Examples:
        toVectors((1,2))              -> [Vector(1,2)]
        toVectors([ (1,2), (3,4) ])   -> [Vector(1,2), Vector(3,4)]
        toVectors(Vector(1,2))        -> [Vector(1,2)]
    """
    # Single object
    if not isinstance(obj, (list, tuple)):
        return [toVector(obj)]
    # Iterable of objects
    return [toVector(o) for o in obj]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def split(points):
    """
    Convert a list of Vector-like objects into two NumPy arrays (x, y).
    Input:
        [Vector, (x,y), [x,y], ...]
    Returns:
        xs, ys   (NumPy arrays)
    """
    pts = [toVector(p) for p in points]
    xs = np.array([p.x for p in pts], dtype=float)
    ys = np.array([p.y for p in pts], dtype=float)
    return xs, ys

def join(xs, ys):
    """
    Convert x and y sequences into a list of Vector objects.
    Input:
        xs, ys  (same length)
        xs[i], ys[i] form Vector(xs[i], ys[i])
    Returns:
        list[Vector]
    """
    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")
    return [Vector(x, y) for x, y in zip(xs, ys)]

# -----------------------------------------------------------------------------
# BASIC GEOMETRIC OPERATIONS
# -----------------------------------------------------------------------------

def length(v):
    """Return the Euclidean norm of vector v."""
    v = toVector(v)
    return v.norm()

def distance(v1, v2):
    """Return the Euclidean distance between v1 and v2."""
    v1, v2 = toVector(v1), toVector(v2)
    return (v1 - v2).norm()

def angle(v1, v2=None):
    """Compute the absolute angle of v1 or the signed angle from v1 to v2."""
    v1 = toVector(v1)
    if v2 is None:
        return math.atan2(v1.y, v1.x)
    v2 = toVector(v2)
    return math.atan2(cross(v1, v2), dot(v1, v2))

def coincident(v1, v2, tol: float = 1e-2):
    """Return True if v1 and v2 are within tol distance."""
    v1, v2 = toVector(v1), toVector(v2)
    dx = v1.x - v2.x
    dy = v1.y - v2.y
    return dx * dx + dy * dy <= tol * tol

def unit(v):
    """Return the unit (normalized) vector in the same direction as v."""
    v = toVector(v)
    return v.normalized()

def perpendicular(v, clockwise=False):
    """Return a perpendicular vector to v (clockwise or counterclockwise)."""
    v = toVector(v)
    if clockwise:
        return Vector(v.y, -v.x)
    return Vector(-v.y, v.x)

def dot(v1, v2):
    return v1.dot(v2)

def cross(v1, v2):
    return v1.cross(v2)

# -----------------------------------------------------------------------------
# VECTOR ALGEBRA
# -----------------------------------------------------------------------------

def dot(v1, v2):
    """Return the dot product v1 · v2."""
    v1, v2 = toVector(v1), toVector(v2)
    return v1.dot(v2)

def cross(v1, v2):
    """Return the 2D scalar cross product (z-component)."""
    v1, v2 = toVector(v1), toVector(v2)
    return v1.cross(v2)

def is_zero(v, tol: float = 1e-9):
    """Return True if |v| <= tol."""
    v = toVector(v)
    return v.norm() <= tol

# -----------------------------------------------------------------------------
# PROJECTIONS & DECOMPOSITIONS
# -----------------------------------------------------------------------------

def project(v, onto):
    """Return the projection of vector v onto vector onto."""
    v, onto = toVector(v), toVector(onto)
    denom = onto.norm() ** 2
    if denom == 0:
        raise ValueError("Cannot project onto zero vector")
    return onto * (dot(v, onto) / denom)

def reject(v, onto):
    """Return the rejection of v from onto (component orthogonal to onto)."""
    v, onto = toVector(v), toVector(onto)
    return v - project(v, onto)

def reflect(v, normal):
    """Reflect vector v across a line through the origin with normal."""
    v, normal = toVector(v), toVector(normal)
    denom = normal.norm() ** 2
    if denom == 0:
        raise ValueError("Cannot reflect across zero normal")
    factor = 2 * dot(v, normal) / denom
    return v - normal * factor

# -----------------------------------------------------------------------------
# LENGTH CONTROL & INTERPOLATION
# -----------------------------------------------------------------------------

def clamp(v, max_len: float):
    """Clamp the magnitude of v to a maximum length."""
    v = toVector(v)
    n = v.norm()
    if n == 0 or n <= max_len:
        return Vector(v)
    return v * (max_len / n)

def lerp(v1, v2, t: float):
    """Return the linear interpolation between v1 and v2 by factor t."""
    v1, v2 = toVector(v1), toVector(v2)
    return (1 - t) * v1 + t * v2

def midpoint(v1, v2):
    """Return the midpoint between v1 and v2."""
    v1, v2 = toVector(v1), toVector(v2)
    return lerp(v1, v2, 0.5)

# -----------------------------------------------------------------------------
# ROTATION / POLAR
# -----------------------------------------------------------------------------

def rotate(v, theta: float):
    """Return vector v rotated by theta radians counterclockwise."""
    v = toVector(v)
    c = math.cos(theta)
    s = math.sin(theta)
    return Vector(c * v.x - s * v.y, s * v.x + c * v.y)

def polar(r: float, theta: float):
    """Create a vector from polar coordinates (r, theta)."""
    return Vector(r * math.cos(theta), r * math.sin(theta))