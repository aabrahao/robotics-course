import numpy as np
import matplotlib.pyplot as plt


def makeScanGrid(lawn, tool_diameter):
    """
    Generate a lawnmower (scanline) coverage pattern over a convex polygon.

    Parameters
    ----------
    lawn : (N, 2) array_like
        Convex polygon vertices (N >= 3), in order (clockwise or CCW).
    tool_diameter : float
        Spacing between adjacent scan lines (tool / mower width).

    Returns
    -------
    waypoints : (M, 2) ndarray
        Ordered list of (x, y) waypoints following a back-and-forth pattern.
    """
    lawn = np.asarray(lawn, dtype=float)
    if lawn.ndim != 2 or lawn.shape[1] != 2 or lawn.shape[0] < 3:
        raise ValueError("lawn must be an (N, 2) array with N >= 3")

    if tool_diameter <= 0:
        raise ValueError("tool_diameter must be positive")

    # ---------------------------------------------------------------------
    # 1) Build a local coordinate frame aligned with the polygon's "major" axis
    # ---------------------------------------------------------------------
    center = lawn.mean(axis=0)
    A = lawn - center  # centered vertices

    # PCA: find principal directions from covariance
    cov = np.cov(A.T)
    eigvals, eigvecs = np.linalg.eigh(cov)  # sorted ascending
    ex = eigvecs[:, 1]  # eigenvector for largest eigenvalue
    ex = ex / np.linalg.norm(ex)
    ey = np.array([-ex[1], ex[0]])  # perpendicular

    # Transform vertices to local (u, v) coordinates
    u = A @ ex
    v = A @ ey
    poly_uv = np.column_stack((u, v))

    v_min = v.min()
    v_max = v.max()

    # ---------------------------------------------------------------------
    # 2) Generate horizontal scanlines in local (u, v) frame
    # ---------------------------------------------------------------------
    vs = np.arange(v_min + tool_diameter / 2.0, v_max, tool_diameter)
    if vs.size == 0:
        vs = np.array([(v_min + v_max) / 2.0])  # small polygon fallback

    waypoints_local = []

    n = poly_uv.shape[0]

    for i, vy in enumerate(vs):
        # Find intersections of line v = vy with polygon edges
        u_intersections = []

        for j in range(n):
            ux0, vy0 = poly_uv[j]
            ux1, vy1 = poly_uv[(j + 1) % n]

            # Check if the horizontal line crosses the edge
            # (vy - vy0) and (vy - vy1) with opposite signs or zero
            denom = (vy1 - vy0)
            if denom == 0:
                continue  # edge is horizontal; skip

            t = (vy - vy0) / denom
            if 0.0 <= t <= 1.0:
                ux = ux0 + t * (ux1 - ux0)
                u_intersections.append(ux)

        if len(u_intersections) < 2:
            # No valid segment on this scanline
            continue

        # Sort and deduplicate intersections
        u_intersections = np.unique(np.array(u_intersections))
        if u_intersections.size < 2:
            continue

        u_left = u_intersections.min()
        u_right = u_intersections.max()

        if i % 2 == 0:
            # left -> right
            waypoints_local.append([u_left, vy])
            waypoints_local.append([u_right, vy])
        else:
            # right -> left
            waypoints_local.append([u_right, vy])
            waypoints_local.append([u_left, vy])

    if not waypoints_local:
        return np.empty((0, 2))

    waypoints_local = np.asarray(waypoints_local)

    # ---------------------------------------------------------------------
    # 3) Transform back to world (x, y) coordinates
    # ---------------------------------------------------------------------
    waypoints_world = center + np.outer(waypoints_local[:, 0], ex) + np.outer(
        waypoints_local[:, 1], ey
    )

    return waypoints_world


# -------------------------------------------------------------------------
# TEST CODE
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: irregular convex quadrilateral (rotated, skewed)
    # Start from a simple rectangle and rotate/translate it
    base = np.array([
        [0.0, 0.0],
        [4.0, 0.5],
        [3.5, 2.5],
        [-0.5, 2.0]
    ])

    # Optionally rotate and translate (to show it's really irregular)
    theta = np.deg2rad(25.0)
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    lawn = base @ R.T + np.array([2.0, 1.0])

    tool_diameter = 0.4

    waypoints = makeScanGrid(lawn, tool_diameter)
    print("Waypoints shape:", waypoints.shape)
    print(waypoints[:10], " ...")  # print first few

    # Close polygon for plotting
    lawn_closed = np.vstack([lawn, lawn[0]])

    plt.figure(figsize=(7, 6))
    plt.plot(lawn_closed[:, 0], lawn_closed[:, 1],
             "-o", label="Lawn boundary", linewidth=2)

    if waypoints.size > 0:
        plt.plot(waypoints[:, 0], waypoints[:, 1],
                 "-o", label="Scan path", markersize=4)

    plt.axis("equal")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Scan Grid over Irregular Convex Lawn")
    plt.legend()
    plt.show()
