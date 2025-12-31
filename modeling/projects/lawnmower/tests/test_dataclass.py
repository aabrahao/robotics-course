from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Union, Optional
import matplotlib.colors as mcolors

RGB = Tuple[float, float, float]

@dataclass(kw_only=True, slots=True, frozen=True)
class Style:
    color: Union[str, RGB] = "blue"
    alpha: float = 1.0
    width: float = 1.0
    fill: bool = True
    marker: str = 'o'
    z_order: int = 1

    @property
    def rgb(self) -> RGB:
        return mcolors.to_rgb(self.color)
    

s = Style()

print('Hello')
print(s)
print(s.color)
print(s.alpha)