import eml4806.geometry as geometry

p1 = geometry.Point()
p2 = geometry.Point()

p2.vector = p1.vector + 1

print(p1.vector)
print(p1)
print(p2)

l1 = geometry.Line(p1, p2)
print(l1)

s1 = geometry.Size(3, 4)
s2 = geometry.Size(1, 1)
s3 = geometry.Size()

s3.vector = s1.vector + 2*s2.vector

print(s1)
print(s2)
print(s3)

s1 = geometry.Rectangle(p1, s1)
print(s1)
