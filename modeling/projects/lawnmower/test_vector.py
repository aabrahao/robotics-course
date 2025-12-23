import numpy as np
import eml4806.geometry.vector as vc
import eml4806.geometry.vectors as vcs


print( np.linalg.norm((1,2,2)) )
print( np.linalg.norm([1,2,2]) )


print( vc.vector() )
print( vc.vector(1,2) )
print( vc.vector(1,2,3) )
print( vc.vector([1,2]) )
print( vc.vector((1,2)) )
print( vc.vector([1,2,3]) )
print( vc.vector((1,2,3)) )
print( vc.vector(np.array([1,2,3])) )
print( vc.vector(np.array((1,2,3))) )

#print( vc.vector(1) )
#print( vc.vector(None) )

# vectors
x = np.linspace(1,3,3)
y = np.linspace(1,3,3)
z = np.linspace(1,3,3)

print( vcs.vectors() )
print( vcs.vectors(vcs.vectors()) )
print( vcs.vectors([]) )
print( vcs.vectors(vc.vector()) )
print( vcs.vectors((1,2)) )
print( vcs.vectors((1,2,3)) )
print( vcs.vectors([1,2]) )
print( vcs.vectors([1,2,3]) )

print( vcs.vectors(x, y) )

v = vcs.vectors(x,y,z)

x,y,z = vcs.split(v)

print(x,y,z)
