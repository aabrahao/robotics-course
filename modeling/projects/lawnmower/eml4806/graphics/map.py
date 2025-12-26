
from __future__ import annotations

from numpy import pi, sin, cos

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as img

from eml4806.geometry.rectangle import Rectangle

####################################################################################

from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection

from eml4806.robot.tool import Blade, BladeState

class CoverageMap:

    __slots__ = ('_workspace', '_high_collection', '_low_collection', '_high_patches', '_low_patches')

    def __init__(self, workspace):
        self._workspace = workspace

        self._high_collection = PatchCollection([], facecolors=Blade.color(BladeState.HIGH), alpha=1.0, zorder=-20)
        self._low_collection = PatchCollection([], facecolors=Blade.color(BladeState.LOW), alpha=1.0, zorder=-10)
        workspace._ax.add_collection(self._high_collection)
        workspace._ax.add_collection(self._low_collection)
        
        self._high_patches = []
        self._low_patches = []

    def cut(self, x, y, r, state):
        if state == BladeState.OFF:
            return
        circle = Circle((x, y), radius=r)
        if state == BladeState.LOW:
            self._low_patches.append(circle)
            self._low_collection.set_paths(self._low_patches)
        else:
            self._high_patches.append(circle)
            self._high_collection.set_paths(self._high_patches)

    def clear(self):
        self._high_collection.set_paths([])
        self._low_collection.set_paths([])
        self._high_patches = []
        self._low_patches = [] 

##########################################################################

class RasterMap(Rectangle):

    __slots__ = ("_workspace", "_artist", "_image")

    def __init__(self, workspace, position=None, size=None, image=None, pixels=1000):
        self._workspace = workspace
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
            (rows, cols), (width, height) = image_bounds(w, h, n)
            self._image = make_map(rows, cols, 255)
            self._size = (width, height)
            return                
        # case 2 — a file path (string)
        if isinstance(image, str):
            self._image = load_image(image)
            return
        # case 3 — already a NumPy image
        if isinstance(image, np.ndarray):
            self._image = image
            return
        raise TypeError(f"Unsupported image type: {type(image)}")

    def _ax(self):
        return self._workspace._ax
    
    def _make(self):
        x, y, w, h = self.rectangle()
        self._artist = self._ax().imshow(self._image, cmap='gray', 
                                         vmin=0, vmax=255, 
                                         origin='upper', extent=[x, x+w, y+h, y])

    def update(self):
        if self._artist:
            self._artist.set_data(self._image)
            self._artist.set_extent(self.extent())
    
    def clear(self):
        rows = self._image.shape[0]
        cols = self._image.shape[1]
        self._image = make_map(rows, cols, 255)
        self.update()

    def _imageSize(self):
        h = self._image.shape[0]
        w = self._image.shape[1]
        return w, h
        
    def _to_pixel(self, x, y, map_distance=False):
        """RasterMap world coordinates (x, y) to pixel indices (u, v)"""
        wi, hi = self._imageSize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        u = (x - xr) / wr*(wi - 1)
        v = (y - yr) / hr*(hi - 1)
        return u, v # (col, row)

    def _from_pixel(self, u, v, map_distance=False):
        """RasterMap pixel indices (u, v) back to world coordinates (x, y)."""
        wi, hi = self._imageSize()
        xr, yr, wr, hr = self.rectangle()
        if map_distance:
            xr = 0.0
            yr = 0.0
        x = xr + u / (wi - 1)*wr
        y = yr + v / (hi - 1)*hr
        return x, y
    
    def _image_circle(self, u, v, r, value):
        """Circle mask in pixel (w,v), r"""
        m = self._image
        rows, cols = m.shape
        y, x = np.ogrid[:rows, :cols]
        mask = (y - u)**2 + (x - v)**2 <= r**2
        m[mask] = value
        self.update()
        
    def circle(self, x, y, r, value):
        u, v = self._to_pixel(x, y)
        s, _ = self._to_pixel(r, r, map_distance=True)
        self._image_circle(v, u, s, value)

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

#####################################################################
# Helpers

def image_bounds(width: float, height: float, n: int):
    """
     Compute the raster (pixel-grid) bounds for a world-space rectangle.
    - width, height: world-space dimensions (floats)
    - n: number of pixels assigned to the larger side
    - preserves aspect ratio
    - uses square pixels
    - returns:
        (rows, cols)      : integer pixel resolution
        (width_opt, height_opt) : world-space size represented after rounding
    """
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if n <= 0:
        raise ValueError("n must be a positive integer")

    larger = max(width, height)
    scale = n / larger  # pixels per world unit

    cols = int(width  * scale + 0.5)  # width  -> pixel columns
    rows = int(height * scale + 0.5)  # height -> pixel rows

    pixel_size = 1.0 / scale

    width  = cols * pixel_size
    height = rows * pixel_size

    return (rows, cols), (width, height)

def make_map(rows: int, cols: int, value):
    return np.full((rows, cols), value, dtype=np.uint8)

def to_gray8(image):
    """Convert an RGB or grayscale image array to 8-bit monochrome."""
    if image.ndim == 3:  # RGB
        gray = ( 0.299 * image[..., 0] +
                 0.587 * image[..., 1] +
                 0.114 * image[..., 2] )
        return gray.astype(np.uint8)
    else:  # Already grayscale
        return image.astype(np.uint8)
        
def load_image(filename, convert=to_gray8) -> np.ndarray:
    image = img.imread(filename)
    image = np.flipud(image)
    if convert:
        image = convert(image)
    return image