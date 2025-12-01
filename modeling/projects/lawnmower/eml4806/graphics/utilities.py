import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as img

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

def toGray8(image):
    """Convert an RGB or grayscale image array to 8-bit monochrome."""
    if image.ndim == 3:  # RGB
        gray = ( 0.299 * image[..., 0] +
                 0.587 * image[..., 1] +
                 0.114 * image[..., 2] )
        return gray.astype(np.uint8)
    else:  # Already grayscale
        return image.astype(np.uint8)
        
def loadImage(filename, convert=toGray8) -> np.ndarray:
    image = img.imread(filename)
    image = np.flipud(image)
    if convert:
        image = convert(image)
    return image
    