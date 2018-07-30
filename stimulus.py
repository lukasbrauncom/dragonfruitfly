"""
Provides a framework to generate stimuli in real time.

In order to reduce memory consumption and to enable very long and even stimuli 
of infinite length, stimuli are render on the go.
"""

import copy
from itertools import chain

import numpy as np

from .visualization import View
from .datasets import van_hateren


class Stimulus:
    """Stimulus frame iterator."""
    def __init__(self, fps, size, ppu):
        """Keyword arguments:
        fps -- Frames per second
        size -- Stimulus size in units as tuple(width, height)
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
            "sine": self._sine,
            "rectangle": self._rect,
            "hateren": self._hateren
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
    
    
    def _sine(self, duration, amplitude, wavelength, phase, offset, rotation,
        velocity):
        """Generate sine grating stimulus sequence.
        
        Keyword arguments:
        duration -- Duration in seconds
        amplitude -- Amplitude of sine grating
        wavelength -- Wavelength of sine grating
        phase -- Phase shift of sine grating
        offset -- Offset of sine grating
        rotation -- Rotation of sine grating by 0 or 90 degree
        velocity -- List of speed values in units per second, will be extended 
                    to the amount of frames and interpolated
        """
        frames = int(self.fps * duration)
        
        velocity = self._interpolate(velocity, frames)
        velocity = (2*np.pi*velocity) / self.fps
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
            frame = amplitude * np.sin(frequency * xy + velocity[time_step]
                + phase) + offset
    
    
    def _rect(self, duration, background, foreground, size, position,
                velocity_x, velocity_y):
        """Generate a stimulus sequence with a moving rectangle on a
        background.
        
        Keyword arguments:
        duration -- Duration in seconds
        background -- Background value
        foreground -- Foreground value
        size -- Rectangle size as tuple(width, height)
        position -- Distance to upper left corner tuple(left, top)
        velocity_x -- List of speed values in units per second, will be
                      extended to the amount of frames and interpolated
        velocity_y -- List of speed values in units per second, will be
                      extended to the amount of frames and interpolated
        """
        ppu = self.ppu
        w = self.width
        h = self.height
        
        velocity_x = self._interpolate(velocity_x, duration * self.fps) * ppu
        velocity_x /= self.fps
        velocity_y = self._interpolate(velocity_y, duration * self.fps) * ppu
        velocity_y /= self.fps
        
        s = [value * ppu for value in size]
        print(s)
        pos = [value * ppu for value in position]
        
        for time_step in range(int(self.fps * duration)):
            bg = np.zeros((h, w)) + background
            fg = np.zeros([s[1], s[0]]) + foreground
        
            pos[0] += velocity_x[time_step]
            x = np.round(pos[0]).astype(np.int32)
            pos[1] += velocity_y[time_step]
            y = np.round(pos[1]).astype(np.int32)
            
            bg_top_x = 0 if x < 0 else w if x > w else x
            bg_bottom_x = 0 if x+s[0] < 0 else w if x+s[0] > w else x+s[0]
            bg_top_y = 0 if y < 0 else h if y > h else y
            bg_bottom_y = 0 if y+s[1] < 0 else h if y+s[1] > h else y+s[1]
            
            fg_top_x = 0 if x > 0 else np.min([-x, s[0]])
            fg_bottom_x = s[0] if x < w - s[0] else np.max([w-x, 0])
            fg_top_y = 0 if y > 0 else np.min([-y, s[1]])
            fg_bottom_y = s[1] if y < h - s[1] else np.max([h-y, 0])
            
            bg[bg_top_y:bg_bottom_y, bg_top_x:bg_bottom_x] = fg[fg_top_y:
                fg_bottom_y, fg_top_x:fg_bottom_x]
                
            yield bg
    
    
    def _hateren(self, duration, path, image_id, position, move_x, move_y):
        """Generate a stimulus sequence with a moving window over a natural
        image of Van Hateren's dataset.
        
        Keyword arguments:
        duration -- Duration in seconds
        path -- Path to .iml files
        image_id -- ID of image to be load
        position -- Initial position of the window
        move_x -- Amount of pixels to shift window in x direction in each step        
        move_y -- Amount of pixels to shift window in y direction in each step
        """
        img = van_hateren.get_image(path, image_id)
        for time_step in range(int(self.fps * duration)):
            top_x = position[0] + move_x * time_step
            bottom_x = position[0] + move_x * time_step + self.size[0]
            top_y = position[1] + move_y * time_step
            bottom_y = position[1] + move_y * time_step + self.size[1]
            yield img[top_y:bottom_y, top_x:bottom_x]
    
    
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
    
    
    def show(self, vmin, vmax):
        """Show stimulus.
        
        Keyword arguments:
        vmin -- Minimum (black) value
        vmax -- Maximum (white) value
        """
        view = View(1, self.fps)
        view.add_stream(0, "matrix", self.__next__, [self.width, self.height],
            vmin = vmin, vmax = vmax)
        view.run()


    



    
