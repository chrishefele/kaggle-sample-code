
"""
RDP: Implementation Ramer-Douglas-Peucker algorithm.
http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
Some code below derived from the pip "rdp" package. 
https://pypi.python.org/pypi/rdp/
"""

import numpy as np

EPS = 1.E-5  # min cosine limit, used to prevent 
             # divide-by-zero (equivilent to 0.01 degrees)

def turnangles(M):
    """
    M is an N x 2 array of (x,y) coordinates. 
    Returns the angles (in degrees) between the lines from
    each individual midpoint (x0,y0)  to the endpoints (x1,y1), (x2,y2).
    """
    Mt = M.transpose()
    x0, y0 = Mt[0],     Mt[1]     # arrays of all x's & y's
    x1, y1 = Mt[0][ 0], Mt[1][ 0] # start point
    x2, y2 = Mt[0][-1], Mt[1][-1] # end point

    vec1_x, vec1_y = x1 - x0, y1 - y0 
    vec2_x, vec2_y = x2 - x0, y2 - y0 
    vec1dot2 = vec1_x * vec2_x + vec1_y * vec2_y
    vec1_len = np.sqrt(vec1_x * vec1_x + vec1_y * vec1_y)
    vec2_len = np.sqrt(vec2_x * vec2_x + vec2_y * vec2_y)

    cos = vec1dot2 / np.maximum(vec1_len * vec2_len, EPS)
    cos = np.minimum(np.maximum(cos, -1.), 1.) 
    turn_angles = np.pi - np.arccos(cos) 
    # TODO convert [-360,360] -> [-180,180]
    # turn_angles = np.mod(turn_angles + 3*np.pi, 2.*np.pi) - np.pi 
    # -2pi->0, -pi->-pi 0->0, pi->-pi 2pi->0 
    turn_angles[0], turn_angles[-1] = 0., 0. # endpoints
    return np.rad2deg(turn_angles)

def pldists(M):
    """
    Calculate the perpendicular distance from (x0, y0) to a 
    line defined by the points (x1,y1) & (x2,y2). Uses formula from:
    http://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    """
    Mt = M.transpose()
    x0, y0 = Mt[0],     Mt[1]     # array of all x's and y's 
    x1, y1 = Mt[0][ 0], Mt[1][ 0] # start point
    x2, y2 = Mt[0][-1], Mt[1][-1] # end point
    dx, dy = x2 - x1, y2 - y1
    dists = np.abs( dy*x0 - dx*y0 + x2*y1 - y2*x1 ) / np.sqrt(dy*dy + dx*dx)
    return dists

def rdp(M, epsilon, dists_func=pldists):
    """
    Simplifies a given array of points using the RDP algorithm. 
    M         : a Nx2 numpy array of (x,y) points
    epsilon   : max distance allowed for intermediate points 
    dists_func: dists_func(M) yields an array of float distances 
                e.g. pldists, turnangles
    """
    dists = dists_func(M)

    dmax  = dists.max()
    index = dists.argmax() 
    if not (1 <= index < M.shape[0]):
        dmax = 0.0
        index = -1 

    if dmax > epsilon:
        r1 = rdp( M[     :index + 1], epsilon, dists_func=dists_func )
        r2 = rdp( M[index:         ], epsilon, dists_func=dists_func )
        return np.vstack((r1[:-1], r2))
    else:
        return np.vstack((M[0], M[-1]))

