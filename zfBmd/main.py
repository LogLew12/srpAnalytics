#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os, sys, time
import argparse
import tarfile
import re

OUT_FOLDER='/tmp'
IF_EXITS='replace' # options: "append", "replace", "fail"
DB='develop' # options: "develop", "production"


#sys.path.insert(0, './qc_BMD')


##impor  BMD files from directory
import bmd_analysis_morpho as bmd
import bmd_analysis_LPR_7_PAH_t0_t239 as bmd_LPR

parser = argparse.ArgumentParser('Run the QC and BMD analysis as well as join with \
extract data to store in SRP data analytics portal')

#parser.add_argument('--label', dest='label', help='Label to store data', \
#                    default='newdata')
#parser.add_argument('files', nargs='?', default='',\
#                    help='Morphological files for regular BMD input or LPR (with --LPR option)')
parser.add_argument('--morpho', dest='morpho',\
                    help='Comma-delimited list of morphological files to be processed',\
                    default=None)

parser.add_argument('--LPR', dest='lpr', \
                    help='Comma-delimited list of LPR-related files to be processed. MUST correspond to similar files in the morpho argument',\
                    default=None)

parser.add_argument('--test-lpr', dest='test_lpr',\
                    help='Set this flag to run LPR test code instead of full analysis',\
                    action='store_true', default=False)

parser.add_argument('--test-morpho', dest='test_morpho',\
                    help='Set this flag to run morpho test code instead of full analysis',\
                    action='store_true', default=False)

parser.add_argument('--test-extract', dest='test_extract',\
                    help='Set this flag to run morpho test code with extract data',\
                    action='store_true', default=False)

############ (developer comment)
# for morphological data, only morphological data is needed as input
# for LPR processing, both morphological data and LPR data are needed as inputs


def merge_files(path, file_dict):
    """
    merge_files takes a dictionary of files and joints them to a single file to
    added to the next step of the algorithm

    Attributes
    ------
    path : str
    file_dict: dict
    """

    ## three lists of files to collect
    bmds = []
    fits = []
    dose = []
    for dataset, filelist in file_dict.items():
        bmds.append(filelist[0])
        fits.append(filelist[1])
        dose.append(filelist[2])

    ##concatenate all the files together
    pd.concat([pd.read_csv(f) for f in bmds]).to_csv(path+'/new_bmds.csv')
    pd.concat([pd.read_csv(f) for f in fits]).to_csv(path+'/new_fits.csv')
    pd.concat([pd.read_csv(f) for f in dose]).to_csv(path+'/new_dose.csv')
    return [path+'/new_bmds.csv',path+'/new_fits.csv',path+'/new_dose.csv']


def run_lpr_on_file(lpr_file, morph_file, full_devel='full'):
    """
    runs LPR code on a file
    Attributes
    ----
    unformatted_file: str
    """
    LPR_input_csv_file_name_wide = lpr_file[:-4] + "_wide_t0_t239_" + str(full_devel) + ".csv"

    command = "python3 /zfBmd/format_LPR_input.py " + str(lpr_file) + " " + str(full_devel)

    if not os.path.exists(LPR_input_csv_file_name_wide):
        print(command)
        res0 = os.system(command)

    #print ("LPR_input_csv_file_name_wide:" + str(LPR_input_csv_file_name_wide))

    #print ("morpho_input_csv_file_name:" + str(morph_file))
    #to_be_processed/7_PAH_zf_LPR_data_2021JAN11_tall.csv
    morpho_input_csv_file_name_wide = morph_file[:-4] + "_wide_DNC_0.csv"

    if not os.path.exists(morpho_input_csv_file_name_wide):
        command = "python3 /zfBmd/format_morpho_input.py " + str(morph_file) + " " + str(full_devel)
        print(command)
        res0 = os.system(command)
            #time.sleep(20)


    res = bmd_LPR.runBmdPipeline(morpho_input_csv_file_name_wide, \
                                             LPR_input_csv_file_name_wide, full_devel)
    return res

def run_morpho_on_file(morph_file, full_devel='full'):
    """
    formats and runs morphological BMD on file
    """
    print("morpho_input_csv_file_name:" + str(morph_file))
    #to_be_processed/7_PAH_zf_LPR_data_2021JAN11_tall.csv
    command = "python3 /zfBmd/format_morpho_input.py " + str(morph_file) + " " + str(full_devel)
    print(command)
    os.system(command)

    morpho_input_csv_file_name_wide = morph_file[:-4] + \
        "_wide_DNC_0.csv"
    print("morpho_input_csv_file_name_wide:" + str(morpho_input_csv_file_name_wide))
    res = bmd.runBmdPipeline(morpho_input_csv_file_name_wide, \
                                             full_devel)
    return res


def main():
    """
    main method for command line
    """
    start_time = time.time()
    args = parser.parse_args()
    #print(args)
    #flist = args.files.split(',')
    #print(flist)

    ##collecting a list of files to add to DB
    files = dict()

    if args.lpr is None:
        lfiles = ''
    else:
        lfiles = args.lpr.split(',')
    if args.morpho is None:
        mfiles = ''
    else:
        mfiles = args.morpho.split(',')

    print(lfiles)
    print(mfiles)
    fd = 'full'
    if args.test_lpr:
        print("Testing LPR code\n")
        lfiles = ['/zfBmd/test_files/7_PAH_zf_LPR_data_2021JAN11_3756.csv']
        mfiles = ['/zfBmd/test_files/7_PAH_zf_morphology_data_2020NOV11_tall_3756.csv']
        fd = 'devel'
 #       files['test'] = run_lpr_on_file(test_lpr, test_morph, 'devel')
    elif args.test_morpho:
        mfiles = ['/zfBmd/test_files/7_PAH_zf_morphology_data_2020NOV11_tall_3756.csv']
        print("Testing morphological code\n")
        fd = 'devel'
#        files['test'] = run_morpho_on_file(test_morph, 'devel')

    if len(lfiles) > 0:
        if len(lfiles) != len(mfiles):
            print("Cannot calculate LPR without morphological files, please re-run with --morpho argument")
            sys.exit()
        else:
            print('Calculating LPR endpoints for '+str(len(lfiles))+' LPR files')
            for i in range(len(lfiles)):
                fname = lfiles[i]
                files[fname] = run_lpr_on_file(fname, mfiles[i], fd)
    elif len(mfiles) > 0:
        print("Calculating morphological endpoints for "+str(len(mfiles))+' files')
        for f in mfiles:
            files[f] = run_morpho_on_file(f, fd)

    end_time = time.time()
    time_took = str(round((end_time-start_time), 1)) + " seconds"
    print ("Done, it took:" + str(time_took))


if __name__ == "__main__":
    main()
