import matplotlib.pylab as plt
import numpy as np

from eml4806.geometry.vector import vectors

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

def generate_convex_polygon(n, x, y, w, h, *, randomness=0.3, padding=10):
    """
    Generates a non-skewed convex polygon with exactly n vertices.
    
    Parameters:
    - n: Number of vertices.
    - x, y, w, h: Bounding box dimensions.
    - randomness: How much the shape deviates from a regular polygon (0 to 1).
    - padding: Buffer in pixels/units between the polygon and the box edge.
    """
    if n < 3:
        raise ValueError("A polygon must have at least 3 vertices.")
    
    # 1. Generate angles with jitter
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    angle_jitter = (randomness * (2 * np.pi / n)) / 2
    angles += np.random.uniform(-angle_jitter, angle_jitter, n)
    angles = np.sort(angles)

    # 2. Generate radii with jitter
    base_radius = 0.5
    radius_jitter = np.random.uniform(-randomness * 0.2, randomness * 0.2, n)
    radii = base_radius + radius_jitter

    # 3. Convert to Cartesian
    vertices = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])

    # 4. Normalize to 0-1 range
    v_min, v_max = vertices.min(axis=0), vertices.max(axis=0)
    vertices = (vertices - v_min) / (v_max - v_min)
    
    # 5. Apply Padding and Scale
    # We reduce the available width/height by 2 * padding
    inner_w = w - (2 * padding)
    inner_h = h - (2 * padding)
    
    if inner_w <= 0 or inner_h <= 0:
        raise ValueError("Padding is too large for the given bounding box.")

    vertices[:, 0] = vertices[:, 0] * inner_w + x + padding
    vertices[:, 1] = vertices[:, 1] * inner_h + y + padding

    return vectors(vertices)