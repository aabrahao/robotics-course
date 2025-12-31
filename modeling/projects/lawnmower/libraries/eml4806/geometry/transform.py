from __future__ import annotations
from typing import Union, Any
import numpy as np
from eml4806.geometry.vector import Vector, as_vector, as_vectors
from eml4806.geometry.angle import wrap

Matrix = np.ndarray # 3x3

class Transform:

    """2D Affine Transformation (T * R * S)."""

    __slots__ = ('_translation', '_rotation', '_scaling')

    def __init__(self, translation: Vector = None, rotation: float = 0.0, scaling: Vector = None):
        self._translation = as_vector(translation if translation is not None else (0.0, 0.0))
        self._rotation = wrap(rotation)
        self._scaling = as_vector(scaling if scaling is not None else (1.0, 1.0))

    def translation(self) -> Vector:
        return self._translation.copy()

    def rotation(self) -> float:
        return self._rotation

    def scaling(self) -> Vector:
        return self._scaling.copy()

    def set(self, **kwargs) -> Transform:
        if 'translation' in kwargs:
            self._translation = as_vector(kwargs['translation'])
        if 'rotation' in kwargs:
            self._rotation = wrap(kwargs['rotation'])
        if 'scaling' in kwargs:
            self._scaling = as_vector(kwargs['scaling'])
        return self

    def translate(self, v: Vector, *, relative: bool = True) -> Transform:
        v = as_vector(v)
        self._translation = (self._translation + v) if relative else v
        return self

    def rotate(self, r: float, *, relative: bool = True) -> Transform:
        self._rotation = wrap((self._rotation + r) if relative else r)
        return self

    def scale(self, s: Union[float, Vector], *, relative: bool = True) -> Transform:
        s = as_vector(s)
        self._scaling = (self._scaling * s) if relative else s
        return self

    def matrix(self) -> Matrix:
        tx, ty = self._translation
        sx, sy = self._scaling
        c, s = np.cos(self._rotation), np.sin(self._rotation)
        return np.array([[sx*c, -sy*s, tx], [sx*s, sy*c, ty], [0, 0, 1]], dtype=np.float64)

    def apply(self, points: Any) -> Union[Vector, np.ndarray]:
        pts = as_vectors(points)
        H = self.matrix()
        return pts @ H[:2, :2].T + H[:2, 2]

    def compose(self, other: Transform) -> Transform:
        if not isinstance(other, Transform):
            raise TypeError(f"Cannot compose Transform with {type(other).__name__}")
        return Transform.from_matrix(self.matrix() @ other.matrix())

    def inverse(self) -> Transform:
        return Transform.from_matrix(np.linalg.inv(self.matrix()))

    def copy(self) -> Transform:
        return Transform(self._translation.copy(), self._rotation, self._scaling.copy())

    @classmethod
    def from_matrix(cls, M: Matrix) -> Transform:
        t = M[:2, 2]
        sx = np.linalg.norm(M[:2, 0])
        sy = np.linalg.norm(M[:2, 1])
        r = np.arctan2(M[1, 0] / sx if sx != 0 else 0, M[0, 0] / sx if sx != 0 else 1)
        return cls(t, r, (sx, sy))

    @classmethod
    def identity(cls) -> Transform:
        return cls()

    def __matmul__(self, other: Any) -> Union[Transform, Vector, np.ndarray]:
        if isinstance(other, Transform):
            return self.compose(other)
        return self.apply(other)

    def __repr__(self) -> str:
        return f"Transform(t={self._translation}, r={self._rotation:.3f}, s={self._scaling})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Transform):
            return False
        return (np.allclose(self._translation, other._translation) and
                np.isclose(self._rotation, other._rotation) and
                np.allclose(self._scaling, other._scaling))