
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from numpy import pi, sin, cos, clip, array

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img

from eml4806.geometry.vector import Vector, toVector, split
from eml4806.geometry.angle import wrap

from eml4806.geometry.rectangle import Rectangle

from eml4806.graphics.utilities import loadImage, toGray8, evaluateRasterBounds, rasterize

class Map(Rectangle):

    #__slots__ = ("_position", "_size")

    def __init__(self, workspace, position=None, size=None, image=None, pixels=1000):
        self._ax = workspace._ax
        self._artist = None
        # Fill workspace
        if position is None or size is None:
            x, y, w, h = workspace.viewport()
            if position is None:
                position = (x,y)
            if size is None:
                size = (w,h)
        super().__init__(position, size)
        self._load(image, pixels)
        self._adjust()
        self._make()

    def _load(self, image, pixels):
        # case 1 — rasterized pixels per largest length
        if image is None:
            n = pixels
            _, _, w, h = self.rectangle()
            (rows, cols), (width, height) = evaluateRasterBounds(w, h, n)
            self._image = rasterize(rows, cols, 255)
            self._size = (width, height)
            return                
        # case 2 — a file path (string)
        if isinstance(image, str):
            self._image = loadImage(image)
            return
        # case 3 — already a NumPy image
        if isinstance(image, np.ndarray):
            self._image = image
            return
        raise TypeError(f"Unsupported image type: {type(image)}")

    def _make(self):
        x, y, w, h = self.rectangle()
        self._artist = self._ax.imshow(self._image, cmap='gray', vmin=0, vmax=255, origin='upper', extent=[x, x+w, y+h, y] )

    def update(self):
        if self._artist:
            self._artist.set_data(self._image)
            self._artist.set_extent(self.extent())
    
    def clear(self):
        rows = self._image.shape[0]
        cols = self._image.shape[1]
        self._image = rasterize(rows, cols, 255)
        self.update()

    def _imageSize(self):
        h = self._image.shape[0]
        w = self._image.shape[1]
        return w, h
        
    def _toPixel(self, x, y, map_distance=False):
        """Map world coordinates (x, y) to pixel indices (u, v)"""
        wi, hi = self._imageSize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        u = (x - xr) / wr*(wi - 1)
        v = (y - yr) / hr*(hi - 1)
        return u, v # (col, row)

    def _fromPixel(self, u, v, map_distance=False):
        """Map pixel indices (u, v) back to world coordinates (x, y)."""
        wi, hi = self._imageSize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        x = xr + u / (wi - 1)*wr
        y = yr + v / (hi - 1)*hr
        return x, y
    
    def _imageCircleMask(self, u, v, r, func):
        """Circle mask in pixel (w,v), r"""
        m = self._image
        rows, cols = m.shape
        y, x = np.ogrid[:rows, :cols]
        mask = (y - u)**2 + (x - v)**2 <= r**2
        m[mask] = func( m[mask] )
        self.update()
        
    def circle(self, x, y, r, func=lambda x: 0.5*x):
        u, v = self._toPixel(x, y)
        s, _ = self._toPixel(r, r, map_distance=True)
        self._imageCircleMask(v, u, s, func)

    def _adjust(self):
        """
        Fits inside viewport
        """
        # Pixes
        wi, hi = self._imageSize()  
        if wi <= 0 or hi <= 0:
            return
        # Drawing are
        xr, yr, wr, hr = self.rectangle()
        if wr <= 0 or hr <= 0:
            return
        # Scale
        li = max(wi, hi)
        lr = min(wr, hr)
        if li == 0 or lr <= 0:
            return
        scale = lr / li
        w = wi*scale
        h = hi*scale
        self._size = (w, h)
  