#!/usr/bin/env python
# coding: utf-8

######################
## IMPORT LIBRARIES ##
######################

# Import python libraries 
import pandas as pd
import sys
import argparse

# Import zfBMD specific functions 
from format_binary_data import format_morpho_input
from format_binary_data import format_lpr_input 
from calculate_BMD_flags import generate_BMD_flags
from select_and_run_models import model_fitting


###########################
## COLLECT CLI ARGUMENTS ##
###########################

parser = argparse.ArgumentParser('Run the QC and BMD analysis as well as join with extract data to store \
in SRP data analytics portal')

parser.add_argument('--morpho', dest='morpho',\
                    help='Pathway to the morphological file to be processed. Required.',\
                    default=None)
parser.add_argument('--LPR', dest='lpr', \
                    help='Pathway to the light photometer response (LPR) file to be processed containing the same \
                          samples as morpho. Optional. Unless both is True, only LPR data will be returned.',\
                    default=None)
parser.add_argument('--both', dest='both', \
                    help='Return both morpho and LPR endpoints. Optional. Default is False.',\
                    default=False)
parser.add_argument('--output', dest = 'output', \
                    help = 'The output folder for files. Default is current directory.',\
                    default = '.')
parser.add_argument('--test', dest='test',\
                    help='Set this flag to test code with internal files. Default is False.',\
                    action='store_true', default=False)
                    
##############################
## DEFINE AND RUN FUNCTIONS ##
##############################

def main():
    """
    Gather the input arguments and run the zfBMD pipeline which: 

    1. formats input data
    2. calculate benchmark doses 
    3. select and run models

    Returns
    ----
    """
    
    # Parse inputted arguments from the command line 
    args = parser.parse_args()

    # Pull arguments
    morpho_path = args.morpho
    lpr_path = args.lpr

    # If there is no morphological data and this is not the test mode, stop. 
    if args.morpho is None and args.test == False:
        sys.exit("--morpho cannot be blank, since morphological data is required to run zfBMD.")
    
    # Users must supply both morpho and lpr data if both is selected
    if args.both and args.lpr is None:
        sys.exit("--lpr cannot be blank if args.both is True.")

    # Load test data if test is true 
    if args.test == True:
        morpho_path = '/zfBmd/test_files/7_PAH_zf_morphology_data_2020NOV11_tall_3756.csv'
        lpr_path = '/zfBmd/test_files/7_PAH_zf_LPR_data_2021JAN11_3756.csv'
    
    ### 1. Format data--------------------------------------------------------------------------
    dose_response, theEndpoints, MortWells, Mort24Wells = format_morpho_input(morpho_path)

    if (args.lpr is not None):
        lpr_dose_response = format_lpr_input(lpr_path, theEndpoints, MortWells, Mort24Wells)

    ### 2. Calculate dose response--------------------------------------------------------------

    if (args.lpr is None or args.both):
        BMD_Flags = generate_BMD_flags(dose_response)

    if (args.lpr is not None):
        lpr_BMD_Flags = generate_BMD_flags(lpr_dose_response) 

    ### 3. Select and run models----------------------------------------------------------------

    if (args.lpr is None or args.both):
        model_selection = model_fitting(dose_response, BMD_Flags)
    
    if (args.lpr is not None):
        lpr_model_selection = model_fitting(lpr_dose_response, lpr_BMD_Flags)

    ### 4. Format outputs-----------------------------------------------------------------------


    



if __name__ == "__main__":
    main()
