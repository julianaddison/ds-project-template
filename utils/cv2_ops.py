"""
Author: Julian Addison

Organization: Firemark Labs

Utility functions for mask- and contour-related operations

"""

import cv2
import numpy as np
from typing import List, Dict, Tuple


def calc_contour_properties(cnt):
    area = cv2.contourArea(cnt)
    ellipse = cv2.fitEllipse(cnt)
    perimeter = cv2.arcLength(cnt, True)
    M = cv2.moments(cnt)
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])

    centroid_dist = ((cx - ellipse[0][0]) ** 2 + \
                     (cy - ellipse[0][1]) ** 2) ** 0.5

    try:
        ellipse_ratio = ellipse[1][1] / ellipse[1][0]
    except ZeroDivisionError:
        ellipse_ratio = 10

    properties = {'ellipse': ellipse,
                  'perimeter': perimeter,
                  'area': area,
                  'centroid': (cx, cy),
                  'ellipse_ratio': ellipse_ratio,
                  'centroid_dist': centroid_dist}

    return properties


def set_largest_contour_within_bbox_to_black(mask: np.array, bbox: np.array, height: int, width: int):
    # Get the original masked bbox
    orig_mask = mask.copy()[int(bbox[0] * height):int(bbox[2] * height), int(bbox[1] * width):int(bbox[3] * width)]
    cropped_mask = orig_mask.copy()

    # Find Contours and their area
    contours, hierarchy = cv2.findContours(cropped_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return cropped_mask, None
    areas = [cv2.contourArea(c) for c in contours]
    cnt = contours[np.argmax(areas)]
    area = areas[np.argmax(areas)]

    # Fill in the largest contour with black
    cropped_mask = cv2.fillPoly(cropped_mask, [cnt], 0)

    # Calculate the area ratio of the largest contour v.s. the bounding box (for checking later)
    # There are some other shape-related checks we can perform to try and weed out non-FFBs
    area_ratio = area / ((bbox[2] - bbox[0]) * height * ((bbox[3] - bbox[1]) * width))
    try:
        properties = calc_contour_properties(cnt)

        properties['area_ratio'] = area_ratio
        properties['bbox_height'] = (bbox[2] - bbox[0]) * height
        properties['bbox_width'] = (bbox[3] - bbox[1]) * width
    except cv2.error as err:
        properties = None
        pass

    return cropped_mask, properties


def check_point(cnt, bound):
    """
    Check if cnt lies in boundary through OpenCV's pointpolygon test
    :param cnt:
    :param bound:
    :return:
    """
    # checks if the point exists within the contours including the boundary or outside
    check_sum = 0
    for i in range(0, len(bound)):
        # if window boundary points are within contour boundary or contour add one
        if cv2.pointPolygonTest(cnt, (bound[i][0], bound[i][1]), False) >= 0:
            check_sum += 1
    return check_sum


def convert_grayscale(im):
    """
    convert to grayscale
    """
    return cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)


def binarize_image(im):
    """
    binarize image
    """
    _, im = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return im


def fill_contours(im, cnts):
    """
    fill contours
    """
    im_ = im.copy()
    cv2.drawContours(im_, cnts, -1, (0, 255, 0), thickness=cv2.FILLED)
    return im_


def blend_image(im, im_):
    """
    blend image
    """
    return cv2.addWeighted(im, 0.8, im_, 0.2, 0)


def get_contours(mask):
    """
    get mask contours
    """
    ret, thresh = cv2.threshold(mask, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def bounding_rect(cnt):
    """
    get bounding rect of contour :: bbox is x, y, w, h
    """
    return cv2.boundingRect(cnt)


def find_nonzero_points(im):
    """
    find nonzero points in an image. im is a threshold image
    """
    return cv2.findNonZero(im)


def min_rect_from_points(points):
    """
    generate min bounding rectangle from points
    """
    rect = cv2.minAreaRect(points)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    return box


def draw_polylines(img, pts, isClosed=True, color=(255, 0, 0), thickness=2):
    img_copy = img.copy()
    return cv2.polylines(img_copy, [pts], isClosed, color, thickness)


def get_area(poly_pts: list):
    return cv2.contourArea(np.array(poly_pts))


def calculate_areas(poly):
    area = 0
    for p in poly:
        area += get_area(p)
    return p


def calculate_laplacian_blur(image: np.array, ddepth=None, kernel_size: int=3):
    if ddepth is None:
        ddepth = cv2.CV_64F
    input = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(input, ddepth, ksize=kernel_size).var()