import cv2
import os.path


def read_image(image_path):
    if os.path.isfile(image_path):
        return cv2.imread(image_path)
    else:
        raise FileNotFoundError(f'{image_path} not found')
