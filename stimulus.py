"""
Provides a framework to generate stimuli in real time.

In order to reduce memory consumption and to enable very long and even stimuli 
of infinite length, stimuli are render on the go.
"""

import copy
from itertools import chain

import numpy as np

from .visualization import View


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
        self._generator = None
        
        self._fncts = {
            "constant": self._constant,
            "sine": self._sine
        }
    
    
    def __iter__(self):
        return self
    
    
    def __next__(self):
        """Return next stimulus frame"""
        if self._generator == None:
            fncts = self._fncts
            definitions = copy.deepcopy(self._definitions)
            mapping = [(fncts[defi.pop("type")], defi) for defi in definitions]
            self._generator = chain(*[fnct(**defi) for fnct, defi in mapping])
        
        return next(self._generator)


    def _constant(self, duration, value):
        """Generate a constant stimulus sequence.
        
        Keyword arguments:
        duration -- Duration in seconds
        value -- intensity value of the stimulus
        """
        for time_step in range(int(self.fps * duration)):
            frame = np.zeros((self.height, self.width)) + value
            yield frame
    
    
    def _sine(self, duration, amplitude, wavelength, phase, offset, rotation, velocity):
        """Generate sine grating stimulus sequence.
        
        Keyword arguments:
        duration -- Duration in seconds
        amplitude -- Amplitude of sine grating
        wavelength -- Wavelength of sine grating
        phase -- Phase shift of sine grating
        offset -- Offset of sine grating
        rotation -- Rotation of sine grating by 0 or 90 degree
        velocity -- List of speed values, will be extended to the amount of frames and interpolated
        """
        frames = int(self.fps * duration)
        
        velocity = self._interpolate(velocity, frames)
        velocity = (2*np.pi) / (self.fps / velocity)
        velocity = velocity.cumsum()
        
        frequency = (2*np.pi) / float(wavelength)
        
        # Generate first frame
        step_size = 1 / self.ppu
        xx, yy = np.mgrid[0:self.size[0]:step_size, 0:self.size[1]:step_size]
        
        xy = yy if rotation == 0 else xx
        
        frame = amplitude * np.sin(frequency * xy + phase) + offset
        
        # Generate following frames
        for time_step in range(frames):
            yield frame
            frame = amplitude * np.sin(frequency * xy + velocity[time_step] + phase) + offset
            

    def append(self, definition):
        """Append a stimulus sequence to the stimulus.
        
        Call list_stimuli() for a list of all stimulus types and their 
        parameters.
        
        Keyword arguments:
        definition -- Dictionary describing the sequence
        """
        self.duration += definition["duration"]
        self.frames += definition["duration"] * self.fps
        self.shape = (self.frames, self.height, self.width)
        
        self._definitions.append(definition)
    
    
    def reset(self):
        """Reset generator to initial condition."""
        self._generator = None
        

    def list_stimuli(self):
        """Print all available stimulus types and their parameters."""
        print("Available stimuli:")
        for key, value in self._fncts.items():
            print('{\n\t"type": "' + key + '",')
            params = value.__code__.co_varnames[1:value.__code__.co_argcount]
            for param in params:
                print('\t"' + param + '": <value>,')
            print("}\n")
    
    
    def _interpolate(self, inp, frames):
        """Interpolate array of values
        
        Keyword arguments:
        inp -- Array of values
        frames -- Target size
        """
        if len(inp) == 1:
            return np.array(inp * frames, dtype=np.float64)
        else:
            new_range = np.linspace(0, len(inp)-1, frames)
            return np.interp(new_range, np.arange(len(inp)), inp)
            
    
    def get_frame(self):
        """Return next frame"""
        return sel
    
    
    def show(self):
        """Show stimulus."""
        view = View(1, self.fps)
        view.add_stream(0, "matrix", self.__next__)
        view.run()


    



    
