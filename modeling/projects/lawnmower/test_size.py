import numpy as np

import numpy as np

def evaluateRasterBounds(width: float, height: float, n: int):
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

def rasterize(rows: int, cols: int):
    return np.zeros((rows, cols), dtype=np.uint8)


def rasterize(rows: int, cols: int):
    return np.zeros((rows, cols), dtype=np.uint8)

print( evaluateRasterBounds(12.0, 9.0, 1000) )
print( evaluateRasterBounds(12.0, 12.0, 1000) ) 
