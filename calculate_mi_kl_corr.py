#!/usr/bin/env python3

# Diana Giraldo, Sept 2024
# Last update: Set. 2024

import os, sys
import argparse
import numpy as np
import pandas as pd

import nibabel as nib

N_BINS = 16

def entropy_measures(x,y, bins = N_BINS, range=None):
    jointhist, _, _ = np.histogram2d(x, y, bins = bins, range = range)
    pxy = jointhist/np.sum(jointhist)
    px = np.sum(pxy, axis=1)
    py = np.sum(pxy, axis=0)
    px_py = px[:, None] * py[None, :]

    # Mutual info
    nzs = pxy > 0
    mi = np.sum(pxy[nzs] * np.log(pxy[nzs] / px_py[nzs]))

    # KL
    nzs = (px > 0) * (py > 0)
    klxy = np.sum(px[nzs] * np.log(px[nzs] / py[nzs]))
    klyx = np.sum(py[nzs] * np.log(py[nzs] / px[nzs]))
    
    return(mi, (klxy, klyx))

def norm_cross_corr(x,y):
    sx = x - np.mean(x)
    sy = y - np.mean(y)
    corr = np.sqrt(np.dot(sx,sy)**2/(np.dot(sx,sx)*np.dot(sy,sy)))
    return corr

def calculate_similarity(
    ref_fpath,
    img_fpath_list,
    mask_fpath = None,
    mi_bins = N_BINS,
    mi_robust_max = False,
):
    # Load ref and mask
    ref_array = nib.load(ref_fpath).get_fdata()
    if mask_fpath:
        mask_array = nib.load(mask_fpath).get_fdata().astype(bool)
        ref = ref_array[mask_array]
    else:
        ref = ref_array.ravel()
    
    if mi_robust_max: ref_max = np.percentile(ref, 99.75)*1.2

    # Loop over img list
    MI = []
    NCC = []
    KL = []

    for img_fpath in img_fpath_list:
        
        img_array = nib.load(img_fpath).get_fdata()
        
        if mask_fpath:
            img = img_array[mask_array]
        else:
            img = img_array.ravel()
            
        if mi_robust_max: 
            img_max = np.percentile(img, 99.75)*1.2
            range = [[0, ref_max], [0, img_max]]
        else:
            range = None

        mi,kl = entropy_measures(ref, img, bins = mi_bins, range = range)
        MI.append(mi)
        KL.append(kl)
        
        ncc = norm_cross_corr(ref, img)
        NCC.append(ncc)

    return MI, KL, NCC

# -------------------------------------------------------

def main(args=None):
    # Get inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--reference', type=str, required=True)
    parser.add_argument('-i', '--images', nargs='+', required=True)
    parser.add_argument('-o', '--output-file', type=str, required=True)
    parser.add_argument('-m', '--reference-mask', type=str, default=None)
    parser.add_argument('--n-bins', type=int, default=N_BINS)
    parser.add_argument('--robust-max', action='store_true', default=False)

    args = parser.parse_args(args if args is not None else sys.argv[1:])

    # Check inputs
    if not os.path.isfile(args.reference):
        raise ValueError('Input reference does not exist.')

    if args.reference_mask and not os.path.isfile(args.reference_mask):
        raise ValueError('Reference mask image does not exist.')

    for i,img_fpath in enumerate(args.images):
        if not os.path.isfile(img_fpath):
           raise ValueError(f'Input image {img_fpath} does not exist.') 

    # Initialize dataframe with results
    n_imgs = len(args.images)
    result = pd.DataFrame(
        {
            'reference': [args.reference]*n_imgs,
            'image': args.images
        }
    )

    # Calculate similarity measures
    MI, KL, NCC = calculate_similarity(
        args.reference,
        args.images,
        mask_fpath = args.reference_mask,
        mi_bins = args.n_bins,
        mi_robust_max = args.robust_max,
    )

    # Populate DF
    result['MI'] = MI
    result['KL1'] = [kl[0] for kl in KL]
    result['KL2'] = [kl[1] for kl in KL]
    result['NCC'] = NCC

    # Save
    result.to_csv(args.output_file, index=False)
    print("Results saved in ", args.output_file)

# -------------------------------------------------------

if __name__ == '__main__':
    main()
