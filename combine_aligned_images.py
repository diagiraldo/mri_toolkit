#!/usr/bin/env python3
# Diana Giraldo

import argparse
import os, sys

import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter

DEFAULT_FBA_P = 11
DEFAULT_FBA_SIGMA = 5

def fba_nd_onechannel(img_list, p = DEFAULT_FBA_P, sigma = DEFAULT_FBA_SIGMA):
    
    F_img = [np.fft.rfftn(img) for img in img_list]
    W_img = [gaussian_filter(np.abs(fimg), sigma = sigma) ** p for fimg in F_img]
    sum_W = np.sum(W_img, axis = 0)
    U = np.sum([ fimg*(wimg/sum_W) for fimg, wimg in zip(F_img, W_img) ], axis = 0) 
    
    return np.fft.irfftn(U)

# Select method to combine volumes
def combine_images(
    img_list, 
    method = "average", 
    fba_p = DEFAULT_FBA_P, fba_sigma = DEFAULT_FBA_SIGMA,
):
    
    if method == "fba":
        return fba_nd_onechannel(img_list, p = fba_p, sigma = fba_sigma)

    elif method == "median":
        return np.median(img_list, axis = 0)
    
    else:
        return np.mean(img_list, axis = 0)
    
#---------------------------------------------

def main(args=None):
    
    # Get inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs', nargs='+', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--method', type=str, choices=["fba", "median", "average"], default="average")
    parser.add_argument('--fba-p', type=int, default = DEFAULT_FBA_P)
    parser.add_argument('--fba-sigma', type=float, default = DEFAULT_FBA_SIGMA)
    parser.add_argument('--verbose', action='store_true', default=False)
    
    args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    # Check arguments
    for in_file in args.inputs:
        if not os.path.isfile(in_file):
            raise ValueError(f'Input image file {in_file} does not exist.')

    if args.verbose: 
        print(f'Loading {len(args.inputs)} input images')
        print(*args.inputs, sep = '\n')
    
    # Get first image
    img0 = nib.load(args.inputs[0])
    img_list = [img0.get_fdata()]

    # Get list of arrays
    for i in range(1, len(args.inputs)):
        img_list.append(nib.load(args.inputs[i]).get_fdata())

    # Combine
    out = combine_images(img_list, method = args.method, fba_p = args.fba_p, fba_sigma = args.fba_sigma)

    # Save combined image
    out_nib = nib.Nifti1Image(out, img0.affine, img0.header)
    nib.save(out_nib, args.output)
    if args.verbose: print("Output image saved in", args.output)

#---------------------------------------------
if __name__ == '__main__':
    main()