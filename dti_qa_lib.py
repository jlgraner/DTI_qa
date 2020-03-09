import subprocess
import os, sys, shutil
import logging
import numpy


def __add_prefix(input_file, prefix):
    #This function appends a string to the existing prefix of an image file.
    #It assumes the image file is either .nii or .nii.gz.
    input_beginning, input_end = input_file.split('.nii')
    output_file = input_beginning+str(prefix)+'.nii'+input_end
    return output_file


def select_trs(input_image, output_image, volume_string, overwrite=0):
    #This function uses AFNI's 3dTcat to select a number of TRs from
    #a 4D image.
    logging.info('-------Starting: select_trs-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('select_trs: bad input image')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('select_trs: bad input image')

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            logging.info('output_image already exists...')
            if overwrite:
                logging.info('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                logging.error('ERROR: output_image already there and overwrite not set!')
                raise RuntimeError('select_trs: output_image already exists!')

        #Put together call to 3dTcat
        call_parts = [
                   '3dTcat',
                   '-prefix',
                   output_image,
                   input_image+'[{}]'.format(volume_string)
                  ]

        logging.info('Selecting TRs for shell...')

        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

        if not os.path.exists(output_image):
            logging.error('ERROR: output_image should be there, but is not: {}'.format(output_image))
            raise RuntimeError('select_trs: call to 3dTcat failed!')
    except:
        logging.error('ERROR: in selecting TRs!')
        raise RuntimeError('select_trs: selecting TRs failed somewhere!')

    logging.info('TR removal successful.')
    logging.info('-------Done: select_trs-------')
    return output_image



def create_mean(input_image, output_image, overwrite=0):
    #This function uses AFNI's 3dTstat to create a mean image.
    logging.info('-------Starting: create_means-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('create_mean: bad input image')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('create_mean: bad input image')

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            logging.info('output_image already exists...')
            if overwrite:
                logging.info('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                logging.error('ERROR: output_image already there and overwrite not set!')
                raise RuntimeError('create_mean: output_image already exists!')

        #Put together call to 3dMean
        call_parts = [
                   '3dTstat',
                   '-mean',
                   '-prefix',
                   output_image,
                   input_image
                  ]

        logging.info('Creating mean image...')

        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

        if not os.path.exists(output_image):
            logging.error('ERROR: output_image should be there, but is not: {}'.format(output_image))
            raise RuntimeError('create_mean: call to 3dMean failed!')
    except:
        logging.error('ERROR: in selecting TRs!')
        raise RuntimeError('create_mean: selecting TRs failed somewhere!')

    logging.info('Mean image creation successful.')
    logging.info('-------Done: create_mean-------')
    return output_image



def apply_mask(input_image, mask_image, output_image, overwrite=0, skip=0):
    #This function takes a binary mask image and applies it to another image
    #using AFNI's 3dCalc.
    logging.info('-------Starting: apply_mask-------')

    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('input_image must contain full path')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('input_image not .nii or .nii.gz')

        #Check the mask file for a path
        mask_path, mask_file = os.path.split(mask_image)
        if mask_path is '':
            logging.error('ERROR: mask_image must contain a full path to the mask file!')
            raise RuntimeError('mask_image must contain full path')

        #Check that the mask file is either .nii or .nii.gz
        if len(mask_file.split('.nii')) == 1:
            logging.error('ERROR: mask_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('mask_image not .nii or .nii.gz')

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            logging.info('output_image already exists...')
            if overwrite:
                logging.info('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                logging.error('ERROR: output_image already there and overwrite not set!')
                raise RuntimeError('calc_tsnr: output_image already exists!')

        #Create call to mask the image
        logging.info('Creating call parts list...')
        call_parts = [
                      '3dcalc',
                      '-a', input_image,
                      '-b', mask_image,
                      '-float',
                      '-prefix', output_image,
                      '-expr', 'a*b'
                     ]
        #Carry out masking
        logging.info('...applying mask...')
        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()
    except Exception as err:
        logging.error('ERROR applying mask: {}'.format(err))
        raise RuntimeError('error applying mask')

    print('Masking successful.')
    print('-------Done: apply_mask-------')
    return output_image


def outcount(input_image, mask_image):
    #This function uses AFNI's 3dToutcount to create a file listing
    #the number of outlying voxels in each volume of an image.
    logging.info('-------Starting: outcount-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('outcount: bad input image')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('outcount: bad input image')

        #Check the mask file for a path
        mask_path, mask_file = os.path.split(mask_image)
        if mask_path is '':
            logging.error('ERROR: mask_image must contain a full path to the mask file!')
            raise RuntimeError('mask_image must contain full path')

        #Check that the mask file is either .nii or .nii.gz
        if len(mask_file.split('.nii')) == 1:
            logging.error('ERROR: mask_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('mask_image not .nii or .nii.gz')

        #Put together call to 3dToutcount
        call_parts = [
                   '3dToutcount',
                   '-mask', mask_image,
                   input_image
                  ]

        logging.info('Calculating outlier counts...')

        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

        #Find the mean and max of the 3dToutcount output
        outcount_array = numpy.array(call_output.split(), dtype=int)
        outcount_mean = outcount_array.mean()
        outcount_max = outcount_array.max()
        outcount_max_index = numpy.argmax(outcount_array)
        outcount_max_volume = outcount_max_index+1

    except:
        logging.error('ERROR: 3dToutcount failed!')
        raise RuntimeError('outcount: 3dToutcount run failed somewhere!')

    logging.info('Outlier count calculation successful.')
    logging.info('-------Done: outcount-------')
    return outcount_mean, outcount_max, outcount_max_volume


def motion_correct(input_image, base_image, output_image, overwrite=1):
    #This function runs motion correction on an input image, using another image
    #as the base for registration.
    logging.info('-------Starting: motion_correct-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('input_image must contain full path')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('input_image not .nii or .nii.gz')

        #Check the base file for a path
        base_path, base_file = os.path.split(base_image)
        if base_path is '':
            logging.error('ERROR: base_image must contain a full path to the mask file!')
            raise RuntimeError('base_image must contain full path')

        #Check that the base file is either .nii or .nii.gz
        if len(base_file.split('.nii')) == 1:
            logging.error('ERROR: base_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('base_image not .nii or .nii.gz')

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            logging.info('output_image already exists...')
            if overwrite:
                logging.info('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                logging.error('ERROR: output_image already there and overwrite not set!')
                raise RuntimeError('calc_tsnr: output_image already exists!')
        #Create maxdisp output file
        motcor_out_maxdisp = output_image.split('.nii')[0]+'_maxdisp.txt'
        #Check to see if output motion-corrected image is already there
        for element in [output_image, motcor_out_maxdisp]:
            if os.path.exists(element):
                logging.info('motion-correction file already exists: {}'.format(element))
                if overwrite:
                    logging.info('Overwrite set to 1, deleting: {}'.format(element))
                    os.remove(element)
                else:
                    logging.error('Motion-corrected file already exists and overwrite not set, exitting...')
                    raise RuntimeError('motion-corrected file exists and overwrite not set')

        #Create call to motion-correct the image
        logging.info('Creating call parts list...')
        call_parts = [
                      '3dvolreg',
                      '-prefix', output_image,
                      '-float',
                      '-maxdisp1D', motcor_out_maxdisp,
                      '-base', base_image,
                      input_image
                     ]
        #Carry out motion correction
        logging.info('...running motion correction...')
        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()
    except Exception as err:
        logging.error('ERROR running motion correction: {}'.format(err))
        raise RuntimeError('error running motion correction')

    print('Motion correction successful.')
    print('-------Done: motion_correct-------')
    return output_image, motcor_out_maxdisp


def calc_tsnr(input_image, mask_image, output_image, overwrite=1):
    #Calculate a 3D voxel-wise TSNR image from the input 4D image
    logging.info('-------Starting: calc_tsnr-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('outcount: bad input image')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('outcount: bad input image')

        #Check the mask file for a path
        mask_path, mask_file = os.path.split(mask_image)
        if mask_path is '':
            logging.error('ERROR: mask_image must contain a full path to the mask file!')
            raise RuntimeError('mask_image must contain full path')

        #Check that the mask file is either .nii or .nii.gz
        if len(mask_file.split('.nii')) == 1:
            logging.error('ERROR: mask_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('mask_image not .nii or .nii.gz')

        #Check to see if passed output image is already there
        if os.path.exists(output_image):
            logging.info('output_image already exists...')
            if overwrite:
                logging.info('Overwrite set to 1, deleting...')
                os.remove(output_image)
            else:
                logging.error('ERROR: output_image already there and overwrite not set!')
                raise RuntimeError('calc_tsnr: output_image already exists!')

        #Put together call to 3dToutcount
        call_parts = [
                   '3dTstat',
                   '-tsnr',
                   '-mask', mask_image,
                   '-prefix', output_image,
                   input_image
                  ]

        logging.info('Calculating TSNR image...')

        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

    except:
        logging.error('ERROR: 3dTstat failed!')
        raise RuntimeError('calc_tsnr: 3dToutcount run failed somewhere!')

    logging.info('TSNR image calculation successful.')
    logging.info('-------Done: calc_tsnr-------')
    return output_image


def ave_tsnr(input_image, mask_image):
     #This function uses AFNI's 3dROIstats to calculate the average
     #TSNR for the image.
    logging.info('-------Starting: ave_tsnr-------')
    try:
        #Check the input file for a path
        input_path, input_file = os.path.split(input_image)
        if input_path is '':
            logging.error('ERROR: input_image must contain a full path to the image file!')
            raise RuntimeError('ave_tsnr: bad input image')

        #Check that the input file is either a .nii or .nii.gz file
        if len(input_file.split('.nii')) == 1:
            logging.error('ERROR: input_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('ave_tsnr: bad input image')

        #Check the mask file for a path
        mask_path, mask_file = os.path.split(mask_image)
        if mask_path is '':
            logging.error('ERROR: mask_image must contain a full path to the mask file!')
            raise RuntimeError('mask_image must contain full path')

        #Check that the mask file is either .nii or .nii.gz
        if len(mask_file.split('.nii')) == 1:
            logging.error('ERROR: mask_image file type not recognized. Should be .nii or .nii.gz!')
            raise RuntimeError('mask_image not .nii or .nii.gz')

        #Put together call to 3dToutcount
        call_parts = [
                   '3dROIstats',
                   '-nzmean',
                   '-quiet',
                   '-nomeanout',
                   '-nobriklab',
                   '-mask', mask_image,
                   input_image
                  ]

        logging.info('Calculating average TSNR...')

        logging.info('Calling: {}'.format(' '.join(call_parts)))
        proc = subprocess.Popen(call_parts, stdout=subprocess.PIPE)
        call_output, stderr = proc.communicate()

        #Isolate the number in the output
        average_tsnr = float(call_output.strip())

    except:
        logging.error('ERROR: 3dROIstats failed!')
        raise RuntimeError('ave_tsnr: 3dROIstats run failed somewhere!')

    logging.info('Average TSNR calculation successful.')
    logging.info('-------Done: ave_tsnr-------')
    return average_tsnr


def qa_the_dti(sub, dti_image, mask_image, shell_index_file, output_dir, overwrite):

    #Check inputs
    if not os.path.exists(dti_image):
        logging.error('ERROR: dti_image cannot be found: {}'.format(dti_image))
        raise RuntimeError('dti_image not found!')

    output_file = __add_prefix(dti_image, '_QA_metrics')
    output_file = output_file.split('.nii')[0]+'.csv'
    output_file = os.path.join(output_dir, os.path.split(output_file)[-1])

    if os.path.exists(output_file) and overwrite==0:
        logging.error('ERROR: output_file exists and overwrite not set!')
        raise RuntimeError('output_file exists and overwrite not set!')
    elif os.path.exists(output_file) and overwrite==1:
        logging.info('output_file exists and overwrite set; deleting it!')
        os.remove(output_file)

    if not os.path.exists(mask_image):
        logging.error('ERROR: mask_image cannot be found: {}'.format(mask_image))
        raise RuntimeError('mask_image not found!')

    if not os.path.exists(shell_index_file):
        logging.error('ERROR: shell_index_file not found: {}'.format(shell_index_file))
        raise RuntimeError('shell_index_file not found!')

    try:
        #Create dictionary to house the information for each shell
        metric_dict = {}

        #Create output directory
        if not os.path.exists(output_dir):
            logging.info('Creating output directory...')
            os.makedirs(output_dir)

        #Read in b0 shell index file ('0' means a b=0 volume, '1' indicates the first shell, '2' indicates the second shell, etc.)
        with open(shell_index_file, 'r') as fid:
            contents = fid.read()
        shell_index_list = contents.split(' ')
        ##Determine which volumes correspond to each shell
        #Find the number of unique entries in the shell index list
        unique_shell_list = list(set(shell_index_list))
        #Look for a '0' in the list, indicating at least one b=0 volume
        if '0' not in unique_shell_list:
            logging.error('ERROR: shell_index_file did not contain any 0s, suggesting no b=0 volumes! There should be at least one!')
            raise RuntimeError('shell_index_file contains no 0s')

        #Create the masked output file name
        masked_output = os.path.join(output_dir, os.path.split(__add_prefix(dti_image, '_brain'))[-1])

        #Apply the mask to the full dwi image
        dti_masked_image = apply_mask(dti_image, mask_image, masked_output, overwrite=overwrite, skip=1)

        #Set the shell file name template
        shell_file = __add_prefix(dti_masked_image, '_shell{}')

        number_of_shells = len(unique_shell_list)-1
        unique_shell_list.sort()
        for element in unique_shell_list:
            #For each shell...
            if element != '0':
                shell_label = element
                metric_dict[shell_label] = {}
                shell_volume_string = ''
                #Create list of volumes in this shell
                for count in range(len(shell_index_list)):
                    if shell_index_list[count] == shell_label:
                        shell_volume_string = shell_volume_string+str(count)+','
                #Remove the trailing ','
                shell_volume_string = shell_volume_string[:-1]
                #Create an image of just the shell volumes
                output_image = shell_file.format(shell_label)
                shell_image = select_trs(dti_image, output_image, shell_volume_string, overwrite=overwrite)

                #Create the mean image of the shell
                mean_output = __add_prefix(shell_image, '_mean')
                mean_shell_image = create_mean(shell_image, mean_output, overwrite=overwrite)

                ##Extract outlier metrics##
                #Use 3dToutcount on the shell image
                outcount_mean, outcount_max, outcount_max_volume = outcount(shell_image, mask_image)

                #Save the outcount mean and max to the working dictionary
                metric_dict[shell_label]['outcount_mean'] = outcount_mean
                metric_dict[shell_label]['outcount_max'] = outcount_max
                metric_dict[shell_label]['outcount_max_volume'] = outcount_max_volume

                ##Extract motion metrics##
                #Create motion correction files
                volreg_output = __add_prefix(shell_image, '_volreg')
                volreg_image, maxdisp_file = motion_correct(shell_image, mean_shell_image, volreg_output, overwrite=overwrite)

                #Find maximum max displacement for this shell
                with open(maxdisp_file, 'r') as fid:
                    maxdisp_contents = fid.read()
                maxdisp_array = numpy.array(maxdisp_contents.split('\n ')[1:], dtype=float)
                motcor_maxdisp_volume = numpy.argmax(maxdisp_array)+1
                metric_dict[shell_label]['maxdisp'] = maxdisp_array.max()
                metric_dict[shell_label]['maxdisp_volume'] = motcor_maxdisp_volume

                ##Extract TSNR metrics
                #Create a 3D voxel-wise TSNR image
                tsnr_output = __add_prefix(shell_image, '_tsnr')
                tsnr_image = calc_tsnr(shell_image, mask_image, tsnr_output, overwrite=overwrite)

                #Calculate average TSNR from the 3D TSNR image
                tsnr = ave_tsnr(tsnr_image, mask_image)
                metric_dict[shell_label]['tsnr_mean'] = tsnr

        header_line = 'sub,shell,outcount_mean,outcount_max,outcount_max_volume,maxdisp,maxdisp_volume,tsnr_mean'
        lines_to_write = []
        lines_to_write.append(header_line)
        for key in metric_dict.keys():
            new_line = '{},{},{},{},{},{},{}'.format(sub,key,metric_dict[key]['outcount_mean'],metric_dict[key]['outcount_max'],metric_dict[key]['outcount_max_volume'],metric_dict[key]['maxdisp'],metric_dict[key]['maxdisp_volume'],metric_dict[key]['tsnr_mean'])
            lines_to_write.append(new_line)
        logging.info('Writing output file: {}'.format(output_file))
        with open(output_file, 'w') as fid:
            for line in lines_to_write:
                fid.write(line+'\n')
        logging.info('Finished well.')
    except Exception as err:
        logging.error('Something went wrong: {}'.format(err))