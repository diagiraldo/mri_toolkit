# My MRI toolkit

This is a set of tools that I have created to fit my needs when processing MRIs. 

## Reorient to RAS
`reorient_RAS.py` reorients a nifti input so its axes are in RAS orientation (left to Right, posterior to Anterior, inferior to Superior). It uses [`as_closest_canonical`](https://nipy.org/nibabel/reference/nibabel.funcs.html#as-closest-canonical) while saving the reorientation matrix so the reorientation can be undone. 

## Reorient with reference
`reorient_nifti.py`

## Align and combine with MRtrix3
It is a routine of MRtrix3 commands to align (linear registration), interpolate, and combine (average) a set of images. 
