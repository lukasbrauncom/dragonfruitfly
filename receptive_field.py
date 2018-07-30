"""
Create kernels for different kinds of receptive fields.
"""

import numpy as np
import matplotlib.pyplot as plt
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


def plot(kernel):
    """Plot kernel.
    
    Keyword arguments:
    kernel -- 2D numpy matrix
    """
    fig, ax = plt.subplots(2, 2)
    ax[0, 0].imshow(kernel, vmin = 0)
    ax[0, 0].set_xticks([])
    ax[0, 0].set_yticks([])
    
    sl = kernel[kernel.shape[0] // 2, :]
    ax[1, 0].plot(sl)
    ax[1, 0].set_xlim([0, len(sl)-1])
    
    x = np.linspace(0, kernel.shape[0]-1, kernel.shape[0])
    sl = kernel[:, kernel.shape[1] // 2]
    ax[0, 1].plot(sl, x)
    ax[0, 1].invert_xaxis()
    ax[0, 1].invert_xaxis()
    ax[0, 1].set_ylim([0, len(sl)-1])
    
    fig.delaxes(ax.flatten()[3])




