"""
Provide a framework to render plots and time series in real time.
"""

import matplotlib.pyplot as plt
import matplotlib.animation


class View:
    """Animate data streams."""
    def __init__(self, nplots, fps = 1):
        """Keyword arguments:
        nplots -- Amount of plots
        fps -- Frames per second for animation
        next -- Function that is called after each time step
        """
        self._nplots = nplots
        self._fps = fps
        
        self._fig, self._axs = plt.subplots(nplots)
        
        self._artists = []
        self._init_fncts = []
        self._getters = [None] * nplots
    
    
    def add_stream(self, pos, data_type, getter):
        """Add a data stream to be animated.
        
        Keyword arguments:
        pos -- Plot position
        data_type -- Data type of the data stream
        getter -- Function that yields the data
        """
        ax = self._axs if self._nplots == 1 else self._axs[pos]
        
        if data_type == "matrix":
            self._artists.append(ax.matshow([[0]], vmin = 0, vmax = 20))
            ax.axis("off")
        
        self._getters[pos] = getter
    
    
    def _update(self, frame):
        """Gets the data and updates plots, then it calls the next function
        if set.
        """
        for i, artist in enumerate(self._artists):
            artist.set_data(self._getters[i]())
            
        return tuple(self._artists)
    
    
    def run(self):
        """Run and show the animation."""
        self.ani = matplotlib.animation.FuncAnimation(self._fig, self._update,
            blit = True, repeat = False, interval = 1000 / self._fps)
        plt.show()






