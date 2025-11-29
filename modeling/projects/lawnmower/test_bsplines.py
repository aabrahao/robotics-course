import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import minimize, NonlinearConstraint

# ============================================================
# B-spline utilities
# ============================================================

def make_open_uniform_knots(n_ctrl, k):
    """
    Open uniform knot vector in [0, 1] with end multiplicity k+1.
    n_ctrl: number of control points
    k: spline degree
    """
    if n_ctrl < k + 1:
        raise ValueError("Need n_ctrl >= k+1")

    # number of interior knots
    n_inner = n_ctrl - k - 1
    if n_inner < 0:
        raise ValueError("Not enough control points for given degree")

    # k+1 zeros, k+1 ones, interior uniformly in (0,1)
    if n_inner > 0:
        inner = np.linspace(0.0, 1.0, n_inner + 2)[1:-1]
    else:
        inner = np.array([])

    t = np.concatenate((
        np.zeros(k + 1),
        inner,
        np.ones(k + 1)
    ))
    return t


def make_splines(z, knots, k, n_ctrl):
    """
    Recover BSpline objects for x(t), y(t) from optimization vector z.
    z = [Px0..Px_{n_ctrl-1}, Py0..Py_{n_ctrl-1}]
    """
    Px = z[:n_ctrl]
    Py = z[n_ctrl:]
    sx = BSpline(knots, Px, k, extrapolate=False)
    sy = BSpline(knots, Py, k, extrapolate=False)
    return sx, sy


# ============================================================
# Curvature and cost
# ============================================================

def curvature_along_spline(sx, sy, t_samples, eps=1e-8):
    """
    Compute curvature kappa(t) along the spline at t_samples.
    kappa = (x' y'' - y' x'') / (x'^2 + y'^2)^(3/2)
    """
    dsx = sx.derivative()
    dsy = sy.derivative()
    d2sx = dsx.derivative()
    d2sy = dsy.derivative()

    kappas = []
    for t in t_samples:
        x1 = dsx(t)
        y1 = dsy(t)
        x2 = d2sx(t)
        y2 = d2sy(t)

        v2 = x1**2 + y1**2
        if v2 < eps:
            kappas.append(0.0)
        else:
            kappa = (x1 * y2 - y1 * x2) / (v2 ** 1.5)
            kappas.append(kappa)
    return np.array(kappas)


def objective(z, knots, k, n_ctrl, t_samples,
              w_length=1.0, w_kappa=0.1):
    """
    Objective: integral ~ sum ( w_length * |q'| + w_kappa * kappa^2 ) dt
    q'(t) = (x'(t), y'(t))
    """
    sx, sy = make_splines(z, knots, k, n_ctrl)
    dsx = sx.derivative()
    dsy = sy.derivative()

    kappas = curvature_along_spline(sx, sy, t_samples)
    cost = 0.0
    for i, t in enumerate(t_samples):
        x1 = dsx(t)
        y1 = dsy(t)
        speed = np.hypot(x1, y1)

        # basic integrand
        integrand = w_length * speed + w_kappa * (kappas[i] ** 2)
        cost += integrand

    # approximate integral with uniform dt
    dt = t_samples[1] - t_samples[0]
    cost *= dt
    return cost


# ============================================================
# Constraints
# ============================================================

def waypoint_constraint_func(z, knots, k, n_ctrl, waypoints, t_waypoints):
    """
    Enforce spline(t_i) = waypoint_i.
    Returns stacked residuals [x(t_i)-x_i, y(t_i)-y_i, ...].
    """
    sx, sy = make_splines(z, knots, k, n_ctrl)
    residuals = []
    for (wx, wy), t in zip(waypoints, t_waypoints):
        residuals.append(sx(t) - wx)
        residuals.append(sy(t) - wy)
    return np.array(residuals)


