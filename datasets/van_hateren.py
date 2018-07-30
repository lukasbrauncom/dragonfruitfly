"""
Helper vor the Van Hateren Narural Image Dataset.

More information about the different formats and download can be found here:
http://bethgelab.org/datasets/vanhateren/
"""
import os
import array

import numpy as np


def get_image(path, image_id):
    """Return the image as uint16 numpy array.
    
    Keyword arguments:
    path -- Path to .iml files
    image_id -- ID of image to be load
    """
    path = os.path.join(path, "imk" + str(image_id).zfill(5) + ".iml")
    
    with open(path, 'rb') as fd:
        img = fd.read()
        arr = array.array('H', img)
        arr.byteswap()
    
    return np.array(arr, dtype='uint16').reshape(1024, 1536)


def get_ids(path):
    """Get all image ids as list.
    
    Keyword arguments:
    path -- Path to .iml files
    """
    ids = []
    for entry in os.scandir(path):
        if ".iml" in entry.name:
            ids.append("".join(filter(str.isdigit, entry.name)))
    ids.sort()
    return ids
    
    
def image_shape():
    """Return the shape of the image data as tuple(height, width)."""
    return (1024, 1536)
