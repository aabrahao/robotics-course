import numpy as np
import matplotlib.pyplot as plt

def generate_convex_polygon(n, x, y, w, h, randomness=0.3, padding=10):
    """Generates a non-skewed convex polygon within a padded bounding box."""
    if n < 3: raise ValueError("n must be >= 3")
    
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    angle_jitter = (randomness * (2 * np.pi / n)) / 2
    angles += np.random.uniform(-angle_jitter, angle_jitter, n)
    angles = np.sort(angles)

    radii = 0.5 + np.random.uniform(-randomness * 0.2, randomness * 0.2, n)
    vertices = np.column_stack([radii * np.cos(angles), radii * np.sin(angles)])

    v_min, v_max = vertices.min(axis=0), vertices.max(axis=0)
    vertices = (vertices - v_min) / (v_max - v_min)
    
    inner_w, inner_h = w - (2 * padding), h - (2 * padding)
    if inner_w <= 0 or inner_h <= 0:
        raise ValueError("Padding is too large for the bounding box.")
        
    vertices[:, 0] = vertices[:, 0] * inner_w + x + padding
    vertices[:, 1] = vertices[:, 1] * inner_h + y + padding

    return vertices

def get_continuous_raster_path(vertices, d):
    """Generates a continuous path starting with the first edge followed by a zigzag."""
    # 1. Align coordinate system to the first edge
    p0, p1 = vertices[0], vertices[1]
    angle = np.arctan2(p1[1] - p0[1], p1[0] - p0[0])
    
    cos_a, sin_a = np.cos(-angle), np.sin(-angle)
    R = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    rot_verts = vertices @ R.T
    
    # 2. Setup scanlines (starting after the first edge height)
    y_min, y_max = np.min(rot_verts[:, 1]), np.max(rot_verts[:, 1])
    # We offset scan_y so it doesn't overlap perfectly with the first edge
    scan_y = np.arange(y_min + d, y_max, d)
    
    loop = np.vstack([rot_verts, rot_verts[0]])
    
    # Start the path with the first two vertices (the first edge)
    # We keep them in the rotated coordinate system for now
    path_points = [rot_verts[0], rot_verts[1]]
    
    for i, y in enumerate(scan_y):
        intersections = []
        for j in range(len(loop) - 1):
            v1, v2 = loop[j], loop[j+1]
            if (v1[1] <= y < v2[1]) or (v2[1] <= y < v1[1]):
                x_int = v1[0] + (y - v1[1]) / (v2[1] - v1[1]) * (v2[0] - v1[0])
                intersections.append(x_int)
        
        if len(intersections) >= 2:
            intersections.sort()
            # Zig-zag: if current end point is far from next start, flip intersections
            # This ensures the tool moves to the closest next point
            last_point_x = path_points[-1][0]
            dist_to_first = abs(intersections[0] - last_point_x)
            dist_to_last = abs(intersections[-1] - last_point_x)
            
            if dist_to_last < dist_to_first:
                intersections.reverse()
                
            for x_p in intersections:
                path_points.append(np.array([x_p, y]))

    # 3. Rotate everything back to world space
    rev_R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return np.array(path_points) @ rev_R.T

def main():
    # Parameters
    N_VERTICES = 6
    BBOX = (0, 0, 500, 500)
    SPACING = 25
    
    # 1. Generate Polygon
    poly = generate_convex_polygon(N_VERTICES, *BBOX, randomness=0.4, padding=40)
    
    # 2. Generate Path (First Edge + Zigzag)
    path = get_continuous_raster_path(poly, SPACING)
    
    # 3. Plot
    plt.figure(figsize=(8, 8))
    
    # Draw Polygon Outline
    closed_poly = np.vstack([poly, poly[0]])
    plt.plot(closed_poly[:, 0], closed_poly[:, 1], 'k--', alpha=0.3, label="Polygon Outline")
    
    # Draw the continuous path
    plt.plot(path[:, 0], path[:, 1], 'r-', lw=2, label="Toolpath (Edge + Zigzag)")
    
    # Highlight the First Edge (part of the path)
    plt.plot(path[0:2, 0], path[0:2, 1], 'blue', lw=4, label="First Edge Segment")
    
    # Direction Markers
    plt.scatter(path[0,0], path[0,1], color='green', s=100, label="Start", zorder=5)
    plt.annotate('', xy=path[1], xytext=path[0], arrowprops=dict(arrowstyle='->', color='blue', lw=2))

    plt.gca().set_aspect('equal')
    plt.legend()
    plt.title("Continuous Path including First Edge")
    plt.show()

if __name__ == "__main__":
    main()