import cython
import numpy as np
cimport numpy as np

def binary_diff_images(a, b, y_bounds, t):
    if y_bounds is None:
        y_bounds = (0, a.shape[0])
    return inner_binary_diff_images(a,b,y_bounds, t)

cpdef bint is_close(unsigned char a, unsigned char b, float rel_tol=1e-09, float abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

cpdef bint pixels_are_similar(unsigned char [:] a, unsigned char [:] b, float t):
    return is_close(a[0], b[0], rel_tol=t) and is_close(a[1], b[1], rel_tol=t) and is_close(a[2], b[2], rel_tol=t)

@cython.boundscheck(False)
cpdef long[:, :] inner_binary_diff_images(unsigned char [:, :, :] a, unsigned char [:, :, :] b, (int, int) y_bounds, float t):
    cdef int x, y, w, h

    h = a.shape[0]
    w = a.shape[1]
    if y_bounds is None:
        y_bounds = (0, h)
    cdef long [:, :] result = np.empty((y_bounds[1] - y_bounds[0], w), dtype=int)

    for y in range(y_bounds[0], y_bounds[1]):
        for x in range(0, w):
            # threshold the pixel
            result[y - y_bounds[0],x] = 0 if pixels_are_similar(a[y,x], b[y,x], t) else 255

    return result