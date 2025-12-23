import numpy as np
from vispy import app, scene
from vispy.visuals.transforms import STTransform

# ---------------------------------------------------------
# Data: sin(x)
# ---------------------------------------------------------
x = np.linspace(-2*np.pi, 2*np.pi, 600)
y = np.sin(x)

# Create points for line plot
pts = np.column_stack([x, y])

# ---------------------------------------------------------
# Desired world ranges
# ---------------------------------------------------------
x_min, x_max = x.min(), x.max()
y_min, y_max = -1.5, 1.5

# ---------------------------------------------------------
# Create canvas and view
# ---------------------------------------------------------
canvas = scene.SceneCanvas(keys='interactive', size=(1100, 650), 
                          show=True, bgcolor='white')
view = canvas.central_widget.add_view()

# ---------------------------------------------------------
# Add the sin(x) curve
# ---------------------------------------------------------
line = scene.visuals.Line(pts, color='blue', width=3, parent=view.scene)

# ---------------------------------------------------------
# Add grid and axes
# ---------------------------------------------------------
grid = scene.visuals.GridLines(parent=view.scene, color=(0.5, 0.5, 0.5, 0.3))

# Add axis visuals
x_axis = scene.AxisWidget(orientation='bottom', 
                         axis_label='x',
                         axis_font_size=12,
                         axis_label_margin=50,
                         tick_label_margin=5)
y_axis = scene.AxisWidget(orientation='left',
                         axis_label='sin(x)',
                         axis_font_size=12,
                         axis_label_margin=50,
                         tick_label_margin=5)

x_axis.stretch = (1, 0.1)
y_axis.stretch = (0.1, 1)

grid_widget = canvas.central_widget.add_grid(margin=10)
grid_widget.padding = 6
grid_widget.add_widget(x_axis, row=1, col=0)
grid_widget.add_widget(y_axis, row=0, col=0)
grid_widget.add_widget(view, row=0, col=1)

# ---------------------------------------------------------
# Setup camera with fixed bounds
# ---------------------------------------------------------
view.camera = scene.PanZoomCamera(aspect=1)
view.camera.set_range(x=(x_min, x_max), y=(y_min, y_max), margin=0)

# Link the axis widgets to the view
x_axis.link_view(view)
y_axis.link_view(view)

# ---------------------------------------------------------
# Run the application
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run()