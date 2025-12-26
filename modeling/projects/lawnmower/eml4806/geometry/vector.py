import numpy as np
import math

# Pre-binding for micro-optimizations
_sqrt = math.sqrt
_cos = math.cos
_sin = math.sin
_atan2 = math.atan2
_acos = math.acos

# =============================================================================
# VECTOR CREATION
# =============================================================================

def vector(*args) -> np.ndarray:
    """Fast-path entry: returns input if already (3,) float64 ndarray."""
    if len(args) == 1:
        v = args[0]
        if type(v) is np.ndarray and v.shape == (3,) and v.dtype == np.float64:
            return v
        arr = np.asarray(v, dtype=np.float64).ravel()
        if arr.size == 3: return arr
        if arr.size == 2: return np.array([arr[0], arr[1], 0.0], dtype=np.float64)
        raise ValueError(f"Vector size {arr.size} invalid.")
    if len(args) == 0:
        return np.zeros(3, dtype=np.float64)
    if len(args) == 3: return np.array(args, dtype=np.float64)
    if len(args) == 2: return np.array([args[0], args[1], 0.0], dtype=np.float64)
    raise TypeError("vector() takes 0, 1, 2, or 3 arguments")

# =============================================================================
# COORDINATE SYSTEMS
# =============================================================================

def polar(r: float, theta: float) -> np.ndarray:
    """Create 3D vector (z=0) from 2D polar coordinates."""
    return np.array([r * _cos(theta), r * _sin(theta), 0.0], dtype=np.float64)

def spherical(r: float, theta: float, phi: float) -> np.ndarray:
    """Create 3D vector from spherical (radial r, azimuth theta, inclination phi)."""
    sin_phi = _sin(phi)
    return np.array([
        r * sin_phi * _cos(theta),
        r * sin_phi * _sin(theta),
        r * _cos(phi)
    ], dtype=np.float64)

# =============================================================================
# OPTIMIZED PRIMITIVES (Raw Arithmetic)
# =============================================================================

def dot(v1: np.ndarray, v2: np.ndarray) -> float:
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return np.array([
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0]
    ], dtype=np.float64)

def triple_product(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """a · (b x c)"""
    return a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])

# =============================================================================
# BASIC OPERATIONS
# =============================================================================

def norm_squared(v: np.ndarray) -> float:
    return dot(v, v)

def norm(v: np.ndarray) -> float:
    return _sqrt(dot(v, v))

def distance_squared(v1: np.ndarray, v2: np.ndarray) -> float:
    dx, dy, dz = v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]
    return dx*dx + dy*dy + dz*dz

def distance(v1: np.ndarray, v2: np.ndarray) -> float:
    return _sqrt(distance_squared(v1, v2))

