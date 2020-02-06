import numpy as np
import scipy

def gaussian(height, center_x, center_y, width_x, width_y, rotation):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)

    rotation = np.deg2rad(rotation)
    center_x = center_x * np.cos(rotation) - center_y * np.sin(rotation)
    center_y = center_x * np.sin(rotation) + center_y * np.cos(rotation)

    def rotgauss(x,y):
        xp = x * np.cos(rotation) - y * np.sin(rotation)
        yp = x * np.sin(rotation) + y * np.cos(rotation)
        g = height*np.exp(
            -(((center_x-xp)/width_x)**2+
              ((center_y-yp)/width_y)**2)/2.)
        return g
    return rotgauss

def moments(data, normalize_height = False):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    X, Y = np.indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = np.sqrt(abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max() if not normalize_height else 1
    return height, x, y, width_x, width_y, 0.0


def moments_fake(data, normalize_height = False):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    x,y = np.unravel_index(np.argmax(data), data.shape)
    col = data[:, int(y)]
    width_x = np.sqrt(abs((np.arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = np.sqrt(abs((np.arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max() if not normalize_height else 1
    width = (width_x + width_y)/2
    return height, x, y, width, width, 0.0

# this is unstable, so we bypass it and just use the moments
"""
def fitgaussian(data):
    #Returns (height, x, y, width_x, width_y)
    #the gaussian parameters of a 2D distribution found by a fit
    params = moments(data)
    errorfunction = lambda p: np.ravel(np.square(gaussian(*p)(*np.indices(data.shape)) - data))
    p, success = scipy.optimize.leastsq(errorfunction, params)
    return p, success
"""
