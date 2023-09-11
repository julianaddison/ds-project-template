"""
Author: Julian Addison

Organization: Firemark Labs

Image operations to be used across different modules

"""

import numpy as np
from PIL import ExifTags, Image
import pillow_heif


def convert_heic_to_jpeg(filepath):
    pillow_heif.register_heif_opener()
    img = Image.open(filepath)
    img.save(filepath)
    return

def central_crop(img: np.array, ratio: float):
    height, width, channels = img.shape
    h_margin = int(((1-ratio)/2)*height)
    w_margin = int(((1-ratio)/2)*width)
    return img[h_margin:-h_margin, w_margin:-w_margin]


def check_rotation_and_save(image_file):
    try:
        image = Image.open(image_file)

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
            image.save(image_file)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
            image.save(image_file)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)
            image.save(image_file)

        image.close()
    except (AttributeError, KeyError, IndexError):
        pass
