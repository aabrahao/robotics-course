import math

def distance(x, y, x1, y1, x2, y2):
    """
    Returns the perpendicular distance from point (x, y)
    to the line defined by points (x1, y1) and (x2, y2).
    """
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

def closest(xp, yp, x1, y1, x2, y2):
    """
    Closest point on the INFINITE line through (x1, y1)-(x2, y2)
    to the point (xp, yp).
    Returns (xc, yc).
    """
    dx = x2 - x1
    dy = y2 - y1
    # Degenerate line (both points the same)
    if dx == 0 and dy == 0:
        raise ValueError("The line is undefined because (x1, y1) == (x2, y2)")
    # Use float math explicitly (helps if you pass ints in some environments)
    dx2_dy2 = float(dx*dx + dy*dy)
    t = ((xp - x1) * dx + (yp - y1) * dy) / dx2_dy2
    # NOTE: no clamping of t → this is an INFINITE line
    xc = x1 + t * dx
    yc = y1 + t * dy
    return xc, yc

def orient(xp, yp, x1, y1, x2, y2):
    value = (x2 - x1)*(yp - y1) - (y2 - y1)*(xp - x1)
    if value > 0:
        return "above"
    elif value < 0:
        return "below"
    else:
        return "on"