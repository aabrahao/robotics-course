import matplotlib.pylab as plt
import numpy as np
from scipy.spatial import ConvexHull

from eml4806.geometry.vector import toVectors

def generateLawn(x, y, w, h, border_percentage, n):
    """
    Generate a random convex polygon ("lawn") inside a rectangle,
    leaving a border around the edges.

    Parameters
    ----------
    x, y : float
        Bottom-left corner of the full area.
    w, h : float
        Width and height of the full area.
    border_percentage : float
        Fraction of width/height to leave as border on EACH side.
        Example: 0.1 -> 10% border on each side.
    n : int
        Number of vertices.

    Returns
    -------
    poly : (n, 2) ndarray
        Vertices of the convex polygon inside the inner area.
    """
    # If user passes 10 instead of 0.10, normalize it
    if border_percentage > 1.0:
        border_percentage = border_percentage / 100.0

    if not (0.0 <= border_percentage < 0.5):
        raise ValueError("border_percentage must be in [0, 0.5).")

    # Compute inner (usable) rectangle
    margin_x = w * border_percentage
    margin_y = h * border_percentage

    inner_x = x + margin_x
    inner_y = y + margin_y
    inner_w = w - 2 * margin_x
    inner_h = h - 2 * margin_y

    if inner_w <= 0 or inner_h <= 0:
        raise ValueError("Border too large, no space left for the lawn.")

    # Use the optimized function you already have:
    poly = random_convex_polygon(n, inner_x, inner_y, inner_w, inner_h)

    # If you really need a list of tuples:
    poly_as_list = [tuple(p) for p in poly]

    return toVectors(poly_as_list)

_rng = np.random.default_rng()  # module-level RNG

def random_convex_polygon(n, x, y, w, h, max_tries=1000):
    """
    Generate a random convex polygon with `n` vertices inside an axis-aligned
    rectangle:

        bottom-left corner: (x, y)
        size: (w, h)

    Returns
    -------
    poly : (n, 2) ndarray of float
        Vertices in counter-clockwise order.
    """
    if n < 3:
        raise ValueError("Polygon must have at least 3 vertices")

    if w <= 0 or h <= 0:
        raise ValueError("Width and height must be positive")

    xmax = x + w
    ymax = y + h

    # Oversample factor; tweak if you want richer hulls
    k = max(5 * n, n + 5)

    for _ in range(max_tries):
        # Vectorized random points
        pts = np.empty((k, 2), dtype=float)
        pts[:, 0] = _rng.uniform(x,   xmax, k)
        pts[:, 1] = _rng.uniform(y,   ymax, k)

        # Compute convex hull
        hull = ConvexHull(pts)
        hull_pts = pts[hull.vertices]  # CCW order
        m = hull_pts.shape[0]

        if m < n:
            # Not enough distinct hull vertices, resample
            continue

        if m == n:
            return hull_pts

        # m > n: pick n evenly spaced hull vertices
        # np.linspace avoids Python loops & rounding noise
        idx = np.linspace(0, m - 1, n, endpoint=False, dtype=int)
        return hull_pts[idx]

    raise RuntimeError("Failed to generate a convex polygon after many attempts.")
