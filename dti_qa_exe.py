#!/usr/bin/python3

import os
import logging
import argparse
import dti_qa_lib as dtal

#Preprocessing:
#   1. Apply the DWI mask to the raw DWI data
#   2. Create the 4D image of each shell
#   3. Create the mean image for each shell

#Calculating outlier count metrics:
#   1. Use 3dToutcount on each shell dataset
#   2. Find the maximum outlier count per shell
#   3. Find the mean outlier count per shell

#Calculating motion correction metrics:
#   1. 3dvolreg each shell 4D image using the mean as the base
#   2. Find the maximum displacement for each shell and then for the image

#Calculating TSNR metrics:
#   1. Get TSNR from 3dTstat, using the DWI mask as a mask, for each shell
#   2. Use 3dROIstats to get average TSNR for each shell


#Set up argument parser and help dialogue
parser=argparse.ArgumentParser(
    description='''Create image QA metrics for DWI data. Based on: "The Impact of Quality Assurance Assessment on Diffusion Tensor Imaging Outcomes in a Large-Scale Population-Based Cohort", Roalf et al., Neuroimage, 2016. ''',
    usage='python3 dti_qa.py dti_image mask_image shell_index_file output_dir [--overwrite]')
parser.add_argument('--overwrite', help='if set, delete the output_dir if it already exists', action='store_const', const=1, default=0)
parser.add_argument('subID', help='Subject ID associated with DTI data')
parser.add_argument('dti_image', help='path and filename of a 4D .nii or .nii.gz')
parser.add_argument('mask_image', help='path and filename of a 3D mask .nii or .nii.gz image')
parser.add_argument('shell_index_file', help='path and filename of a b-vector file containing three rows, each with one element per diffusion volume')
parser.add_argument('output_dir', help='output directory where things will be written')
args = parser.parse_args()


def main(args):

    #Set basic logger
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    #Handle arguments
    sub = str(args.subID)
    dti_image = str(args.dti_image)
    mask_image = str(args.mask_image)
    shell_index_file = str(args.shell_index_file)
    output_dir = str(args.output_dir)
    overwrite = int(args.overwrite)

    logging.info('')
    logging.info('-------Input Arguments--------')
    logging.info('sub: {}'.format(sub))
    logging.info('dti_image: {}'.format(dti_image))
    logging.info('mask_image: {}'.format(mask_image))
    logging.info('shell_index_file: {}'.format(shell_index_file))
    logging.info('output_dir: {}'.format(output_dir))
    logging.info('overwrite: {}'.format(overwrite))
    logging.info('------------------------------')
    logging.info('')

    #Try running the QA
    try:
        output_written = dtal.qa_the_dti(sub, dti_image, mask_image, shell_index_file, output_dir, overwrite)
    except Exception as err:
        logging.error('Something went wrong: {}'.format(err))


if __name__ == "__main__":
    main(args)