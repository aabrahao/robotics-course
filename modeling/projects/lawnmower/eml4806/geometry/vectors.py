import numpy as np

# =============================================================================
# CONSTRUCTOR
# =============================================================================

def vectors(*args) -> np.ndarray:
    n_args = len(args)
    if n_args == 1:
        v = args[0]
        # --- THE FASTEST PATH ---
        # 1. Check type directly (faster than isinstance)
        # 2. Check ndim, shape, and dtype
        if type(v) is np.ndarray:
            if v.ndim == 2 and v.shape[1] == 3 and v.dtype == np.float64:
                return v # Absolute zero-copy return
        
        # --- SECONDARY PATH: Handling non-compliant inputs ---
        # Instead of hasattr, use a try-except or check for None/Empty
        if v is None: 
            return np.empty((0, 3), dtype=np.float64)
        arr = np.asarray(v, dtype=np.float64)
        # Zero-length check after conversion
        if arr.size == 0:
            return np.empty((0, 3), dtype=np.float64)
        if arr.ndim == 2:
            if arr.shape[1] == 2:
                # Optimized padding: Allocate once, slice once
                res = np.zeros((arr.shape[0], 3), dtype=np.float64)
                res[:, :2] = arr
                return res
            return arr # If shape[1] is 3 but it failed dtype check above
        if arr.ndim == 1:
            size = arr.shape[0]
            if size == 3:
                return arr.reshape(1, 3) # Zero-copy view change
            if size == 2:
                return np.array([[arr[0], arr[1], 0.0]], dtype=np.float64)
            raise ValueError(f"Vector size {size} invalid. Expected 2 or 3.")
    elif n_args == 0:
        return np.empty((0, 3), dtype=np.float64)
    elif n_args == 2 or n_args == 3:
        # np.column_stack is excellent here for list-of-coordinates input
        x = np.asarray(args[0], dtype=np.float64)
        y = np.asarray(args[1], dtype=np.float64)
        z = np.asarray(args[2], dtype=np.float64) if n_args == 3 else np.zeros_like(x)
        return np.column_stack([x, y, z])
    raise TypeError(f"vectors() takes 0-3 arguments, got {n_args}")

as_vectors = vectors

# =============================================================================
# Unzip
# =============================================================================

def split(data: np.ndarray) -> tuple:
    return data[:, 0], data[:, 1], data[:, 2]

# =============================================================================
# SEQUENCE MUTATION
# =============================================================================

def append(data: np.ndarray, item) -> np.ndarray:
    """Add vector(s) to the end (returns new array)."""
    return np.vstack([data, vectors(item)])

def prepend(data: np.ndarray, item) -> np.ndarray:
    """Add vector(s) to the start (returns new array)."""
    return np.vstack([vectors(item), data])

def concat(*sequences) -> np.ndarray:
    """Join multiple sequences into one."""
    return np.vstack([vectors(seq) for seq in sequences])

# =============================================================================
# GEOMETRIC ANALYSIS
# =============================================================================

def deltas(data: np.ndarray) -> np.ndarray:
    """Vector differences between nodes (N-1, 3)."""
    return np.diff(data, axis=0)

def step_lengths(data: np.ndarray) -> np.ndarray:
    """Distance between consecutive points."""
    return np.linalg.norm(np.diff(data, axis=0), axis=1)

def cumulative_lengths(data: np.ndarray) -> np.ndarray:
    """Distance along sequence at each node."""
    return np.concatenate([[0.0], np.cumsum(step_lengths(data))])

def total_length(data: np.ndarray) -> float:
    return float(np.sum(step_lengths(data)))

def tangents(data: np.ndarray) -> np.ndarray:
    """Unit direction vectors (N, 3)."""
    d = deltas(data)
    norms = np.linalg.norm(d, axis=1, keepdims=True)
    tangs = np.divide(d, norms, out=np.zeros_like(d), where=norms > 1e-10)
    return np.vstack([tangs, tangs[-1:]])

# =============================================================================
# SPATIAL QUERIES
# =============================================================================

def closest_point_on_path(data: np.ndarray, target: np.ndarray) -> tuple:
    """Vectorized search for closest point on a piecewise-linear path."""
    target = np.asarray(target, dtype=np.float64)
    p1, p2 = data[:-1], data[1:]
    seg = p2 - p1
    seg_len_sq = np.sum(seg**2, axis=1)
    t = np.sum((target - p1) * seg, axis=1) / (seg_len_sq + 1e-20)
    t = np.clip(t, 0, 1)
    candidates = p1 + t[:, np.newaxis] * seg
    dists_sq = np.sum((candidates - target)**2, axis=1)
    idx = np.argmin(dists_sq)
    return candidates[idx], idx, t[idx]

def bounding_box(data: np.ndarray) -> tuple:
    """Returns (min_point, max_point)."""
    return data.min(axis=0), data.max(axis=0)

def bounding_sphere(data: np.ndarray) -> tuple:
    """Returns (center, radius)."""
    center = data.mean(axis=0)
    radius = float(np.max(np.linalg.norm(data - center, axis=1)))
    return center, radius

# =============================================================================
# SAMPLING & SMOOTHING
# =============================================================================

def resample(data: np.ndarray, count: int) -> np.ndarray:
    """Uniformly resamples nodes along the sequence."""
    if len(data) < 2: return data
    old_t = np.linspace(0, 1, len(data))
    new_t = np.linspace(0, 1, count)
    return np.column_stack([np.interp(new_t, old_t, data[:, i]) for i in range(3)])

def smooth(data: np.ndarray, window: int = 3) -> np.ndarray:
    """Vectorized moving average with edge padding."""
    if window < 2: return data.copy()
    kernel = np.ones(window) / window
    padded = np.pad(data, ((window//2, window//2), (0, 0)), mode='edge')
    return np.column_stack([np.convolve(padded[:, i], kernel, mode='valid') for i in range(3)])

is_null = lambda v: np.allclose(v, 0)