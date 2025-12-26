import numpy as np
import matplotlib.pyplot as plt

from eml4806.geometry.vector import vectors

def generate_raster_path(polygon, d):
    """Generates a continuous zigzag raster path parallel to the first edge."""
    # 2D
    vertices = polygon[:, :2]
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
    path = np.array(path_points) @ rev_R.T
    return vectors(path)