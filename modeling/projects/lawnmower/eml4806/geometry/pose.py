import numpy as np

import eml4806.geometry.vector as vector
import eml4806.geometry.angle as angle

def new(x,y,theta):
    return np.array([x, y, angle.wrap(theta)], dtype='float')

def ensureOne(p):
    """
    Ensure p is exactly a 3-element numpy array (x, y, theta).
    Requirements:
        - shape must be (3,)
        - dtype is float
        - no None, no empty, no extra dimensions
    """
    if p is None:
        raise ValueError("ensurePose(): None is not a valid pose")
    a = np.asarray(p, dtype=float)
    # Must be exactly 3 elements in 1D
    if a.ndim != 1 or a.shape[0] != 3:
        raise ValueError(f"ensurePose(): expected shape (3,), got {a.shape}")
    return a

def set(position, heading):
    p = vector.ensureOne(position)
    h = float(heading)
    return new(p[0], p[1], h)

def position(p):
    return vector.new(p[0], p[1])

def heading(p):
    return p[2]

def direction(p):
    return vector.new(np.cos(p[2]), np.sin(p[2]))

