from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Any, Tuple, Optional, Union
import matplotlib.colors as mcolors

# Type alias for clarity
RGB = Tuple[float, float, float]

# =============================================================================
# COLOR UTILITIES
# =============================================================================

def to_rgb(val: RGB | str = None) -> RGB:
    """
    Converts various inputs to an RGB tuple (0.0-1.0).
    Optimized to minimize heavy lookups.
    """
    if val is None:
        # Default Blue (Standard Matplotlib C0)
        return (0.12, 0.46, 0.70)
    if isinstance(val, tuple):
        if len(val) == 3: return val
        if len(val) == 4: return val[:3] # Strip Alpha
    try:
        # mcolors.to_rgb handles strings, hex, and numeric arrays
        return mcolors.to_rgb(val)
    except (ValueError, TypeError):
        return (0.5, 0.5, 0.5) # Fallback Gray

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(frozen=True, slots=True)
class Stroke:
    color: RGB
    width: float = 1.0

@dataclass(frozen=True, slots=True)
class Fill:
    color: RGB

@dataclass(frozen=True, slots=True)
class Style:
    """
    Immutable style definition. 
    Using frozen=True allows styles to be hashed/cached.
    """
    stroke: Optional[Stroke] = None
    fill: Optional[Fill] = None
    opacity: float = 1.0

    def has_fill(self) -> bool:
        return self.fill is not None and self.opacity > 0

    def has_stroke(self) -> bool:
        return (self.stroke is not None and 
                self.stroke.width > 0 and 
                self.opacity > 0)

    def copy(self, **changes) -> Style:
        """Helper for partial updates: style.copy(opacity=0.2)"""
        return replace(self, **changes)

# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def pen(*, color=None, width: float = 1.0, opacity: float = 0.5) -> Style:
    rgb = to_rgb(color)
    return Style(stroke=Stroke(rgb, width), opacity=opacity)

def brush(*, color=None, opacity: float = 0.5, stroke_width: float = 0.0) -> Style:
    rgb = to_rgb(color)
    stroke = Stroke(rgb, stroke_width) if stroke_width > 0 else None
    return Style(stroke=stroke, fill=Fill(rgb), opacity=opacity)