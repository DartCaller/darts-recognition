import matplotlib.image as mpimg
import numpy as np


def read_image(image_path):
    np.flip(mpimg.imread(image_path).copy(), (0, 1))