def unit(v: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    n = norm(v)
    if n < epsilon: raise ValueError("Null vector")
    return v / n

# =============================================================================
# 2D SPECIFIC OPERATIONS (XY-Plane)
# =============================================================================

def cross2d(v1: np.ndarray, v2: np.ndarray) -> float:
    """Z-component of cross product (signed area/orientation)."""
    return v1[0]*v2[1] - v1[1]*v2[0]

def perpendicular2d(v: np.ndarray, clockwise: bool = False) -> np.ndarray:
    """90° rotation in the XY plane."""
    if clockwise:
        return np.array([v[1], -v[0], 0.0], dtype=np.float64)
    return np.array([-v[1], v[0], 0.0], dtype=np.float64)

# =============================================================================
# ANGLES & ROTATIONS
# =============================================================================

def angle(v1: np.ndarray, v2: np.ndarray = None) -> float:
    """Polar angle (1 arg) or signed relative angle (2 args)."""
    if v2 is None: return _atan2(v1[1], v1[0])
    return _atan2(cross2d(v1, v2), dot(v1, v2))

def angle_between(v1: np.ndarray, v2: np.ndarray, epsilon: float = 1e-10) -> float:
    """Unsigned 3D angle [0, π]."""
    m1m2 = norm(v1) * norm(v2)
    if m1m2 < epsilon: raise ValueError("Zero vector angle")
    return _acos(np.clip(dot(v1, v2) / m1m2, -1.0, 1.0))

def rotate_x(v: np.ndarray, theta: float) -> np.ndarray:
    c, s = _cos(theta), _sin(theta)
    return np.array([v[0], c*v[1] - s*v[2], s*v[1] + c*v[2]], dtype=np.float64)

def rotate_y(v: np.ndarray, theta: float) -> np.ndarray:
    c, s = _cos(theta), _sin(theta)
    return np.array([c*v[0] + s*v[2], v[1], -s*v[0] + c*v[2]], dtype=np.float64)

def rotate_z(v: np.ndarray, theta: float) -> np.ndarray:
    c, s = _cos(theta), _sin(theta)
    return np.array([c*v[0] - s*v[1], s*v[0] + c*v[1], v[2]], dtype=np.float64)

def rotate2d(v: np.ndarray, theta: float) -> np.ndarray:
    return rotate_z(v, theta)

def rotate_axis(v: np.ndarray, axis: np.ndarray, theta: float) -> np.ndarray:
    """Rodrigues' rotation formula."""
    k = unit(axis)
    c, s = _cos(theta), _sin(theta)
    return v*c + cross(k, v)*s + k*dot(k, v)*(1.0-c)

# =============================================================================
# PROJECTIONS & GEOMETRY
# =============================================================================

def project(v: np.ndarray, onto: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    d2 = dot(onto, onto)
    if d2 < epsilon: raise ValueError("Project onto zero")
    return onto * (dot(v, onto) / d2)

def reject(v: np.ndarray, onto: np.ndarray) -> np.ndarray:
    """Perpendicular component of v relative to onto."""
    return v - project(v, onto)

def decompose(v: np.ndarray, onto: np.ndarray):
    """Returns (parallel, perpendicular) components."""
    p = project(v, onto)
    return p, v - p

def reflect(v: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Reflect v across a surface with given normal."""
    return v - project(v, normal) * 2.0

# =============================================================================
# INTERPOLATION & CONTROL
# =============================================================================

def clamp(v: np.ndarray, max_len: float) -> np.ndarray:
    n2 = dot(v, v)
    if n2 <= max_len * max_len: return v.copy()
    return v * (max_len / _sqrt(n2))

def set_magnitude(v: np.ndarray, new_mag: float, epsilon: float = 1e-10) -> np.ndarray:
    n = norm(v)
    if n < epsilon: raise ValueError("Zero vector magnitude")
    return v * (new_mag / n)

def lerp(v1: np.ndarray, v2: np.ndarray, t: float) -> np.ndarray:
    return v1 + (v2 - v1) * t

def midpoint(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
    return (v1 + v2) * 0.5

def slerp(v1: np.ndarray, v2: np.ndarray, t: float, epsilon: float = 1e-10) -> np.ndarray:
    """Spherical linear interpolation."""
    n1, n2 = norm(v1), norm(v2)
    if n1 < epsilon or n2 < epsilon: return lerp(v1, v2, t)
    u1, u2 = v1/n1, v2/n2
    dot_val = np.clip(dot(u1, u2), -1.0, 1.0)
    omega = _acos(dot_val)
    if omega < 1e-6: return lerp(v1, v2, t)
    sin_o = _sin(omega)
    return (u1 * (_sin((1-t)*omega)/sin_o) + u2 * (_sin(t*omega)/sin_o)) * lerp(n1, n2, t)

# =============================================================================
# ALIASES & CHECKS
# =============================================================================

def is_zero(v: np.ndarray, tol: float = 1e-9) -> bool:
    return dot(v, v) <= tol * tol

def coincident(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-2) -> bool:
    return distance_squared(v1, v2) <= tol * tol

def is_parallel(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-6) -> bool:
    u1, u2 = unit(v1), unit(v2)
    return abs(abs(dot(u1, u2)) - 1.0) < tol

def is_perpendicular(v1: np.ndarray, v2: np.ndarray, tol: float = 1e-6) -> bool:
    return abs(dot(v1, v2)) < tol

resize = set_magnitude
mag = magnitude = norm
dist = distance
normalize = unit
rotate = rotate2d
is_null = is_zero
parallel_component = project
perpendicular_component = reject
perp2d = perpendicular2d

# =============================================================================
# Vectors
# =============================================================================

def vectors(*args) -> np.ndarray:
    """Normalize inputs to (N,3) float64. Optimized for (N,3) ndarray."""
    n = len(args)
    if n == 1:
        v = args[0]
        # Fastest path: already (N,3) float64
        if type(v) is np.ndarray and v.ndim == 2 and v.shape[1] == 3 and v.dtype == np.float64:
            return v
        if v is None: return np.empty((0, 3), dtype=np.float64)
        
        arr = np.atleast_1d(np.asarray(v, dtype=np.float64))
        if arr.size == 0: return np.empty((0, 3), dtype=np.float64)
        
        # Reshape or pad 1D/2D inputs
        if arr.ndim == 1:
            if arr.size == 3: return arr.reshape(1, 3)
            if arr.size == 2: return np.concatenate([arr, [0.0]]).reshape(1, 3)
        elif arr.ndim == 2:
            if arr.shape[1] == 3: return arr
            if arr.shape[1] == 2: 
                return np.column_stack([arr, np.zeros(len(arr))])
        raise ValueError(f"Invalid shape {arr.shape}")

    if n == 0: return np.empty((0, 3), dtype=np.float64)
    
    # 2 or 3 arg: Coordinate stacking using broadcasting
    try:
        xyz = args if n == 3 else (*args, 0.0)
        return np.column_stack(np.broadcast_arrays(*xyz)).astype(np.float64)
    except:
        raise ValueError("Coordinate shapes must match.")

def split(data: np.ndarray) -> tuple:
    """Unpack (N,3) into X, Y, Z via Transpose view."""
    v = data if (type(data) is np.ndarray and data.shape[-1] == 3) else vectors(data)
    return v.T  # Unpacks automatically if used as x, y, z = split(d)

def append(data: np.ndarray, item) -> np.ndarray:
    return np.concatenate((data, vectors(item)), axis=0)

def prepend(data: np.ndarray, item) -> np.ndarray:
    return np.concatenate((vectors(item), data), axis=0)