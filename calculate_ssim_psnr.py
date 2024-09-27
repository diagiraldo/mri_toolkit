#!/usr/bin/env python3

# Diana Giraldo, Jan 2024
# Last update: Jan. 2024

import os, sys
import argparse
import numpy as np
import pandas as pd

import nibabel as nib

from skimage.metrics import structural_similarity
from skimage.util.arraycrop import crop

def main(args=None):
    
    # Get inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=str, required=True)
    parser.add_argument('--image', type=str, required=True)
    parser.add_argument('--reference-mask', type=str, default=None)
    parser.add_argument('--output-file', type=str, required=True)
    parser.add_argument('--no-reorient', action='store_true', default=False)
    parser.add_argument('--ssim-sigma', type=float, default=1.5)
    parser.add_argument('--ssim-non-gaussian-weights', action='store_true', default=False)
    parser.add_argument('--ssim-use-sample-covariance', action='store_true', default=False) 
    
    args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    # Check inputs
    if not os.path.isfile(args.reference):
        raise ValueError('Input reference does not exist.')
        
    if not os.path.isfile(args.image):
        raise ValueError('Input image does not exist.')
        
    if not os.path.isdir(os.path.dirname(args.output_file)):
        raise ValueError('Output directory does not exist.')
        
    if args.reference_mask and not os.path.isfile(args.reference_mask):
        raise ValueError('Reference mask image does not exist.')
        
    # Read images
    REF = nib.load(args.reference)
    ref_range = np.max(REF.get_fdata())
    
    if args.reference_mask : 
        REFmask = nib.load(args.reference_mask)
        ref_range = np.max(REF.get_fdata()*REFmask.get_fdata())
    
    IM = nib.load(args.image)
    
    if not args.no_reorient:
        im2ref_ornt = nib.orientations.ornt_transform(
            start_ornt = nib.orientations.io_orientation(IM.affine),
            end_ornt = nib.orientations.io_orientation(REF.affine)
        )
        IM = IM.as_reoriented(im2ref_ornt)
        
    # Squared error map
    sq_err = (REF.get_fdata() - IM.get_fdata()) ** 2
    
    # Structural similarity map
    _, str_sim = structural_similarity(
        IM.get_fdata(), REF.get_fdata(), 
        data_range = ref_range,
        gaussian_weights = not args.ssim_non_gaussian_weights,
        sigma = args.ssim_sigma,
        use_sample_covariance = args.ssim_use_sample_covariance,
        full = True,
    )
    pad = (2 * int(3.5 * args.ssim_sigma + 0.5)) // 2
    
    # Calculate PSNR and SSIM for the whole image
    mse =  np.sum(sq_err, dtype=np.float64)/sq_err.size
    psnr_whole = 10 * np.log10((ref_range ** 2) / mse)
    ssim_whole = crop(str_sim, pad).sum(dtype=np.float64)/crop(str_sim, pad).size
    
    # Calculate PSNR and SSIM within mask
    if args.reference_mask :
        mse = np.sum(sq_err*REFmask.get_fdata(), dtype=np.float64)/np.sum(REFmask.get_fdata())
        psnr_mask = 10 * np.log10((ref_range ** 2) / mse)
        ssim_mask = crop(str_sim*REFmask.get_fdata(), pad).sum(dtype=np.float64)/np.sum(crop(REFmask.get_fdata(), pad))
        
    # Construct dataframe with results
    result = pd.DataFrame(
        {
            'reference': [args.reference],
            'image': [args.image],
            'PSNR': [psnr_whole],
            'SSIM': [ssim_whole],
        }
    )
    
    if args.reference_mask:
        result = result.assign(
            PSNR_mask = [psnr_mask],
            SSIM_mask = [ssim_mask]
        )
    
    result.to_csv(args.output_file, index=False)
    print("PSNR and SSIM saved in ", args.output_file)
        
    
if __name__ == '__main__':
    main()
