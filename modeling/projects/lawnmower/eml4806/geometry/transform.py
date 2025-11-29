import numpy as np

import eml4806.geometry.vector as vector

#########################################################

class Transform:

    def __init__(self, position=(0.0, 0.0), orientation=0.0, scaling=(1.0, 1.0)):
        self._position = vector.ensureOne(position)
        self._orientation = float(orientation)
        self._scaling = vector.ensureOne(scaling)

    @property
    def matrix(self):
        return Transform.to_matrix(self)

    @property
    def inverse(self):
        return np.linalg.inv(self.matrix)

    def clone(self):
        return Transform(self._position.copy(), self._orientation, self._scaling.copy())

    def translate(self, d):
        e = vector.ensureOne(d)
        self._position += e

    def rotate(self, da):
        self._orientation += float(da)

    def scale(self, s):
        if np.isscalar(s): 
            s = (s, s)
        self._scaling *= s

    def apply(self, points, inverse=False):
        p = vector.ensureMany(points)
        # Extract transform components
        tx, ty = self._position
        rot = self._orientation
        sx, sy = self._scaling
        if not inverse:
            # Scale
            x = p[:, 0]*sx
            y = p[:, 1]*sy
            # Rotate
            c = np.cos(rot)
            s = np.sin(rot)
            out_x = c * x - s * y
            out_y = s * x + c * y
            # Translate
            out_x += tx
            out_y += ty
        else:
            # Un-translate
            x = p[:, 0] - tx
            y = p[:, 1] - ty
            # Un-rotate
            c = np.cos(rot)
            s = np.sin(rot)
            out_x = c * x + s * y
            out_y = -s * x + c * y
            # Un-scale
            out_x /= sx
            out_y /= sy
        out = vector.new(out_x, out_y)
        if len(out) == 1:
            return out[0]
        return out

    @classmethod
    def compound(cls, M1, M2):
        M = M1.matrix @ M2.matrix
        return Transform.from_matrix(M)

    @classmethod
    def identity(cls):
        return cls()

    @classmethod
    def translation(cls, x, y):
        return cls((x, y), 0.0, (1.0, 1.0))

    @classmethod
    def rotation(cls, angle):
        return cls((0.0, 0.0), angle, (1.0, 1.0))

    @classmethod
    def scale(cls, s):
        if np.isscalar(s): 
            s = (s, s)
        return cls((0.0, 0.0), 0.0, s)

    @classmethod
    def from_matrix(cls, M):
        M = np.asarray(M, dtype=float)
        assert M.shape == (3, 3), "Matrix must be 3x3"
        # Translation
        tx, ty = M[0, 2], M[1, 2]
        # Upper-left 2x2 contains rotation * scale
        a, b = M[0, 0], M[0, 1]
        c, d = M[1, 0], M[1, 1]
        # Scale is length of the column vectors
        sx = np.sqrt(a * a + c * c)
        sy = np.sqrt(b * b + d * d)
        # Rotation is angle of first column
        rot = np.arctan2(c, a)
        return cls((tx, ty), rot, (sx, sy))

    @classmethod
    def to_matrix(cls, tf):
        tx, ty = tf._position
        c = np.cos(tf._orientation)
        s = np.sin(tf._orientation)
        sx, sy = tf._scaling
        return np.array(
            [[c * sx, -s * sy,  tx],
             [s * sx,  c * sy,  ty], 
             [   0.0,     0.0, 1.0]], dtype=float
        )
