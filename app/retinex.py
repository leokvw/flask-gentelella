import json

import skimage.color as sc
import skimage.exposure as se
import numpy as np
from scipy.ndimage import gaussian_filter

with open('config.json', 'r') as f:
    config = json.load(f)


# 图像直方图均衡
def coloredHistoEqual(img):
    img_cvt = sc.rgb2ycbcr(img)
    # img_cvt = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    img_cvt[:, :, 0] = se.equalize_hist(img_cvt[:, :, 0])
    # img_cvt[:, :, 0] = img_cvt.equalizeHist(img_cvt[:, :, 0])
    # img_histogram = cv2.cvtColor(img_cvt, cv2.COLOR_YCrCb2BGR)
    img_histogram = sc.ycbcr2rgb(img_cvt)
    return img_histogram


# 伽马变换
def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")

    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def single_scale_retinex(img, sigma):
    retinex = np.log10(img) - np.log10(gaussian_filter(img, sigma))

    return retinex


def multi_scale_retinex(img, sigma_list):
    retinex = np.zeros_like(img)
    for sigma in sigma_list:
        retinex += single_scale_retinex(img, sigma)

    retinex = retinex / len(sigma_list)

    return retinex


def color_restoration(img, alpha, beta):
    img_sum = np.sum(img, axis=2, keepdims=True)

    restoration = beta * (np.log10(alpha * img) - np.log10(img_sum))

    return restoration


def simplest_color_balance(img, low_clip, high_clip):
    global high_val, low_val
    total = img.shape[0] * img.shape[1]
    for i in range(img.shape[2]):
        unique, counts = np.unique(img[:, :, i], return_counts=True)
        current = 0
        for u, c in zip(unique, counts):
            if float(current) / total < low_clip:
                low_val = u
            if float(current) / total < high_clip:
                high_val = u
            current += c

        img[:, :, i] = np.maximum(np.minimum(img[:, :, i], high_val), low_val)

    return img


def multi_scale_retinex_with_color_restoration(img, sigma_list, g, b, alpha, beta, low_clip, high_clip):
    img = np.float64(img) + 1.0

    img_retinex = multi_scale_retinex(img, sigma_list)
    img_color = color_restoration(img, alpha, beta)
    img_msrcr = g * (img_retinex * img_color + b)

    for i in range(img_msrcr.shape[2]):
        img_msrcr[:, :, i] = (img_msrcr[:, :, i] - np.min(img_msrcr[:, :, i])) / \
                             (np.max(img_msrcr[:, :, i]) - np.min(img_msrcr[:, :, i])) * \
                             255

    img_msrcr = np.uint8(np.minimum(np.maximum(img_msrcr, 0), 255))
    img_msrcr = simplest_color_balance(img_msrcr, low_clip, high_clip)

    return img_msrcr


def automated_multi_scale_retinex_with_color_restoration(img, sigma_list):
    img = np.float64(img) + 1.0

    img_retinex = multi_scale_retinex(img, sigma_list)

    for i in range(img_retinex.shape[2]):
        unique, count = np.unique(np.int32(img_retinex[:, :, i] * 100), return_counts=True)
        for u, c in zip(unique, count):
            if u == 0:
                zero_count = c
                break

        low_val = unique[0] / 100.0
        high_val = unique[-1] / 100.0
        for u, c in zip(unique, count):
            if u < 0 and c < zero_count * 0.1:
                low_val = u / 100.0
            if u > 0 and c < zero_count * 0.1:
                high_val = u / 100.0
                break

        img_retinex[:, :, i] = np.maximum(np.minimum(img_retinex[:, :, i], high_val), low_val)

        img_retinex[:, :, i] = (img_retinex[:, :, i] - np.min(img_retinex[:, :, i])) / \
                               (np.max(img_retinex[:, :, i]) - np.min(img_retinex[:, :, i])) \
                               * 255

    img_retinex = np.uint8(img_retinex)

    return img_retinex


def multi_scale_retinex_with_chromaticity_preservation(img, sigma_list, low_clip, high_clip):
    img = np.float64(img) + 1.0

    intensity = np.sum(img, axis=2) / img.shape[2]

    retinex = multi_scale_retinex(intensity, sigma_list)

    intensity = np.expand_dims(intensity, 2)
    retinex = np.expand_dims(retinex, 2)

    intensity1 = simplest_color_balance(retinex, low_clip, high_clip)

    intensity1 = (intensity1 - np.min(intensity1)) / \
                 (np.max(intensity1) - np.min(intensity1)) * \
                 255.0 + 1.0

    img_msrcp = np.zeros_like(img)

    for y in range(img_msrcp.shape[0]):
        for x in range(img_msrcp.shape[1]):
            B = np.max(img[y, x])
            A = np.minimum(256.0 / B, intensity1[y, x, 0] / intensity[y, x, 0])
            img_msrcp[y, x, 0] = A * img[y, x, 0]
            img_msrcp[y, x, 1] = A * img[y, x, 1]
            img_msrcp[y, x, 2] = A * img[y, x, 2]

    img_msrcp = np.uint8(img_msrcp - 1.0)

    return img_msrcp
