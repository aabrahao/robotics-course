import numpy as np

from eml4806.geometry.vector import Vector, toVector, toVectors
from eml4806.geometry.point import Point

v1 = Vector(1,2)
print(v1)
print()

print( Vector() )
print( Vector((1,2)) )
print( Vector([1,2]) )
print( Vector(Point(1,2)) )

x,y = v1
print(f'{x},{y}')
print( np.linalg.norm(v1) )

print( np.cross(v1, v1) )

print( np.sqrt( 2*v1 + (3,3)) )

print(-v1)


print( toVectors([]) )
