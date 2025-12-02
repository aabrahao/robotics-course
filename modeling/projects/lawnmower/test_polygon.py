import matplotlib.pylab as plt
import numpy as np
from scipy.spatial import ConvexHull

_rng = np.random.default_rng()  # module-level RNG

def random_convex_polygon(n, x, y, size, max_tries=1000):
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

    w, h = size
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

# --------------------------
# Demo / test code
# --------------------------

if __name__ == "__main__":

    import matplotlib.pyplot as plt

    poly = random_convex_polygon(
        n=4,
        x=0.0,
        y=0.0,
        size=(10.0, 6.0)
    )

    print(poly)

    # If you really need a list of tuples:
    poly_as_list = [tuple(p) for p in poly]

    xs = np.append(poly[:, 0], poly[0, 0])
    ys = np.append(poly[:, 1], poly[0, 1])

    plt.plot(xs, ys, marker="o")
    plt.fill(xs, ys, alpha=0.3)
    plt.gca().set_aspect("equal")
    plt.title("Optimized Random Convex Polygon")
    plt.show()

