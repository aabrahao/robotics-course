import numpy as np

class Size:

    """2D size storing width (w) and height (h) as floats."""

    __slots__ = ("_w", "_h")

    def __init__(self, w: float = 0.0, h: float = 0.0):
        self._w = float(w)
        self._h = float(h)

    # w / h properties

    @property
    def w(self) -> float:
        return self._w

    @w.setter
    def w(self, w: float) -> None:
        self._w = float(w)

    @property
    def h(self) -> float:
        return self._h

    @h.setter
    def h(self, h: float) -> None:
        self._h = float(h)

    # vector property (NumPy interoperability)

    @property
    def vector(self) -> np.ndarray:
        """Return NumPy array [w, h]."""
        return np.array([self._w, self._h], dtype=float)

    @vector.setter
    def vector(self, v):
        """
        Set size from any 2-element vector-like value:
            s.vector = (w, h)
            s.vector = [w, h]
            s.vector = np.array([w, h])
            s.vector = another_size
        """
        if isinstance(v, Size):
            self._w, self._h = v._w, v._h
            return

        arr = np.asarray(v, dtype=float).flatten()
        if arr.size != 2:
            raise ValueError(f"Expected 2 elements, got {arr.size}")

        self._w, self._h = float(arr[0]), float(arr[1])

    # basic operations

    def set(self, w: float, h: float) -> None:
        self._w = float(w)
        self._h = float(h)

    def copy(self) -> "Size":
        return Size(self._w, self._h)

    # convenience helpers

    def area(self) -> float:
        return self._w * self._h

    def empty(self) -> bool:
        return self._w == 0.0 and self._h == 0.0

    # __iter__ (like Point)

    def __iter__(self):
        yield self._w
        yield self._h

    # representation

    def __repr__(self) -> str:
        return f"Size({self._w}, {self._h})"
