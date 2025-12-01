import numpy as np
import matplotlib.pyplot as plt

# Create a white 8-bit image (grayscale)
rows, cols = 300, 400
img = np.full((rows, cols), 255, dtype=np.uint8)

plt.imshow(img, cmap='gray', vmin=0, vmax=255)
plt.title("White uint8 Image")
plt.axis("off")

plt.show()