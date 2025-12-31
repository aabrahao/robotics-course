import numpy as np
import math

Vector = np.ndarray # (2,)
Vectors = np.ndarray # (N,2)

# Pre-binding for micro-optimizations
_sqrt = math.sqrt
_cos = math.cos
_sin = math.sin
_atan2 = math.atan2
_acos = math.acos

# =============================================================================
# VECTOR CREATION
# =============================================================================

def as_vector(*args) -> np.ndarray:
    """Fast-path entry: returns input if already (2,) float64 ndarray."""
    if len(args) == 1:
        v = args[0]
        if type(v) is np.ndarray and v.shape == (2,) and v.dtype == np.float64:
            return v
        arr = np.asarray(v, dtype=np.float64).ravel()
        if arr.size == 2: 
            return arr
        raise ValueError(f"Vector size {arr.size} invalid, expected 2.")
    if len(args) == 0:
        return np.zeros(2, dtype=np.float64)
    if len(args) == 2: 
        return np.array(args, dtype=np.float64)
    raise TypeError("as_vector() takes 0, 1, or 2 arguments")

# =============================================================================
# COORDINATE SYSTEMS
# =============================================================================

def polar(r: float, theta: float) -> np.ndarray:
    """Create 2D vector from polar coordinates."""
    return np.array([r * _cos(theta), r * _sin(theta)], dtype=np.float64)

# =============================================================================
# OPTIMIZED PRIMITIVES (Raw Arithmetic)
# =============================================================================

def dot(v1: np.ndarray, v2: np.ndarray) -> float:
    """Dot product of two 2D vectors."""
    return v1[0]*v2[0] + v1[1]*v2[1]

def cross(v1: np.ndarray, v2: np.ndarray) -> float:
    """Cross product (scalar z-component, signed area/orientation)."""
    return v1[0]*v2[1] - v1[1]*v2[0]

# =============================================================================
# BASIC OPERATIONS
# =============================================================================

def norm_squared(v: np.ndarray) -> float:
    """Squared magnitude of vector."""
    return v[0]*v[0] + v[1]*v[1]

def norm(v: np.ndarray) -> float:
    """Magnitude of vector."""
    return _sqrt(v[0]*v[0] + v[1]*v[1])

def distance_squared(v1: np.ndarray, v2: np.ndarray) -> float:
    """Squared distance between two vectors."""
    dx, dy = v1[0]-v2[0], v1[1]-v2[1]
    return dx*dx + dy*dy

def distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """Distance between two vectors."""
    return _sqrt(distance_squared(v1, v2))

