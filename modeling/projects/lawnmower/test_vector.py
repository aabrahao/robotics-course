import eml4806.geometry.vector as vector

print( vector.vector(1, 2) )
print()
print( vector.vector((1, 2, 3, 4, 5), (6, 7, 8, 9, 10)) )

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

v = (1, 2)
p = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

print( vector.dot(v,v) )
print( vector.dot(p,p) )

print( vector.length(v) )
print( vector.length(p) )

print( vector.zero(v) )
print( vector.zero(p) )

print(vector.scalar(v))
print(vector.scalar(p))

#print( vector.append([],[]))
#print( vector.append(v,[]))
#print( vector.append([],v))
print( vector.append(None,v))
print( vector.append(v,None))
