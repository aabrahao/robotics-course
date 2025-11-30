import numpy as np

from eml4806.geometry.vector import Vector, toVector, toVectors
from eml4806.geometry.angle import wrap

class Transform:
    """
    2D similarity transform: translation + rotation + non-uniform scaling.
    Internally stored as:
        _translation: Vector   (tx, ty)
        _rotation:    float    (radians)
        _scaling:     Vector   (sx, sy)
    """

    def __init__(self, translation=(0.0, 0.0), rotation=0.0, scaling=(1.0, 1.0)):
        self._translation: Vector = toVector(translation)
        self._rotation: float     = float(rotation)
        self._scaling: Vector     = toVector(scaling)

    # -------------------------------------------------------------------------
    # GETTERS  (method-only API)
    # -------------------------------------------------------------------------

    def translation(self) -> Vector:
        """Return the translation component as a Vector."""
        return Vector(self._translation)

    def rotation(self) -> float:
        """Return the rotation angle in radians."""
        return float(self._rotation)

    def scaling(self) -> Vector:
        """Return the scaling factors as a Vector."""
        return Vector(self._scaling)

    # -------------------------------------------------------------------------
    # Mutating operations (these act as setters when relative=False)
    # -------------------------------------------------------------------------

    def translate(self, d, relative: bool = False):
        d = toVector(d)
        if relative:
            self._translation = self._translation + d
        else:
            self._translation = d
        return self

    def rotate(self, angle, relative: bool = False):
        angle = float(angle)
        if relative:
            self._rotation += angle
        else:
            self._rotation = angle
        self._rotation = wrap(self._rotation)
        return self

    def scale(self, s, relative: bool = False):
        if np.isscalar(s):
            s = Vector(float(s), float(s))
        else:
            s = toVector(s)
        if relative:
            self._scaling = Vector(self._scaling.x * s.x, self._scaling.y * s.y)
        else:
            self._scaling = s
        return self

    # -------------------------------------------------------------------------
    # Read-only computed values
    # -------------------------------------------------------------------------

    def matrix(self) -> np.ndarray:
        """Return the 3×3 homogeneous matrix representing the transform."""
        return Transform.to_matrix(self)

    def inverse(self) -> "Transform":
        """Return a new Transform representing the inverse transform."""
        return Transform.from_matrix(np.linalg.inv(self.matrix()))

    def clone(self) -> "Transform":
        """Return a deep copy of this transform."""
        return Transform(
            Vector(self._translation),
            self._rotation,
            Vector(self._scaling),
        )

    # -------------------------------------------------------------------------
    # Applying the transform to points
    # -------------------------------------------------------------------------

    def apply(self, points, inverse: bool = False):
        """
        Apply the transform to a single point or a list of points.
        Acceptable input:
            - Vector / (x,y) / [x,y] / np.array([x,y])
            - list/tuple of such objects
        Output:
            - Vector        if input contained 1 point
            - list[Vector]  if input contained multiple points
        """
        vectors = toVectors(points)
        
        tx = self._translation.x
        ty = self._translation.y
        rot = self._rotation
        sx = self._scaling.x
        sy = self._scaling.y
        c = np.cos(rot)
        s = np.sin(rot)
        
        results = []
        if not inverse: # Forward
            for p in vectors:
                # Scale
                x = p.x * sx
                y = p.y * sy
                # Rotate
                xo = c * x - s * y
                yo = s * x + c * y
                # Translate
                xo += tx
                yo += ty
                results.append(Vector(xo, yo))
        else: # Inverse
            inv_sx = 1.0 / sx
            inv_sy = 1.0 / sy
            for p in vectors:
                # Untranslate
                x = p.x - tx
                y = p.y - ty
                # Unrotate
                xo = c * x + s * y
                yo = -s * x + c * y
                # Unscale
                xo *= inv_sx
                yo *= inv_sy
                results.append(Vector(xo, yo))
        
        if len(results) == 1:
            results[0]
        
        return results

    # -------------------------------------------------------------------------
    # Class methods
    # -------------------------------------------------------------------------

    @classmethod
    def compound(cls, T1: "Transform", T2: "Transform") -> "Transform":
        M = T1.matrix() @ T2.matrix() # T1 @ T2
        return cls.from_matrix(M)

    @classmethod
    def from_matrix(cls, M) -> "Transform":
        M = np.asarray(M, dtype=float)
        assert M.shape == (3, 3)
        # Translation
        tx, ty = M[0, 2], M[1, 2]
        # Decompose rotation * scaling (upper-left 2×2)
        a, b = M[0, 0], M[0, 1]
        c, d = M[1, 0], M[1, 1]
        # Scale
        sx = np.sqrt(a * a + c * c)
        sy = np.sqrt(b * b + d * d)
        # Rotation
        rot = np.arctan2(c, a)
        return cls(translation=(tx, ty), rotation=rot, scaling=(sx, sy))

    @classmethod
    def to_matrix(cls, tf: "Transform") -> np.ndarray:
        tx, ty = tf._translation
        c = np.cos(tf._rotation)
        s = np.sin(tf._rotation)
        sx, sy = tf._scaling
        return np.array([
            [c*sx, -s*sy,  tx],
            [s*sx,  c*sy,  ty],
            [ 0.0,   0.0, 1.0]], dtype=float)

    # -------------------------------------------------------------------------
    # Printing
    # -------------------------------------------------------------------------

    def __repr__(self):
        return (
            f"Transform(translation={self._translation}, "
            f"rotation={self._rotation}, "
            f"scaling={self._scaling})"
        )

    def __str__(self):
        ang_deg = np.degrees(self._rotation)
        return (
            f"Transform: translation={self._translation}, "
            f"rotation={ang_deg:.2f}°, scaling={self._scaling}"
        )
