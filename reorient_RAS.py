#!/usr/bin/env python3
# Diana Giraldo
# July 2023

import argparse
import os, sys

import numpy as np
import nibabel as nib

def main(args=None):
    
    # Get inputs
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--ro-matrix', type=str)
    
    args = parser.parse_args(args if args is not None else sys.argv[1:])
    
    # Check arguments
    if not os.path.isfile(args.input):
        raise ValueError('Input image file does not exist.')
    
    # Get input image orientation
    IM = nib.load(args.input)
    im_ori = nib.orientations.io_orientation(IM.affine)
    print('Image orientation:', nib.aff2axcodes(IM.affine))

    # Reoriented image
    RO = nib.as_closest_canonical(IM)
    ref_ori = nib.orientations.io_orientation(RO.affine)
    print('Reference orientation:', nib.aff2axcodes(RO.affine))

    # Save reoriented image
    nib.save(RO, args.output)

    if args.ro_matrix is not None:
        # Orientation transform from reference to input
        or_ref2in = nib.orientations.ornt_transform(ref_ori, im_ori)
        # Affine transform from input to reference
        aff_in2ref = nib.orientations.inv_ornt_aff(or_ref2in, np.array(RO.shape).astype(np.int32))
        # Save reorientation affine transform 
        np.savetxt(args.ro_matrix, aff_in2ref)
        
#---------------------------------------------
if __name__ == '__main__':
    main()