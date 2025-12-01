
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

def toGray8(image):
    """Convert an RGB or grayscale image array to 8-bit monochrome."""
    if image.ndim == 3:  # RGB
        gray = ( 0.299 * image[..., 0] +
                 0.587 * image[..., 1] +
                 0.114 * image[..., 2] )
        return gray.astype(np.uint8)
    else:  # Already grayscale
        return image.astype(np.uint8)

class Map(Rectangle):

    #__slots__ = ("_position", "_size")

    def __init__(self, workspace, position, size, image):
        self._ax = workspace.axis
        self._artist = None
        self._image = image
        super().__init__(position, size)
        self.adjust()
        self.make()

    def make(self):
        x, y, w, h = self.rectangle()
        self._artist = self._ax.imshow(self._image, cmap='gray', origin='upper', extent=[x, x+w, y+h, y] )

    def update(self):
        if self._artist:
            self._artist.set_data(self._image)
            self._artist.set_extent(self.extent())

    def isize(self):
        h = self._image.shape[0]
        w = self._image.shape[1]
        return w, h
    
    def toPixel(self, x, y, map_distance=False):
        """Map world coordinates (x, y) to pixel indices (u, v)"""
        wi, hi = self.isize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        u = (x - xr) / wr*(wi - 1)
        v = (y - yr) / hr*(hi - 1)
        return u, v # (col, row)

    def fromPixel(self, u, v, map_distance=False):
        """Map pixel indices (u, v) back to world coordinates (x, y)."""
        wi, hi = self.isize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        x = xr + u / (wi - 1)*wr
        y = yr + v / (hi - 1)*hr
        return x, y
    
    def icircle(self, u, v, r, func):
        """Circle mask in pixel (w,v), r"""
        m = self._image
        rows, cols = m.shape
        y, x = np.ogrid[:rows, :cols]
        mask = (y - u)**2 + (x - v)**2 <= r**2
        m[mask] = func( m[mask] )
        self.update()
        
    def circle(self, x, y, r, func=lambda x: 0.5*x):
        u, v = self.toPixel(x, y)
        s, _ = self.toPixel(r, r, map_distance=True)
        self.icircle(v, u, s, func)

    def viewport(self):
        """Actual artist rectangle"""
        xmin, xmax = self._ax.get_xlim()
        ymin, ymax = self._ax.get_ylim()
        return xmin, ymin, xmax-xmin, ymax-ymin

    def adjust(self):
        """
        Fits inside viewport
        """
        # Pixes
        wi, hi = self.isize()  
        if wi <= 0 or hi <= 0:
            return
        # Drawing are
        xr, yr, wr, hr = self.viewport()
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
        self.size = (w, h)

    @classmethod
    def load(cls, filename, convert=toGray8) -> np.ndarray:
        image = img.imread(filename)
        image = np.flipud(image)
        if convert:
            image = convert(image)
        return image


    


     


