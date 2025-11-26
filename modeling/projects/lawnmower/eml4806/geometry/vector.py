import numpy as np

def vector(x, y):
    """Create a 2D vector or array of vectors from scalars or arrays, broadcasting as needed."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape == () and y.shape == ():
        return np.array([x, y], float)
    X, Y = np.broadcast_arrays(x, y)
    return np.column_stack((X, Y))

def ensure(v):
    """Ensure input is a valid 2D vector shape: (2,) or (N,2)."""
    if v is None: return None
    e = np.asarray(v, float)
    if e.ndim == 1 and e.shape[0] == 2: return e
    if e.ndim == 2 and e.shape[1] == 2: return e
    raise ValueError(f"Expected (2,) or (N,2), got {e.shape}")

def scalar(x):
    """Return True if x is a numeric scalar."""
    return np.isscalar(x)

def null():
    """Return a zero 2D vector (2,)."""
    return vector(0.0, 0.0)

def zero(v, tol=1e-9):
    """Check if vector(s) are near zero length."""
    return length(v) <= tol

def length(v):
    """Return Euclidean length(s) of a vector or array of vectors."""
    return np.linalg.norm(ensure(v), axis=-1)

def distance(v1, v2):
    """Return Euclidean distance(s) between vector(s)."""
    e1, e2 = ensure(v1), ensure(v2)
    return np.linalg.norm(e1 - e2, axis=-1)

def angle(v):
    """Return angle(s) of 2D vector(s) in radians."""
    e = ensure(v)
    return np.arctan2(e[...,1], e[...,0])

def coincident(v1, v2, tol=1e-2):
    """Check if vectors/sets are equal within a geometric tolerance."""
    e1, e2 = ensure(v1), ensure(v2)
    return e1.shape == e2.shape and np.sum((e1 - e2)**2, axis=-1).max() <= tol*tol

def unit(v):
    """Return normalized vector(s). Zero vectors remain unchanged."""
    e = ensure(v)
    n = np.linalg.norm(e, axis=-1, keepdims=True)
    r = e / np.where(n == 0, 1, n)
    return r[0] if r.shape == (1,2) else r

def perpendicular(v, clockwise=False):
    """Return a perpendicular vector (clockwise or counterclockwise)."""
    e = ensure(v)
    p = np.column_stack(( e[...,1], -e[...,0])) if clockwise \
        else np.column_stack((-e[...,1],  e[...,0]))
    return p[0] if p.shape == (1,2) else p

def split(v):
    """Split a vector/array into x and y components."""
    e = ensure(v)
    return (e[0], e[1]) if e.ndim == 1 else (e[:,0], e[:,1])

def append(points, new):
    """Append one or many 2D vectors to an existing list of vectors."""
    if points is None: return ensure([new])
    if new    is None: return ensure([points])
    e1, e2 = ensure(points), ensure(new)
    if e1.ndim == 1: e1 = e1[None]
    if e2.ndim == 1: e2 = e2[None]
    return np.concatenate((e1, e2), 0)

def dot(v1, v2):
    """Return dot product of two 2D vectors or arrays of vectors."""
    e1, e2 = ensure(v1), ensure(v2)
    return np.sum(e1 * e2, axis=-1)

def cross(v1, v2):
    """Return 2D cross product (scalar z-component) for vector(s)."""
    e1, e2 = ensure(v1), ensure(v2)
    return e1[...,0] * e2[...,1] - e1[...,1] * e2[...,0]

def bounding(v):
    """Return min and max corners of a point set."""
    e = ensure(v)
    return e.min(axis=0), e.max(axis=0)