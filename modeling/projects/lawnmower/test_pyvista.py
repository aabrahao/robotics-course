import pyvista as pv
import numpy as np

# Create a plotter
plotter = pv.Plotter()

# Define square vertices (centered at origin)
size = 2.0
square_points = np.array([
    [-size/2, -size/2, 0],
    [size/2, -size/2, 0],
    [size/2, size/2, 0],
    [-size/2, size/2, 0]
])

# Create lines connecting the points
lines = np.hstack([
    [2, 0, 1],
    [2, 1, 2],
    [2, 2, 3],
    [2, 3, 0]
])

# Initial square
square = pv.PolyData(square_points, lines=lines)
actor = plotter.add_mesh(square, color='red', line_width=5)

# Set up 2D view with parallel projection
plotter.view_xy()  # Look down at XY plane
plotter.camera.parallel_projection = True  # Enable parallel projection (no perspective)
plotter.camera.parallel_scale = 1.5  # Adjust zoom for parallel projection

# Add a reference grid
plotter.show_grid()

# Open the plotter
plotter.show(interactive_update=True, auto_close=False)

# Animation loop
for i in range(360):
    # Calculate rotation angle
    angle = np.radians(i * 2)
    
    # Rotation matrix around z-axis
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])
    
    # Rotate the square points
    rotated_points = square_points @ rotation_matrix.T
    
    # Update the mesh points
    square.points = rotated_points
    
    # Update the render
    plotter.update()

plotter.close()