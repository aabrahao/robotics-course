from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# =============================================================================
# COLOR UTILITIES
# =============================================================================

def color(val=None) -> tuple:
    """Normalizes color input into a standard (R, G, B) tuple. No caching."""
    if type(val) is tuple:
        return val

    if val is None:
        try:
            c = next(iter(plt.rcParams['axes.prop_cycle']))['color']
            return mcolors.to_rgb(c)
        except (KeyError, StopIteration):
            return (0.121, 0.466, 0.705)

    try:
        return mcolors.to_rgb(val)
    except (ValueError, TypeError):
        return (0.5, 0.5, 0.5)

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass(slots=True)
class Stroke:
    color: Any
    width: float

    def clone(self) -> Stroke:
        return Stroke(self.color, self.width)

@dataclass(slots=True)
class Fill:
    color: Any

    def clone(self) -> Fill:
        return Fill(self.color)

class Style:
    __slots__ = ('stroke', 'fill', 'opacity')

    def __init__(self, stroke: Optional[Stroke], fill: Optional[Fill], opacity: float):
        """No defaults: all parameters must be provided explicitly."""
        self.stroke = stroke
        self.fill = fill
        self.opacity = float(opacity)

    def __repr__(self) -> str:
        s_part = f"stroke={self.stroke}" if self.stroke else "no stroke"
        f_part = f"fill={self.fill}" if self.fill else "no fill"
        return f"Style({s_part}, {f_part}, opacity={self.opacity})"

    def hasFill(self) -> bool:
        return self.opacity > 0.0 and self.fill is not None

    def hasStroke(self) -> bool:
        return (self.opacity > 0.0 and 
                self.stroke is not None and 
                self.stroke.width > 0.0)

    def clone(self) -> Style:
        return Style(
            stroke=self.stroke.clone() if self.stroke else None,
            fill=self.fill.clone() if self.fill else None,
            opacity=self.opacity
        )

# =============================================================================
# FACTORY FUNCTIONS (These provide the defaults)
# =============================================================================

def pen(color_val=None, width=1.0, opacity=0.5) -> Style:
    """Explicitly builds a Style with a Stroke."""
    c = color(color_val)
    w = float(width)
    o = float(opacity)
    return Style(Stroke(c, w), None, o)
    
def brush(color_val=None, width=1.0, opacity=0.5) -> Style:
    """Explicitly builds a Style with both Stroke and Fill."""
    c = color(color_val)
    w = float(width)
    o = float(opacity)
    return Style(Stroke(c, w), Fill(c), o)