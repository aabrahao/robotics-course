from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
import uuid
from matplotlib.transforms import Affine2D
from typing import Any, Optional, Dict, Union

from eml4806.graphics.shape import Geometry, Points, Polyline, Polygon, Rectangle, Circle, Triangle, Arrow, Axes
from eml4806.graphics.style import Style
from eml4806.geometry.transform import Transform

class Matplotlib:

    __slots__ = ('figure', 'ax', 'artists')
    
    def __init__(self):
        self.artists: Dict[uuid.UUID, Any] = {}
        plt.ion()
        self.figure, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.ax.set_autoscale_on(False)

    def __del__(self):
        plt.ioff()
        plt.show()

    def __contains__(self, uid: uuid.UUID) -> bool:
        """Enables syntax: 'if uid in renderer:'"""
        return uid in self.artists

    def remove(self, uid: uuid.UUID):
        if artist := self.artists.pop(uid, None):
            if isinstance(artist, (list, tuple)): 
                for a in artist: a.remove()
            else: artist.remove()

    def create(self, uid: uuid.UUID, geometry: Geometry, style: Style, transform: Transform):
        # Renderer decides the Matplotlib primitive based on Geometry type
        if isinstance(geometry, (Circle, Polygon, Triangle, Rectangle)):
            artist = self.ax.fill([], [], closed=True)
        elif isinstance(geometry, Points):
            artist = self.ax.plot([], [], 'o')
        elif isinstance(geometry, Polyline):
            artist = self.ax.plot([], [], '-')
        elif isinstance(geometry, Arrow):
            artist = self.ax.quiver([0], [0], [0], [0], angles='xy', scale_units='xy', scale=1)
        elif isinstance(geometry, Axes):
            artist = self.ax.quiver([0, 0], [0, 0], [0, 0], [0, 0], angles='xy', scale_units='xy', scale=1)
        else:
            return
        self.artists[uid] = artist
        self.update(uid, geometry, style, transform)

    def update(self, uid: uuid.UUID, geometry: Geometry, style: Style, transform: Transform):
        artist = self.artists.get(uid)
        if not artist: 
            return
        # Plot and Fill return lists; Quiver returns a single object
        artist = artist[0] if isinstance(artist, (list, tuple)) else artist
        # Update actor
        if geometry: self._update_geometry(artist, geometry)
        if style: self._update_style(artist, style)
        if transform: self._update_transform(artist, transform)

    def _update_geometry(self, artist: Any, geometry: Geometry):
        """Uniform data extraction for data-only Geometry classes."""
        # 1. Fill-based Shapes
        if isinstance(geometry, Polygon):
            artist.set_xy(geometry.points)
        elif isinstance(geometry, Triangle):
            h = geometry.size * np.sqrt(3) / 2
            v = np.array([[0, 2*h/3], [-geometry.size/2, -h/3], [geometry.size/2, -h/3]]) + geometry.center
            artist.set_xy(v)
        elif isinstance(geometry, Rectangle):
            w, h = geometry.size
            xy = geometry.center - geometry.size / 2
            v = np.array([xy, [xy[0]+w, xy[1]], [xy[0]+w, xy[1]+h], [xy[0], xy[1]+h]])
            artist.set_xy(v)
        elif isinstance(geometry, Circle):
            theta = np.linspace(0, 2*np.pi, 72, endpoint=False)
            x = geometry.center[0] + geometry.radius * np.cos(theta)
            y = geometry.center[1] + geometry.radius * np.sin(theta)
            artist.set_xy(np.column_stack([x, y]))
        # 2. Plot-based Paths
        elif isinstance(geometry, (Polyline, Points)):
            artist.set_data(geometry.points[:, 0], geometry.points[:, 1])
        # 3. Quiver-based Vectors
        elif isinstance(geometry, Arrow):
            o = geometry.origin
            u, v = geometry.direction
            artist.set_offsets(o)
            artist.set_UVC(u, v)
        elif isinstance(geometry, Axes):
            o = geometry.origin
            s = geometry.scale
            artist.set_offsets((o, o))
            artist.set_UVC([s, 0], [0, s])

    def _update_style(self, artist: Any, style: Style):
        props = {}
        if style.color is not None:
            if hasattr(artist, 'set_facecolor'):
                props['facecolor'] = style.color
                props['edgecolor'] = style.color
            else:
                props['color'] = style.color
        if style.alpha is not None and hasattr(artist, 'set_alpha'): props['alpha'] = style.alpha
        if style.visible is not None and hasattr(artist, 'set_visible'): props['visible']= style.visible
        if style.zorder is not None and hasattr(artist, 'set_zorder'): props['zorder'] = style.zorder
        if style.width is not None and hasattr(artist, 'set_linewith'): props['linewidth']= style.width
        if style.fill is not None and hasattr(artist, 'set_fill'): props['fill']= style.fill
        if style.marker is not None and hasattr(artist, 'set_marker'): props['marker'] = style.marker
        if style.size is not None and hasattr(artist, 'set_markersize'): props['markersize']= style.size
        artist.set(**props)
    
    def _update_transform(self, artist: Any, transform: Transform):
        tx, ty = transform.translation()
        r = transform.rotation()
        sx, sy = transform.scaling()
        m = Affine2D().scale(sx, sy).rotate(r).translate(tx, ty)
        artist.set_transform(m + self.ax.transData)

    def render(self):
        self.figure.canvas.draw_idle()
        self.figure.canvas.flush_events()

    def set_viewport(self, x: float, y: float, w: float, h: float):
        self.ax.set_xlim(x, x + w)
        self.ax.set_ylim(y, y + h)