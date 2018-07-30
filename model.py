"""
Provide a framework to create GPU accelerated models and to run them on models.
"""
import numpy as np

import tensorflow as tf

class Model:
    def __init__(self, stimulus):
        """Create and run a TensorFlow dataflow graphs on a stimulus.
        
        Keyword arguments:
        stimulus -- Stimulus to run the model on
        """
        self.first_frame = np.expand_dims(next(stimulus), axis = 0)
        stimulus.reset()
        self.frames = stimulus.shape[0]
        
        self.stimulus = stimulus
        self.graph = tf.Graph()
        
        self._session = None
        self._global_step = 0
        
        with self.graph.as_default():
            self._x = tf.placeholder(tf.float32,
                        shape = self.first_frame.shape)
        
        self._fetch_nodes = []
        self._last_node = self._x
    
    
    def __iter__(self):
        self._fetch_nodes = self._last_node
        return self
    
    
    def __next__(self):
        if self._global_step == 0:
            with self.graph.as_default():
                self._session = tf.Session()
                self._session.run(tf.global_variables_initializer())
        
        try:
            frame = np.expand_dims(next(self.stimulus), axis = 0)
        except:
            self._session.close()
            self._global_step == 0
            self.stimulus.reset()
            raise StopIteration
        
        self._global_step += 1
        
        return frame, self._session.run(self._fetch_nodes, {self._x: frame})
    
    
    def __call__(self, nodes):
        self._fetch_nodes = nodes
        return self
    
    
    
