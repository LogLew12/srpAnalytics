#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os, sys, time
import argparse
sys.path.insert(0, './qc_BMD')
#from qc_BMD import bmd_analysis_full as bmd
from qc_BMD import bmd_analysis_02 as bmd

parser = argparse.ArgumentParser('Run the QC and BMD analysis as well as join with \
extract data to store in SRP data analytics portal')

#parser.add_argument('--label', dest='label', help='Label to store data', \
#                    default='newdata')
parser.add_argument('--isSample', dest='isSample', action='store_true',\
                    default=False, help='Set this flag if we \
                    are processing a sample not a chemical')
parser.add_argument('files', nargs='?', default='')
parser.add_argument('--devel', dest='devel',\
                    help='Set this flag to run test code instead of full analysis',\
                    action='store_true', default=False)
parser.add_argument('--LPR', dest='LPR',\
                    help='Set this flag to run LPR code instead of morphological endpoint',\
                    action='store_true', default=False)

if __name__ == "__main__":
    args = parser.parse_args()
    flist = args.files.split(',')
    print(flist)

    if len(flist)==0:
        print("No new files, just re-building archive")
        command = "Rscript /srpAnalytics/03_mergeWithExtracts.R"
        os.system(command)
    else:
        for input_csv_file_name in flist:
            #  if args.isSample:
            ##this doesn't exist yet - we need to read in sample information and merge with
            ##existing dose response data
            #      command = "Rscript 04_mergeWithChems.R "+str(input_csv_file_name)
            #      print(command)
            #      os.system(command)
            #  else:
            if args.devel:
                full_devel = "devel"
            else:
                full_devel = "full"
                
            if args.LPR == False:
                command = "python3 /srpAnalytics/01_reformat_df_data.py " + str(input_csv_file_name)
                print(command)
                os.system(command)
            else:
                # for LPR reformatting both morphological and LPR is needed
                command = "python3 /srpAnalytics/01_reformat_df_data.py " + str(input_csv_file_name)
                print(command)
                os.system(command)
                
                command = "python3 /srpAnalytics/01_reformat_df_LPR_data.py " + str(input_csv_file_name) + " " + str(full_devel)
                print(command)
                os.system(command)
            
            
            output_complete_file_path = input_csv_file_name[:-4] + "_wide_DNC_0.csv"
            
            if args.LPR == True:
                output_complete_file_path_LPR = input_csv_file_name[:-4] + "_wide_t0_t239_" + str(full_devel) + ".csv"
            
            #print ("output_complete_file_path:" + str(output_complete_file_path))
            # actual file is not saved here, but it is ok to be used at following procedures
            
            
            #command = "python3 /srpAnalytics/qc_BMD/02_bmd_analysis.py " + \
                #    str(output_complete_file_path)
            
            if args.LPR == False:
                files = bmd.runBmdPipeline(output_complete_file_path, full_devel)
            else:
                files = bmd.runBmdPipeline_LPR(output_complete_file_path_LPR, output_complete_file_path, full_devel)

            command = "Rscript /srpAnalytics/03_mergeWithExtracts.R "
            if args.isSample:
                command = command+'--samples  '
            else:
                command = command+'--chemicals '
            if len(files) == 3:
                command = command + ','.join(files)
                print(command)
                os.system(command)
