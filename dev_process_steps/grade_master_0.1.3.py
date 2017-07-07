#!/usr/bin/env python
# recycle "infrastructure" code elements from previous scripts

SCRIPT_NAME = "grade_master"
SCRIPT_VERSION = "v0.1.3"
REVISION_DATE = "2015-03-04"
AUTHOR = "(hachmann@buffalo.edu)"
DESCRIPTION = "This is a small program to help faculty manage course grades, make projections, etc."

# Version history timeline:
# v0.0.1 (2015-03-02): pseudocode outline 
# v0.0.2 (2015-03-02): more detailed pseudocode outline 
# v0.1.0 (2015-03-02): add basic code infrastructure from previous scripts
# v0.1.1 (2015-03-02): add basic functionality (identify data structure of input file)
# v0.1.2 (2015-03-03): add basic functionality (dictionary of dictionaries)

###################################################################################################
# TASKS OF THIS SCRIPT:
# -assorted collection of tools for the analysis of grade data
###################################################################################################

###################################################################################################
#TODO:
# -replaced optparse with argparser
###################################################################################################

import argparse
import sys
import os
import time
import string
# TODO: this should at some point replaced with argparser
from optparse import OptionParser
from collections import defaultdict
# import numpy as np

from lib_jcode import (banner,
                       print_invoked_opts,
                       tot_exec_time_str,
                       intermed_exec_timing,
                       std_datetime_str,
                       chk_rmfile
                       )
     
###################################################################################################

def main(opts,commline_list):
    """(main):
        Driver of the grade_master script.
    """
    time_start = time.time()

    # now the standard part of the script begins
    logfile = open(opts.logfile,'a',0)
    error_file = open(opts.error_file,'a',0)
    
    banner(logfile, SCRIPT_NAME, SCRIPT_VERSION, REVISION_DATE, AUTHOR, DESCRIPTION)

    # give out options of this run
    print_invoked_opts(logfile,opts,commline_list)

    home_dir = os.getcwd() 

    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')


    #################################################################################################

# read in the CSV file with the raw data of grades 
    # make a logfile entry and screen entry so that we know where we stand
    tmp_str = "Start data aquisition... "
    print tmp_str
    logfile.write(tmp_str + '\n')
# TODO: make use of different print levels
    
    # check that file exists, get filename from optparse
    if opts.data_file is None:
        tmp_str = "... data file not specified."
        print tmp_str
        logfile.write(tmp_str + '\n')
        errorfile.write(tmp_str + '\n')
        sys.exit("Aborting due to missing data file.")
# TODO: This should better be done by exception handling
        
    # open file
    data_file = open(opts.data_file,'r')

    # read top line of data file
    line = data_file.readline()
    # use commas for split operation
    words = line.split(',')

    # extract keys, get rid of empty entries
    keys_list = []
    for word in words:
        if word != '' and word != '\r\n':
            keys_list.append(word)

    print words
    print keys_list

    # think how I want to organize data! what would be a useful data structure?
    # how about a dictionary of dictionaries with mixed arguments
    # I want this logic: 
    # data['ID']['first_name'] = "xxx"
    # data['ID']['last_name'] = "yyy"
    # data['ID']['hw_grades'] = []    list of variable entries
    # data['ID']['midterm_grades'] = []    list of variable entries
    # data['ID']['final_grade'] = z   some number
    # how do we realize this? -> stackoverflow: dictionary of dictionaries

    data_dict = defaultdict(lambda : defaultdict(int))
    
    print data_dict

    sys.exit("This is as far as it goes right now.")

    # read bulk of data file
    # use standard infinite loop construct
    
    # close file
    data_file.close()

    tmp_str = "... finished."
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')

# parse and process the raw data, put it in useful data structure
    # read into our data structure

# perform statistics, analysis, projections
    # compute current average according to grading rules 
    # translate points into grades
    # test different grading schemes 
    # rank students
    # identify best, worst students
    # figure out in detail what we want to do

    #################################################################################################

    # wrap up section
    tmp_str = tot_exec_time_str(time_start) + "\n" + std_datetime_str()
    print tmp_str + 3*'\n'
    logfile.write(tmp_str + 4*'\n')
    logfile.close()    
    error_file.close()
    
    # check whether error_file contains content
    chk_rmfile(opts.error_file)
        
    return 0    #successful termination of program
    
#################################################################################################

if __name__=="__main__":
    usage_str = "usage: %prog [options] arg"
    version_str = "%prog " + SCRIPT_VERSION
    parser = OptionParser(usage=usage_str, version=version_str)    

    # it is better to sort options by relevance instead of a rigid structure
    
    # Section for resultcount:
    parser.add_option('--data_file', 
                      dest='data_file', 
                      type='string', 
                      help='specifies the name of the raw data file in CSV format')

    # Generic options 
    parser.add_option('--print_level', 
                      dest='print_level', 
                      type='int', 
                      default=2, 
                      help='specifies the print level for on screen and the logfile [default: %default]')
        
    # specify log files 
    parser.add_option('--logfile', 
                      dest='logfile', 
                      type='string', 
                      default='grade_master.log',  
                      help='specifies the name of the log-file [default: %default]')

    parser.add_option('--errorfile', 
                      dest='error_file', 
                      type='string', 
                      default='grade_master.err',  
                      help='specifies the name of the error-file [default: %default]')

    opts, args = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 2:
        sys.exit("You tried to run grade_master without options.")
    main(opts,sys.argv)
    
else:
    sys.exit("Sorry, must run as driver...")
    