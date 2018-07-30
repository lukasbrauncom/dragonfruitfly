"""
Create kernels for different kinds of receptive fields.
"""

import numpy as np
from scipy import stats

def gaussian(size, ppu, sigma):
    gauss = stats.multivariate_normal([0, 0], [[sigma, 0], [0, sigma]])
    
    ss = 1 / ppu # Step size
    width = size[0] / 2
    height = size[1] / 2
    
    x, y = np.mgrid[-width:width+ss:ss, -height:height+ss:ss]
    pos = np.zeros((x.shape)+ (2,)))
    pos[:, :, 0] = x
    pos[:, :, 1] = y
    
    return gauss.pdf(pos)
