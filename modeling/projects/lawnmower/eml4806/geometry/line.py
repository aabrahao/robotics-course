import math

from eml4806.geometry.vector import vector

# Point: p
# Line: (p1, p2)

def distance(p1, p2, p):
    """
    Returns the perpendicular distance from point p(x, y)
    to the line defined by points p1(x1, y1) and p2(x2, y2).
    """
    # Line
    x1, y1 = p1
    x2, y2 = p2
    # Point
    x, y = p
    # Line vector components
    A = x2 - x1
    B = y2 - y1
    # Cross product magnitude (2D)
    cross = abs(A * (y1 - y) - (x1 - x) * B)
    # Length of the line segment direction vector
    length = math.hypot(A, B)
    if length == 0:
        raise ValueError("The two points defining the line must not be identical.")
    return cross / length

def closest(p1, p2, p):
    """
    Closest point on the INFINITE line through p1(x1, y1) and p2(x2, y2)
    to the point p(x, y), returning pc(xc, yc).
    """
    # Line
    x1, y1 = p1
    x2, y2 = p2
    # Point
    x, y = p
    # Distance
    dx = x2 - x1
    dy = y2 - y1
    # Degenerate line (both points the same)
    if dx == 0 and dy == 0:
        raise ValueError("The line is undefined because (x1, y1) == (x2, y2)")
    # Use float math explicitly (helps if you pass ints in some environments)
    dx2_dy2 = float(dx*dx + dy*dy)
    t = ((x - x1) * dx + (y - y1) * dy) / dx2_dy2
    # NOTE: no clamping of t → this is an INFINITE line
    xc = x1 + t * dx
    yc = y1 + t * dy
    return vector(xc, yc)