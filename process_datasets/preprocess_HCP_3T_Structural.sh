#!/usr/bin/zsh

# Process HCP structural 
# Diana Giraldo, August 2024

# .zip file
IN_ZIP=${1}

# Output directory
OUT_DIR=${2}

# MRI Toolkit directory
SCR_DIR=/home/vlab/mri_toolkit
# ANTs directory
ANTS_DIR=/opt/ANTs/bin

# Make temporary directory
TMP_DIR=$(mktemp -d)

# Unzip 
unzip ${IN_ZIP} -d ${TMP_DIR}

#IM_ID=$(ls ${TMP_DIR})

# T1
T1=$(ls ${TMP_DIR}/*/unprocessed/3T/T1w_MPR*/*T1w_MPR*.nii.gz | head -n 1 )
${SCR_DIR}/preprocess.sh ${T1} ${OUT_DIR} ${ANTS_DIR}

# T2
T2=$(ls ${TMP_DIR}/*/unprocessed/3T/T2w_SP*/*T2w_SP*.nii.gz | head -n 1 )
${SCR_DIR}/preprocess.sh ${T2} ${OUT_DIR} ${ANTS_DIR}

rm -r ${TMP_DIR}