from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np

from eml4806.geometry.transform import Transform
from eml4806.graphics.style import Style

@dataclass(kw_only=True, slots=True, frozen=True)
class Geometry:
    """Base class for all geometric primitives."""
    pass

@dataclass(kw_only=True, slots=True, frozen=True)
class Points(Geometry):
    """Collection of disconnected 2D points."""
    points: np.ndarray  # N x 2

@dataclass(kw_only=True, slots=True, frozen=True)
class Polyline(Geometry):
    """Open connected line segments."""
    points: np.ndarray  # N x 2

@dataclass(kw_only=True, slots=True, frozen=True)
class Polygon(Geometry):
    """Closed connected shape."""
    points: np.ndarray  # N x 2

@dataclass(kw_only=True, slots=True, frozen=True)
class Rectangle(Geometry):
    """Axis-aligned rectangle (use transform for rotation)."""
    center: np.ndarray
    size: np.ndarray  # (width, height)

@dataclass(kw_only=True, slots=True, frozen=True)
class Circle(Geometry):
    """Circle defined by center and radius."""
    center: np.ndarray
    radius: float

@dataclass(kw_only=True, slots=True, frozen=True)
class Triangle(Geometry):
    """Equilateral triangle pointing upward (use transform for rotation)."""
    center: np.ndarray
    base: float
    height: float

@dataclass(kw_only=True, slots=True, frozen=True)
class Grid(Geometry):
    """2D grid/occupancy map/image."""
    data: np.ndarray
    origin: np.ndarray = field(default_factory=lambda: np.zeros(2))
    resolution: float = 1.0

@dataclass(kw_only=True, slots=True, frozen=True)
class Arrow(Geometry):
    """Directed arrow/vector."""
    origin: np.ndarray
    direction: np.ndarray

@dataclass(kw_only=True, slots=True, frozen=True)
class Axes(Geometry):
    """2D coordinate frame (X-axis: red, Y-axis: green)."""
    origin: np.ndarray
    scale: float = 1.0