"""Techniques for subsampling a mesh."""
import numpy as np
from scipy.linalg import qr, svd, lu, det, cholesky, lstsq
from copy import deepcopy
def get_qr_column_pivoting(Ao, number_of_subsamples):
    """
    Pivoted QR factorization, where the pivots are used as a heuristic for subsampling.
    """
    A = deepcopy(Ao)
    __, __, pvec = qr(A.T, pivoting=True)
    z = pvec[0:number_of_subsamples]
    return z
def get_svd_subset_selection(Ao, number_of_subsamples):
    """
    Singular value decomposition and pivoted QR factorization, where the pivots
    are used as a heuristic for subsampling.
    """
    A = deepcopy(Ao)
    __, __, V = svd(A.T)
    __, __, pvec = qr(V[:, 0:number_of_subsamples].T , pivoting=True )
    z = pvec[0:number_of_subsamples]
    return z
def get_newton_determinant_maximization(Ao, number_of_subsamples):
    """
    A convex relaxation technique for determinant maximization---akin to optimal experiment of
    design (D). Based on the work of Joshi and Boyd [1].

    **References**
        1. Joshi, S., Boyd, S., (2009) Sensor Selection via Convex Optimization. IEEE Transactions on Signal Processing, 57(2). `Paper <https://ieeexplore.ieee.org/document/4663892>`__

    """
    A = deepcopy(Ao)
    maxiter = 50
    n_tol = 1e-12
    gap = 1.005s

    # For backtracking line search parameters
    alpha = 0.01
    beta = 0.5

    # Assuming the input matrix is an np.matrix()
    m, n = A.shape
    if m < n:
        raise(ValueError, 'maxdet(): requires the number of columns to be greater than the number of rows!')
    z = np.ones((m, 1)) * float(number_of_subsamples)/float(m)
    g = np.zeros((m, 1))
    ones_m = np.ones((m, 1))
    ones_m_transpose = np.ones((1, m))
    kappa = np.log(gap) * n/m

    # Objective function
    Z = diag(z)
    fz = -np.log(np.linalg.det(A.T * Z * A)) - kappa * np.sum(np.log(z) + np.log(1.0 - z))

    # Optimization loop!
    for i in range(0, maxiter) :
        Z = diag(z)
        W = np.linalg.inv(A.T * Z * A)
        V = A * W * A.T
        vo = np.matrix(np.diag(V))
        vo = vo.T

        # define some z operations
        one_by_z = ones_m / z
        one_by_one_minus_z = ones_m / (ones_m - z)
        one_by_z2 = ones_m / z**2
        one_by_one_minus_z2 = ones_m / (ones_m - z)**2
        g = -vo- kappa * (one_by_z - one_by_one_minus_z)
        H = np.multiply(V, V) + kappa * diag( one_by_z2 + one_by_one_minus_z2)

        # Textbook Newton's method -- compute inverse of Hessian
        R = np.matrix(cholesky(H) )
        u = lstsq(R.T, g)
        Hinvg = lstsq(R, u[0])
        Hinvg = Hinvg[0]
        v = lstsq(R.T, ones_m)
        Hinv1 = lstsq(R, v[0])
        Hinv1 = Hinv1[0]
        dz = -Hinvg + (np.dot( ones_m_transpose , Hinvg ) / np.dot(ones_m_transpose , Hinv1)) * Hinv1


        deczi = indices(dz, lambda x: x < 0)
        inczi = indices(dz, lambda x: x > 0)
        a1 = 0.99* -z[deczi, 0] / dz[deczi, 0]
        a2 = (1 - z[inczi, 0] )/dz[inczi, 0]
        s = np.min(np.vstack([1.0, np.vstack(a1), np.vstack(a2) ] )  )
        flag = 1

        while flag == 1:
            zp = z + s*dz
            Zp = diag(zp)
            fzp = -np.log(np.linalg.det(A.T * Zp * A) ) - kappa * np.sum(np.log(zp) + np.log(1 - zp)  )
            const = fz + alpha * s * g.T * dz
            if fzp <= const[0,0]:
                flag = 2
            if flag != 2:
                s = beta * s
        z = zp
        fz = fzp
        sig = -g.T * dz * 0.5
        if( sig[0,0] <= n_tol):
            break
        zsort = np.sort(z, axis=0)
        thres = zsort[m - number_of_subsamples - 1]
        zhat, not_used = find(z, thres)

    zsort = np.sort(z, axis=0)
    thres = zsort[m - number_of_subsamples - 1]
    zhat, not_used = find(z, thres)
    p, q = zhat.shape
    Zhat = diag(zhat)
    L = np.log(np.linalg.det(A.T * Zhat  * A))
    ztilde  = z
    Utilde = np.log(np.linalg.det(A.T * diag(z) * A))  + 2 * m * kappa
    z = __binary2indices(zhat)
def __binary2indices(zhat):
    """
    Simple utility that converts a binary array into one with indices!
    """
    pvec = []
    m, n = zhat.shape
    for i in range(0, m):
        if(zhat[i,0] == 1):
            pvec.append(i)
    return pvec