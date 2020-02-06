
# This script loops through ultrasound images that have non-blank masks,
# and plots each one with the edges of their respective masks overlaid in red
# 
# Chris Hefele, May 2016

# IMAGES_TO_SHOW     = 5  # configure to taste :)
IMAGES_TO_SHOW     = 555555  # configure to taste :)

OUTLINE_DIR = "../data/train.outline/" # or None to not write files

import numpy as np
import matplotlib.pyplot as plt
import glob, os, os.path
import cv2


def image_with_mask(img, mask):
    # returns a copy of the image with edges of the mask added in red
    img_color = grays_to_RGB(img)
    mask_edges = cv2.Canny(mask, 100, 200) > 0  
    img_color[mask_edges, 0] = 255  # setting channel 0 = red 
    img_color[mask_edges, 1] = 0
    img_color[mask_edges, 2] = 0
    return img_color

def fimg_to_fmask(img_path):
    # convert an image file path into a corresponding mask file path 
    dirname, basename = os.path.split(img_path)
    maskname = basename.replace(".tif", "_mask.tif")
    return os.path.join(dirname, maskname)

def mask_not_blank(mask):
    return sum(mask.flatten()) > 0

def grays_to_RGB(img):
    # turn 2D grayscale image into grayscale RGB
    return np.dstack((img, img, img)) 

def plot_image(img, title=None):
    plt.figure(figsize=(15,20))
    plt.title(title)
    plt.imshow(img)
    plt.show()

def main():

    f_ultrasounds = [img for img in glob.glob("../download/train/*.tif") if 'mask' not in img]
    # f_ultrasounds.sort()
    f_masks       = [fimg_to_fmask(fimg) for fimg in f_ultrasounds]
    
    images_shown = 0 

    for f_ultrasound, f_mask in zip(f_ultrasounds, f_masks):

        img  = plt.imread(f_ultrasound)
        mask = plt.imread(f_mask)

        if mask_not_blank(mask):

            # plot_image(grays_to_RGB(img),  title=f_ultrasound)
            # plot_image(grays_to_RGB(mask), title=f_mask)

            f_combined = f_ultrasound + " & " + f_mask 
            outline_image = image_with_mask(img, mask)

            # plot_image(outline_image, title=f_combined)
            images_shown += 1

            if OUTLINE_DIR:
                f_out = os.path.join(OUTLINE_DIR, os.path.basename(f_ultrasound))
                plt.imsave(f_out, outline_image)
                print 'wrote:', f_out

        if images_shown >= IMAGES_TO_SHOW:
            break

main()

