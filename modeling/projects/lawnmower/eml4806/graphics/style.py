from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from typing import Any

#######################################################

def pen(color=(0.0,0.0,0.0), width=1.0, opacity=0.5):
    return Style(stroke=Stroke(color, width), opacity=opacity)
    
def brush(color=(0.0,0.0,0.0), width=1.0, opacity=0.5):
    return Style(stroke=Stroke(color, width), fill=Fill(color), opacity=opacity)


@dataclass
class Stroke:

    color: Any = (0.0,0.0,0.0)
    width: float = 1.0

    def clone(self):
        return Stroke(color=self.color, width=self.width)


#######################################################


@dataclass
class Fill:

    color: Any = (0.0,0.0,0.0)

    def clone(self):
        return Fill(color=self.color)


#######################################################


class Style:

    def __init__(self, stroke: Stroke = None, fill: Fill = None, opacity = 0.5):
        self.stroke = stroke
        self.fill = fill
        self.opacity = float(opacity)

    def has_fill(self):
        return self.fill is not None and self.opacity > 0.0

    def has_stroke(self):
        return (self.stroke is not None and self.opacity > 0.0 and self.stroke.width > 0.0)

    def clone(self):
        return Style(
            stroke=self.stroke.clone() if self.stroke is not None else None,
            fill=self.fill.clone() if self.fill is not None else None,
            opacity=self.opacity,
        )
  