import numpy as np

from eml4806.geometry.transform import Transform
from eml4806.graphics.scene import Scene
from eml4806.graphics.shape import Circle, Rectangle
from eml4806.graphics.style import Style
from eml4806.geometry.vector import as_vector, as_vectors

def main():

    scene = Scene(origin=as_vector(0,0), size=as_vector(10, 10))

    r = scene.rectangle(center=(2,2), size=(1,2), color='red', fill=True, rotation=0.3, alpha=0.5)
    print(r)
    
    c = scene.circle(center=(5,5), radius=1.0, color='orange', alpha=0.5)
    print(c)

    x = np.linspace(0, 2*np.pi, 20)
    y = np.sin(x)
    p1 = scene.polygon(points=as_vectors(x,y), translation=(0,8))
    p2 = scene.polyline(points=as_vectors(x,y), translation=(0,5), color='pink', width=5, alpha=0.5)
    
    l = scene.line(start=(1,2), end=(8,8), color='green', width=4, alpha=0.5)
    p3 = scene.points(points=as_vectors(x,y), translation=(0,3), color='green', width=4, alpha=0.5, size=10)

    a1 = scene.arrow(origin=(8,2), direction=(-4,4), color='cyan', alpha=0.5)

    a2 = scene.axes(origin=(5,5), scale=1, color='blue', alpha=0.5)

    r.set(visible=False)
    r.set(visible=True)

    angle = 0.0
    while True:
        r.set(rotation=angle)
        print(r)
        scene.update()
        angle += 0.01
    
if __name__ == "__main__":
    main()





