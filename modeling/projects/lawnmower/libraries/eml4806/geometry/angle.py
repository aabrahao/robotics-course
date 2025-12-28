import numpy as np

# Pre-calculate constants outside the function to save CPU cycles
_PI = np.pi
_TWO_PI = 2.0 * np.pi

def wrap(radians):
    rads = np.asarray(radians)
    wrapped = (rads + _PI) % _TWO_PI - _PI
    # ndim == 0 means it's a single value (scalar)
    if rads.ndim == 0:
        return float(wrapped)
    return wrapped

def radians(degrees):
    return wrap( np.deg2rad(degrees) )