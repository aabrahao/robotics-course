from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Tuple, Union, Any, Dict
import matplotlib.colors as mcolors

# Type aliases
RGB = Tuple[float, float, float]
RGBA = Tuple[float, float, float, float]

@dataclass(slots=True)
class Style:
    """
    High-performance Style configuration.
    Zero dependencies (no Pydantic), minimal overhead.
    """
    # Define fields with defaults
    color: Union[str, RGB] = (0.12, 0.46, 0.70)
    alpha: float = 0.5
    visible: bool = True
    zorder: int = 1
    width: float = 3.0
    fill: bool = True
    marker: str = None
    size: float = 5.0

    def __post_init__(self):
        """Validate all fields immediately after initialization."""
        self.color = self._validate_color(self.color)
        
        if not (0.0 <= self.alpha <= 1.0):
            raise ValueError(f"alpha must be 0-1, got {self.alpha}")
        if self.width < 0:
            raise ValueError(f"width must be non-negative, got {self.width}")
        if self.size < 0:
            raise ValueError(f"size must be non-negative, got {self.size}")

    @staticmethod
    def _validate_color(val: Any) -> RGB:
        try:
            return mcolors.to_rgb(val) if val is not None else (0.12, 0.46, 0.70)
        except Exception as e:
            raise ValueError(f"Invalid color '{val}': {e}")

    def rgb(self) -> RGB:
        return self.color

    def rgba(self) -> RGBA:
        return (*self.color, self.alpha)

    def set(self, **kwargs) -> Style:
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.__post_init__()  # Re-run validation logic
        return self

    def __repr__(self) -> str:
        # Get a temporary instance to compare against defaults
        default_instance = Style.__new__(Style)
        # Note: Default values for dataclasses are stored in the fields
        changed = []
        for f in fields(self):
            val = getattr(self, f.name)
            if val != f.default:
                changed.append(f"{f.name}={val!r}")
        return f"Style({', '.join(changed)})" if changed else "Style()"