def curvature_constraint_func(z, knots, k, n_ctrl, t_samples):
    """
    Returns curvature values kappa(t_j) at t_samples.
    We will constrain them as: -kappa_max <= kappa(t_j) <= kappa_max
    """
    sx, sy = make_splines(z, knots, k, n_ctrl)
    kappas = curvature_along_spline(sx, sy, t_samples)
    return kappas


# ============================================================
# Main optimization wrapper
# ============================================================

def optimize_bspline_path(waypoints, R_min,
                          k=3,         # spline degree (3=cubic, 5=quintic)
                          n_ctrl_extra=3,  # extra control points beyond waypoints
                          n_samples_obj=100,
                          n_samples_kappa=100):
    """
    waypoints: array-like shape (N,2)
    R_min: minimum turning radius
    k: degree of B-spline
    n_ctrl_extra: how many extra control points beyond N waypoints
    """

    waypoints = np.asarray(waypoints, dtype=float)
    N = waypoints.shape[0]
    if N < 2:
        raise ValueError("Need at least 2 waypoints")

    # Choose number of control points (>= k+1)
    n_ctrl = max(N + n_ctrl_extra, k + 1)

    # Build knot vector
    knots = make_open_uniform_knots(n_ctrl, k)

    # Parameter values for waypoints in [0,1]
    # (you can also use cumulative distance-based parametrization for better behavior)
    t_way = np.linspace(0.0, 1.0, N)

    # Initial guess for control points:
    # Map waypoints to equally spaced indices in control-point space,
    # interpolate in-between linearly
    ctrl_indices_for_wp = np.linspace(0, n_ctrl - 1, N)
    ctrl_positions = np.zeros((n_ctrl, 2))
    for dim in range(2):
        ctrl_positions[:, dim] = np.interp(
            np.arange(n_ctrl),
            ctrl_indices_for_wp,
            waypoints[:, dim]
        )
    z0 = np.hstack([ctrl_positions[:, 0], ctrl_positions[:, 1]])

    # Sampling points for objective and curvature constraint
    t_samples_obj = np.linspace(0.0, 1.0, n_samples_obj)
    t_samples_kappa = np.linspace(0.0, 1.0, n_samples_kappa)

    # Curvature bound from R_min
    kappa_max = 1.0 / R_min

    # Define constraint objects
    waypoint_constr = NonlinearConstraint(
        lambda z: waypoint_constraint_func(z, knots, k, n_ctrl, waypoints, t_way),
        lb=0.0,
        ub=0.0
    )

    curvature_constr = NonlinearConstraint(
        lambda z: curvature_constraint_func(z, knots, k, n_ctrl, t_samples_kappa),
        lb=-kappa_max,
        ub=+kappa_max
    )

    # Run SLSQP optimization
    result = minimize(
        fun=lambda z: objective(z, knots, k, n_ctrl, t_samples_obj),
        x0=z0,
        method='SLSQP',
        constraints=[waypoint_constr, curvature_constr],
        options=dict(maxiter=300, ftol=1e-6, disp=True)
    )

    if not result.success:
        print("Optimization did not fully converge:", result.message)

    # Build final splines
    sx_opt, sy_opt = make_splines(result.x, knots, k, n_ctrl)
    return sx_opt, sy_opt, result


# ============================================================
# Example usage
# ============================================================

if __name__ == "__main__":
    
    n = 5

    waypoints = np.random.uniform(0.0, 10.0, (n, 2))

    rmin = 2.0  # minimum turning radius
    
    sx, sy, res = optimize_bspline_path(
        waypoints,
        rmin,
        k=5,            
        n_ctrl_extra=8  
    )

    import matplotlib.pyplot as plt

    ts = np.linspace(0.0, 1.0, 200)
    xs = sx(ts)
    ys = sy(ts)

    plt.figure()
    plt.plot(xs, ys, label="optimized path")
    plt.scatter(waypoints[:, 0], waypoints[:, 1], c='r', label="waypoints")
    plt.axis('equal')
    plt.legend()
    plt.grid(True)
    plt.show()
