import matplotlib.pylab as plt
import numpy as np

from eml4806.geometry.vector import toVectors

_rng = np.random.default_rng()  # module-level RNG

def convex_hull(points):
    """
    Compute the 2D convex hull of a set of points using only NumPy.
    Returns points on the hull in counter-clockwise order with no
    duplicated first/last point.

    Parameters
    ----------
    points : (k, 2) array_like

    Returns
    -------
    hull : (m, 2) ndarray
    """
    pts = np.asarray(points, dtype=float)
    if pts.shape[0] < 3:
        # Degenerate: just return unique points
        # (random_convex_polygon will handle m < n case)
        _, idx = np.unique(pts, axis=0, return_index=True)
        return pts[np.sort(idx)]

    # Sort by x, then by y
    order = np.lexsort((pts[:, 1], pts[:, 0]))
    pts = pts[order]

    def cross(o, a, b):
        # 2D cross product (o->a) x (o->b)
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in pts[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenate lower and upper hulls, removing duplicate endpoints
    hull = np.array(lower[:-1] + upper[:-1])

    # Remove any exact duplicates just in case
    hull_unique, idx = np.unique(hull, axis=0, return_index=True)
    hull_unique = hull_unique[np.argsort(idx)]

    return hull_unique


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
        pts[:, 0] = _rng.uniform(x, xmax, k)
        pts[:, 1] = _rng.uniform(y, ymax, k)

        # Compute convex hull with pure NumPy
        hull_pts = convex_hull(pts)
        m = hull_pts.shape[0]

        if m < n:
            # Not enough distinct hull vertices, resample
            continue

        if m == n:
            return hull_pts

        # m > n: pick n evenly spaced hull vertices
        idx = np.linspace(0, m - 1, n, endpoint=False, dtype=int)
        return hull_pts[idx]

    raise RuntimeError("Failed to generate a convex polygon after many attempts.")


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
    poly : collection of vectors
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

    poly = random_convex_polygon(n, inner_x, inner_y, inner_w, inner_h)

    # If you really need a list of tuples:
    poly_as_list = [tuple(p) for p in poly]

    return toVectors(poly_as_list)
