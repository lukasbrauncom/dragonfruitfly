"""
Create kernels for different kinds of receptive fields.
"""

import numpy as np
from scipy import stats

def gaussian(size, ppu, sigma):
    """Create 2D gaussian kernel
    
    Keyword arguments:
    size -- Size as tuple(width, height)
    ppu -- Pixel per unit
    sigma -- Standard deviation of normal distribution
    """
    gauss = stats.multivariate_normal([0, 0], [[sigma, 0], [0, sigma]])
    
    ss = 1 / ppu # Step size
    width = size[0] / 2
    height = size[1] / 2
    
    x, y = np.mgrid[-height:height+ss:ss, -width:width+ss:ss]
    pos = np.zeros((x.shape) + (2,))
    pos[:, :, 0] = x
    pos[:, :, 1] = y
    
    return gauss.pdf(pos)