def unit(v: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """Normalized unit vector."""
    n = norm(v)
    if n < epsilon: 
        raise ValueError("Null vector")
    return v / n

# =============================================================================
# 2D OPERATIONS
# =============================================================================

def perpendicular(v: np.ndarray, clockwise: bool = False) -> np.ndarray:
    """90° rotation. Default counter-clockwise."""
    if clockwise:
        return np.array([v[1], -v[0]], dtype=np.float64)
    return np.array([-v[1], v[0]], dtype=np.float64)

def left(v: np.ndarray) -> np.ndarray:
    """90° counter-clockwise rotation."""
    return np.array([-v[1], v[0]], dtype=np.float64)

def right(v: np.ndarray) -> np.ndarray:
    """90° clockwise rotation."""
    return np.array([v[1], -v[0]], dtype=np.float64)

# =============================================================================
# ANGLES & ROTATIONS
# =============================================================================

def angle(v1: np.ndarray, v2: np.ndarray = None) -> float:
    """
    Polar angle (1 arg) or signed relative angle (2 args).
    One arg: angle from positive x-axis [-π, π].
    Two args: signed angle from v1 to v2 [-π, π].
    """
    if v2 is None: 
        return _atan2(v1[1], v1[0])
    return _atan2(cross(v1, v2), dot(v1, v2))

def angle_between(v1: np.ndarray, v2: np.ndarray, epsilon: float = 1e-10) -> float:
    """Unsigned angle between vectors [0, π]."""
    m1m2 = norm(v1) * norm(v2)
    if m1m2 < epsilon: 
        raise ValueError("Zero vector angle")
    return _acos(np.clip(dot(v1, v2) / m1m2, -1.0, 1.0))

def rotate(v: np.ndarray, theta: float) -> np.ndarray:
    """Rotate vector by angle theta (counter-clockwise)."""
    c, s = _cos(theta), _sin(theta)
    return np.array([c*v[0] - s*v[1], s*v[0] + c*v[1]], dtype=np.float64)

def rotate_around(v: np.ndarray, center: np.ndarray, theta: float) -> np.ndarray:
    """Rotate vector around a center point."""
    return rotate(v - center, theta) + center

# =============================================================================
# PROJECTIONS & GEOMETRY
# =============================================================================

def project(v: np.ndarray, onto: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """Project v onto another vector."""
    d2 = norm_squared(onto)
    if d2 < epsilon: 
        raise ValueError("Project onto zero")
    return onto * (dot(v, onto) / d2)

def reject(v: np.ndarray, onto: np.ndarray) -> np.ndarray:
    """Perpendicular component of v relative to onto."""
    return v - project(v, onto)

def decompose(v: np.ndarray, onto: np.ndarray):
    """Returns (parallel, perpendicular) components."""
    p = project(v, onto)
    return p, v - p

def reflect(v: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Reflect v across a line with given normal."""
    return v - 2.0 * project(v, normal)

# =============================================================================
# INTERPOLATION & CONTROL
# =============================================================================

def clamp(v: np.ndarray, max_len: float) -> np.ndarray:
    """Clamp vector to maximum length."""
    n2 = norm_squared(v)
    if n2 <= max_len * max_len: 
        return v.copy()
    return v * (max_len / _sqrt(n2))

def set_magnitude(v: np.ndarray, new_mag: float, epsilon: float = 1e-10) -> np.ndarray:
    """Set vector to specific magnitude."""
    n = norm(v)
    if n < epsilon: 
        raise ValueError("Zero vector magnitude")
    return v * (new_mag / n)

def limit(v: np.ndarray, max_len: float) -> np.ndarray:
    """Limit vector magnitude (alias for clamp)."""
    return clamp(v, max_len)

def lerp(v1: np.ndarray, v2: np.ndarray, t: float) -> np.ndarray:
    """Linear interpolation between vectors."""
    return v1 + (v2 - v1) * t

def midpoint(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Midpoint between two vectors."""
    return (v1 + v2) * 0.5

def slerp(v1: np.ndarray, v2: np.ndarray, t: float, epsilon: float = 1e-10) -> np.ndarray:
    """Spherical linear interpolation."""
    n1, n2 = norm(v1), norm(v2)
    if n1 < epsilon or n2 < epsilon: 
        return lerp(v1, v2, t)
    u1, u2 = v1/n1, v2/n2
    dot_val = np.clip(dot(u1, u2), -1.0, 1.0)
    omega = _acos(dot_val)
    if omega < 1e-6: 
        return lerp(v1, v2, t)
    sin_o = _sin(omega)
    return (u1 * (_sin((1-t)*omega)/sin_o) + u2 * (_sin(t*omega)/sin_o)) * lerp(n1, n2, t)

# =============================================================================
# GEOMETRIC QUERIES
# =============================================================================

def is_zero(v: np.ndarray, tol: float = 1e-9) -> bool:
    """Check if vector is effectively zero."""
    return norm_squared(v) <= tol * tol

def coincident(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-2) -> bool:
    """Check if two vectors are approximately equal."""
    return distance_squared(v1, v2) <= tol * tol

def is_parallel(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-6) -> bool:
    """Check if vectors are parallel."""
    u1, u2 = unit(v1), unit(v2)
    return abs(abs(dot(u1, u2)) - 1.0) < tol

def is_perpendicular(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-6) -> bool:
    """Check if vectors are perpendicular."""
    return abs(dot(v1, v2)) < tol

def determinant(v1: np.ndarray, v2: np.ndarray) -> float:
    """2x2 determinant (same as cross product)."""
    return v1[0]*v2[1] - v1[1]*v2[0]

def area_triangle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Signed area of triangle (positive if counter-clockwise)."""
    return 0.5 * cross(b - a, c - a)

def ccw(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> bool:
    """Test if points a, b, c are in counter-clockwise order."""
    return cross(b - a, c - a) > 0

# =============================================================================
# ALIASES
# =============================================================================

resize = set_magnitude
mag = magnitude = norm
dist = distance
normalize = unit
is_null = is_zero
parallel_component = project
perpendicular_component = reject
perp = perpendicular
cross2d = cross

# =============================================================================
# BATCH OPERATIONS (Multiple Vectors)
# =============================================================================

def as_vectors(*args) -> np.ndarray:
    """Normalize inputs to (N,2) float64. Optimized for (N,2) ndarray."""
    n = len(args)
    if n == 1:
        v = args[0]
        # Fastest path: already (N,2) float64
        if type(v) is np.ndarray and v.ndim == 2 and v.shape[1] == 2 and v.dtype == np.float64:
            return v
        if v is None: 
            return np.empty((0, 2), dtype=np.float64)
        
        arr = np.atleast_1d(np.asarray(v, dtype=np.float64))
        if arr.size == 0: 
            return np.empty((0, 2), dtype=np.float64)
        
        # Reshape 1D/2D inputs
        if arr.ndim == 1:
            if arr.size == 2: 
                return arr.reshape(1, 2)
            if arr.size % 2 == 0:
                return arr.reshape(-1, 2)
        elif arr.ndim == 2:
            if arr.shape[1] == 2: 
                return arr
        raise ValueError(f"Invalid shape {arr.shape}, expected (N,2)")

    if n == 0: 
        return np.empty((0, 2), dtype=np.float64)
    
    # 2 arg: Coordinate stacking using broadcasting
    if n == 2:
        try:
            return np.column_stack(np.broadcast_arrays(*args)).astype(np.float64)
        except:
            raise ValueError("Coordinate shapes must match.")
    
    raise TypeError("as_vectors() takes 0, 1, or 2 arguments")

def split(data: np.ndarray) -> tuple:
    """Unpack (N,2) into X, Y via transpose view."""
    v = data if (type(data) is np.ndarray and data.shape[-1] == 2) else as_vectors(data)
    return v.T  # Unpacks automatically if used as x, y = split(d)

def append(data: np.ndarray, item) -> np.ndarray:
    """Append vector(s) to array."""
    return np.concatenate((data, as_vectors(item)), axis=0)

def prepend(data: np.ndarray, item) -> np.ndarray:
    """Prepend vector(s) to array."""
    return np.concatenate((as_vectors(item), data), axis=0)

# =============================================================================
# VECTORIZED OPERATIONS (operate on multiple vectors at once)
# =============================================================================

def norms(vectors: np.ndarray) -> np.ndarray:
    """Compute norms of multiple vectors efficiently."""
    return np.sqrt(np.sum(vectors * vectors, axis=1))

def normalize_batch(vectors: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """Normalize multiple vectors."""
    n = norms(vectors)[:, np.newaxis]
    n = np.where(n < epsilon, 1.0, n)
    return vectors / n

def rotate_batch(vectors: np.ndarray, theta: float) -> np.ndarray:
    """Rotate multiple vectors by same angle."""
    c, s = _cos(theta), _sin(theta)
    x, y = vectors[:, 0], vectors[:, 1]
    return np.column_stack([c*x - s*y, s*x + c*y])

def distances(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    """Compute distances between corresponding pairs of vectors."""
    diff = v1 - v2
    return np.sqrt(np.sum(diff * diff, axis=1))