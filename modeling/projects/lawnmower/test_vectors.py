import numpy as np

import eml4806.geometry.vector as vector
import eml4806.geometry.pose as pose

from numpy.random import uniform as random

import eml4806.geometry.transform as transform

print( vector.new(1, 2) )
print()
print( vector.new((1, 2, 3, 4, 5), (6, 7, 8, 9, 10)) )

print()
print( vector.ensure((1, 2)) )
print()
print( vector.ensure([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]) )

print()
print( vector.append((1, 2), (1, 2)) )
print()
print( vector.append([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)], (1,2)) )
print()
print( vector.append((1,2), [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]) )
print()
print( vector.append([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)], [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]) )

u = (1, 2)
v = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

print( vector.dot(v,v) )
print( vector.dot(u,u) )

print( vector.length(v) )
print( vector.length(u) )

print( vector.zero(v) )
print( vector.zero(u) )

print( vector.append([],[]))
print( vector.append(v,[]))
print( vector.append([],v))
print( vector.append(None,v))
print( vector.append(v,None))

print( random(1, 10) )
print( random(1, 10, 3) )
print( random(1, 10, (10, 2)) )

p = pose.new(1.0, 2.0, np.pi*0.75)

print( p )
print( pose.position(p) )
print( pose.heading(p) )
print( pose.direction(p) )

path = vector.ensure([
        [2.0, 2.0],
        [0.0, 3.0],
        [2.0, 8.0],
        [8.0, 4.0]
    ])

print(path[3])

print()
for point in path:
    print(point)

print()
for i in range( len(path)-1 ):
    point = path[i]
    next_point = path[i+1]
    print()
    print(point)
    print(next_point)

print()
print(path[-1])

print(len([]))

print()
print( vector.ensure([]) )
print( vector.ensure(None) )

e = []
print( vector.append(e, v) )
print( vector.append(e, u) )

print()
print( vector.ensure([]).shape )
print( vector.ensure(None).shape )
print( vector.ensure([1,2]).shape )
print( vector.ensure(e).shape )
print( vector.ensure(v).shape )
print( vector.ensure(u).shape )

print()
t = transform.Transform.rotation(np.pi/2)
print( t.apply(e) )
print( t.apply(v) )
print( t.apply(u) )
