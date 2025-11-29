import numpy as np

def new(x, y):
    """Create a 2D vector or array of vectors from scalars or arrays, broadcasting as needed."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape == () and y.shape == ():
        return np.array([x, y], float)
    X, Y = np.broadcast_arrays(x, y)
    return np.column_stack((X, Y))

def ensure(v):
    """
    Normalize v into a valid 2D vector representation.
    Rules:
        None, []       -> empty array of shape (0, 2)
        (2,)           -> single vector, stays (2,)
        (N,2)          -> list of vectors, stays (N,2)  (including N=1)
        anything else  -> error
    """
    if v is None:
        return np.empty((0, 2), dtype=float)
    a = np.asarray(v, dtype=float)
    # Empty → canonical "no vectors"
    if a.size == 0:
        return np.empty((0, 2), dtype=float)
    # (2,) → single vector
    if a.ndim == 1 and a.shape[0] == 2:
        return a
    # (N,2) → list of vectors (including N = 1)
    if a.ndim == 2 and a.shape[1] == 2:
        return a
    # Anything else → invalid
    raise ValueError(f"ensure(): expected shape (2,) or (N,2); got {a.shape}")

def ensureOne(v):
    """
    Ensure v represents exactly ONE 2D vector.
    Valid:
        (2,)      → (2,)
        (1,2)     → (2,)
    Errors:
        None, []
        (N,2) with N != 1
        any other shape
    """
    a = ensure(v)
    # None / [] → ensure() gave (0,2)
    if a.size == 0:
        raise ValueError("ensureOne(): empty input does not represent a vector")
    # Single vector: (2,)
    if a.ndim == 1 and a.shape == (2,):
        return a
    # Exactly one row: (1,2) → (2,)
    if a.ndim == 2 and a.shape == (1, 2):
        return a[0]
    # More than one row, or weird shape
    raise ValueError(f"ensureOne(): expected a single vector, got shape {a.shape}")

def ensureMany(v):
    """
    Ensure v represents zero, one, or many 2D vectors.
    Valid:
        None      → empty (0,2)
        []        → empty (0,2)
        (2,)      → (1,2)
        (1,2)     → (1,2)
        (N,2)     → (N,2)
    Errors:
        any other shape
    """
    a = ensure(v)
    # (0,2) or (N,2) already fine
    if a.ndim == 2:
        return a
    # (2,) → promote to (1,2)
    # (because ensure() guarantees this is the only valid 1D shape)
    return a.reshape(1, 2)

def isEmpty(v):
    if v is None: return True
    if len(v)==0: return True
    return False

def null():
    """Return a zero 2D vector (2,)."""
    return new(0.0, 0.0)

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

def append(points, more_points):
    """Append one or many 2D vectors to an existing list of vectors."""
    p = ensureMany(points)
    q = ensureMany(more_points)
    if p.size == 0:
        return q
    if q.size == 0:
        return p
    return np.concatenate((p, q), axis=0)

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