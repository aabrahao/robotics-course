from __future__ import annotations
from dataclasses import replace
from typing import Any, Optional, Dict, Set, Tuple
import uuid

# Assuming these are defined elsewhere in your package
from eml4806.graphics.shape import Geometry
from eml4806.graphics.style import Style
from eml4806.geometry.transform import Transform

class Actor:

    """Represents a renderable object with geometry, style, and transform."""
    
    __slots__ = ('scene', 'uid', 'geometry', 'transform', 'style', 'update_flags')

    _STYLE_KEYS = frozenset({'color', 'alpha', 'visible', 'width', 'fill', 'marker', 'size', 'z_order'})
    _TRANSFORM_KEYS = frozenset({'translation', 'rotation', 'scaling'})

    def __init__(self, scene, uid: uuid.UUID, geometry: Geometry, style: Style, transform: Transform):
        self.scene = scene
        self.uid = uid
        self.geometry = geometry
        self.style = style
        self.transform = transform
        self.update_flags = UpdateFlags()

    def set(self, **kwargs):
        geometry_args, style_args, transform_args = self._split_args(**kwargs)
        # Geometry
        if geometry_args:
            self.geometry = replace(self.geometry, **geometry_args)
            self.update_flags.geometry = True
        # Style
        if style_args:
            if self.style is None:
                self.style = Style()
            self.style.set(**style_args)
            self.update_flags.style = True
        # Transform
        if transform_args:
            if self.transform is None:
                self.transform = Transform()
            self.transform.set(**transform_args) #
            self.update_flags.transform = True
        # Schedule update
        self.scene.flag(self.uid)

    def poll_updates(self) -> Tuple[Optional[Geometry], Optional[Style], Optional[Transform]]:
        """Returns only the components that have changed since the last sync."""
        return (self.geometry if self.update_flags.geometry else None,
                self.style if self.update_flags.style else None,
                self.transform if self.update_flags.transform else None)

    def _split_args(self, **kwargs):
        """Categorizes kwargs into geometry, style, and transform buckets."""
        style_args = {k: v for k, v in kwargs.items() if k in self._STYLE_KEYS}
        transform_args = {k: v for k, v in kwargs.items() if k in self._TRANSFORM_KEYS}
        # Geometry is the "catch-all" for keys not in style or transform
        geometry_args = {k: v for k, v in kwargs.items() 
                     if k not in self._STYLE_KEYS and k not in self._TRANSFORM_KEYS}
        return geometry_args, style_args, transform_args

    def __repr__(self) -> str:
        uid_short = str(self.uid)[:8]
        return (f"Actor<{uid_short}> (Flags: {self.update_flags})\n"
                f"  Type:      {type(self.geometry).__name__}\n"
                f"  Geometry:  {self.geometry}\n"
                f"  Style:     {self.style}\n"
                f"  Transform: {self.transform}")


class UpdateFlags:

    """Compact bitwise flag manager."""

    __slots__ = ('_flags',)
    _FIELDS = {'geometry': 1, 'style': 2, 'transform': 4}

    def __init__(self, **kwargs):
        self._flags = 0
        if kwargs: self.set(**kwargs)

    def set(self, **kwargs):
        for k, v in kwargs.items():
            bit = self._FIELDS.get(k, 0)
            self._flags = (self._flags | bit) if v else (self._flags & ~bit)
        return self

    def __getattr__(self, name):
        if (bit := self._FIELDS.get(name)):
            return bool(self._flags & bit)
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self._FIELDS: self.set(**{name: value})
        else: super().__setattr__(name, value)

    def clear(self): self._flags = 0
    
    @property
    def any(self): return bool(self._flags)

    def __repr__(self):
        active = [k for k, b in self._FIELDS.items() if self._flags & b]
        return f"UpdateFlags({', '.join(active) or 'Clean'})"