import numpy as np
from eml4806.geometry.vector import vector, vectors
from eml4806.geometry.angle import wrap

scalar = np.isscalar

class Transform:

    __slots__ = ['_translation', '_rotation', '_scaling', '_H']

    def __init__(self, translation=vector(), 
                 rotation=vector(), # roll, picth, yaw!
                 scaling=1.0,
                 H=None):
        self._translation = vector(translation)
        self._rotation = vector(rotation)
        self._rotation = wrap(self._rotation)
        self._scaling = float(scaling)
        self._H = H # Cached homogeneous matrix

    # --- Factories ---

    @classmethod
    def from_matrix(cls, M: np.ndarray) -> "Transform":
        """Decompose 4x4 homogeneous matrix into Transform."""
        t, r, s = cls._decompose(M)
        return cls(t, r, s, H=M.copy())

    @classmethod
    def identity(cls) -> "Transform":
        """Create identity transform."""
        return cls()

    # --- Access Functions ---
   
    def translation(self) -> np.ndarray:
        """Get translation vector (copy)."""
        return self._translation.copy()

    def rotation(self) -> np.ndarray:
        """Get rotation angles in radians (copy)."""
        return self._rotation.copy()

    def scaling(self) -> float:
        """Get uniform scaling factor."""
        return self._scaling

    def matrix(self) -> np.ndarray:
        """Get 4x4 transformation matrix (copy)."""
        return self._matrix().copy()

    # --- Core Operations ---

    def copy(self) -> "Transform":
        """Deep copy of the transform."""
        return Transform(self._translation, self._rotation, self._scaling, H=self._matrix())

    def apply(self, points):
        """Apply transform to points: p' = (R * S * p) + t."""
        M = self._matrix()
        pts = vectors(points)
        return pts @ M[:3, :3].T + M[:3, 3]

    def compose(self, other: "Transform") -> "Transform":
        """Compose transforms: result = self @ other."""
        self._ensure(other, "other")
        H = self._matrix() @ other._matrix()
        return Transform.from_matrix(H)

    def inverse(self) -> "Transform":
        """Compute inverse transform."""
        H = np.linalg.inv(self._matrix())
        return Transform.from_matrix(H)

    # --- Operators ---

    def __matmul__(self, other):
        """
        Compose transforms or apply to points using @ operator.
        Usage:
            T1 @ T2        -> Compose two transforms
            T @ point      -> Apply transform to point(s)
            T @ points     -> Apply transform to points
        """
        if isinstance(other, Transform):
            return self.compose(other)
        else:
            # Assume it's point(s)
            return self.apply(other)

    # --- Mutators (chainable) ---

    def translate(self, translation, relative=True):
        """Translate transform."""
        v = vector(translation)
        if relative:
            self._translation = self._translation + v
        else:
            self._translation = v
        self._H = None
        return self

    def rotate(self, rotation, *, relative=True):
        """Rotate transform."""
        v = vector(rotation)
        if relative:
            self._rotation = self._rotation + v
        else:
            self._rotation = v
        self._rotation = wrap(self._rotation)
        self._H = None
        return self

    def scale(self, s, relative=True):
        """Scale transform uniformly."""
        s = float(s)
        if relative:
            self._scaling *= s
        else:
            self._scaling = s
        self._H = None
        return self

    # --- Private Implementation ---

    def _matrix(self):
        """Compute cached matrix (private internal use)."""
        if self._H is None:
            self._H = self._build(self._translation, self._rotation, self._scaling)
        return self._H

    @staticmethod
    def _build(t, r, s):
        """Build 4x4 homogeneous matrix from TRS (private)."""
        roll, pitch, yaw = r
        cr, sr = np.cos(roll) , np.sin(roll)
        cp, sp = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw)  , np.sin(yaw)
        # R = Rz​(yaw) @ Ry​(pitch) @ Rx​(roll)
        R = np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp,   cp*sr,            cp*cr]
        ], dtype=t.dtype)
        # Scaling
        M = np.eye(4, dtype=t.dtype)
        M[:3, :3] = R * s  # Uniform scaling
        # Translation
        M[:3, 3] = t
        return M

    @staticmethod
    def _decompose(M):
        """Extract TRS from 4x4 homogeneous matrix (private)."""
        t = vector(M[:3, 3])
        # Extract uniform scale from first column (assuming uniform scaling)
        s = float(np.linalg.norm(M[:3, 0]))
        # Extract rotation matrix by removing scale
        R = M[:3, :3] / (s + 1e-12)
        # Extract Euler angles from rotation matrix
        pitch = np.arcsin(np.clip(-R[2, 0], -1.0, 1.0))
        if abs(np.cos(pitch)) > 1e-6:
            roll = np.arctan2(R[2, 1], R[2, 2])
            yaw = np.arctan2(R[1, 0], R[0, 0])
        else:
            roll = 0.0
            yaw = np.arctan2(-R[0, 1], R[1, 1])
        return t, wrap(vector(roll, pitch, yaw)), s

    @staticmethod
    def _ensure(obj, name="argument"):
        """Ensure object is a Transform instance."""
        if not isinstance(obj, Transform):
            raise TypeError(f"{name} must be Transform, got {type(obj).__name__}")
        return obj

    def __repr__(self):
        return f"Transform(t={self._translation}, r={self._rotation}, s={self._scaling})"

    def __str__(self):
        return f"Transform(t={self._translation}, r={self._rotation}, s={self._scaling})"