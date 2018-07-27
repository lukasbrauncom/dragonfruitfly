"""
Provides a framework to generate stimuli in real time.

In order to reduce memory consumption and to enable very long and even stimuli 
of infinite length, stimuli are render on the go.
"""

class Stimulus:
    """Stimulus frame iterator."""
    def __init__(self, fps, size, ppu):
        """Keyword arguments:
        fps -- Frames per second
        size -- Stimulus size in units as tuple(height, width)
        ppu -- Pixels per unit
        """
        self.fps = fps
        self.size = size
        self.ppu = ppu
        
        self.height = size[0] * ppu
        self.width = size[1] * ppu
        self.shape = (0, self.height, self.width)
        
        self.duration = 0
        self.frames = 0
        
        self._definitions = []
        
        self._fncts = {
        }
        
        self._current_frame = 0
    
    
    def __iter__(self):
        return self
    
    
    def __next__(self):
        """Return next stimulus frame"""
        if self._current_frame >= self.frames:
            raise StopIteration
        self._current_frame += 1
        
        return []


    def append(self, definition):
        """Append a stimulus sequence to the stimulus.
        
        Call list_options() for a list of all stimulus types and their 
        parameters.
        
        Keyword arguments:
        definition -- Dictionary describing the sequence
        """
        self.duration += definition["duration"]
        self.frames += definition["duration"] * self.fps
        self.shape = (self.frames, self.height, self.width)
        
        self._definitions.append(definition)


    
