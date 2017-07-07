#!/usr/bin/env python
# recycle "infrastructure" code elements from previous scripts

SCRIPT_NAME = "grade_master"
SCRIPT_VERSION = "v0.1.8"
REVISION_DATE = "2015-03-05"
AUTHOR = "(hachmann@buffalo.edu)"
DESCRIPTION = "This is a small program to help faculty manage course grades, make projections, etc."

# Version history timeline:
# v0.0.1 (2015-03-02): pseudocode outline 
# v0.0.2 (2015-03-02): more detailed pseudocode outline 
# v0.1.0 (2015-03-02): add basic code infrastructure from previous scripts
# v0.1.1 (2015-03-02): add basic functionality (identify data structure of input file)
# v0.1.2 (2015-03-03): add basic functionality (dictionary of dictionaries)
# v0.1.3 (2015-03-04): implement dictionary of dictionaries properly
# v0.1.4 (2015-03-04): put in some checks and read in the data into dictionary
# v0.1.5 (2015-03-04): revamp the data structure
# v0.1.6 (2015-03-04): implement grading rules
# v0.1.7 (2015-03-05): implement letter grades
# v0.1.8 (2015-03-05): fix rounding error in letter grades

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


    n_keys = len(keys_list)
    
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

    data_dict = defaultdict(lambda : defaultdict(int))  # note: we use the anonymous function construct lambda here

    # let's collect the 
    id_list = []

    # read bulk of data file
    # use standard read in with infinite loop construct
    while 1:
        line = data_file.readline()
        if not line: break        
        words = line.split(',')
        # we have to put the data somewhere, so let's try a list for the time being
        data_list = []
        for word in words:
            if word != '' and word != '\r\n':   # again, get rid of junk data
                data_list.append(word)  # populate data_list

        
# TODO: we should have some check here to account for non-uniformity issues 
        # the least that has to be given is that the data_list and key_list have to have the same lenght
        # TODO: we should probably do more than that but we can figure that out later
        if len(data_list) == n_keys:
            id = data_list[2]
            id_list.append(id)
            hw_list = []
            midterm_list = []
            for i in xrange(n_keys):    # note that we use xrange instead of range
                key = keys_list[i]
                data = data_list[i]
                if key == "Last name":
                    data_dict[id]['last_name'] = data 
                elif key == "First name":
                    data_dict[id]['first_name'] = data 
                elif key == "Student ID":
                    continue
                elif 'HW' in key:
                    hw_list.append(float(data))         # don't forget to convert string to float
                elif (key == 'M1') or (key == 'M2'):    # careful, since we basically hardwire this; we may want to implement a more general version down the road
                    midterm_list.append(float(data))    # don't forget to convert string to float
                elif key == 'Final':
                    data_dict[id]['final_grade'] = float(data)
                else:
                    sys.exit("There is something funny going on here. We have an unknown key!")

            # now we have to put lists into dictionary                    
            data_dict[id]['hw_grades'] = hw_list
            data_dict[id]['midterm_grades'] = midterm_list
            
            print data_dict[id]
            print 
 
    # close file
    data_file.close()

# TODO: well, this is not yet the data structure we want, so we have to rewrite a little 
                 

# perform statistics, analysis, projections
# compute current average according to grading rules 
    # implement grading rules: HW: 20%, better midterm 35%, worse midterm 15%, final: 30%
    # cast this into different scenarios
    if 'Final' in keys_list:
        for id in id_list:
            hw_average = sum(data_dict[id]['hw_grades'])/len(data_dict[id]['hw_grades'])
            midterm_max = max(data_dict[id]['midterm_grades'])
            midterm_min = min(data_dict[id]['midterm_grades'])
            final = data_dict[id]['final_grade']    # this is really for readability
            grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*final

            data_dict[id]['hw_grade_av'] = hw_average
            data_dict[id]['midterm_grade_max'] = midterm_max
            data_dict[id]['midterm_grade_min'] = midterm_min
            data_dict[id]['grade_total'] = grade_total
            
    elif 'M2' in keys_list:
            hw_average = sum(data_dict[id]['hw_grades'])/len(data_dict[id]['hw_grades'])
            midterm_max = max(data_dict[id]['midterm_grades'])
            midterm_min = min(data_dict[id]['midterm_grades'])
            midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])

            grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*midterm_average

            data_dict[id]['hw_grade_av'] = hw_average
            data_dict[id]['midterm_grade_max'] = midterm_max
            data_dict[id]['midterm_grade_min'] = midterm_min
            data_dict[id]['grade_total'] = grade_total
        
    elif 'M1' in keys_list:
            hw_average = sum(data_dict[id]['hw_grades'])/len(data_dict[id]['hw_grades'])
            midterm_max = max(data_dict[id]['midterm_grades'])
            midterm_min = min(data_dict[id]['midterm_grades'])
            midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])

            grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*midterm_average

            data_dict[id]['hw_grade_av'] = hw_average
            data_dict[id]['midterm_grade_max'] = midterm_max
            data_dict[id]['midterm_grade_min'] = midterm_min
            data_dict[id]['grade_total'] = grade_total

    elif 'HW1' in keys_list:
# TODO: test if this really works
            hw_average = sum(data_dict[id]['hw_grades'])/len(data_dict[id]['hw_grades'])
#             midterm_max = max(data_dict[id]['midterm_grades'])
#             midterm_min = min(data_dict[id]['midterm_grades'])
#             midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])

            grade_total = hw_average 

            data_dict[id]['hw_grade_av'] = hw_average
#             data_dict[id]['midterm_grade_max'] = midterm_max
#             data_dict[id]['midterm_grade_min'] = midterm_min
            data_dict[id]['grade_total'] = grade_total    
    else:
        sys.exit("No grades given right now, so there is not much we can do.")


    print id_list 
    # test if this works
    for id in id_list:
        print str(id) + ' ' + str(data_dict[id]['grade_total'])


    
    # translate points into grades
    for id in id_list:
        if round(data_dict[id]['grade_total']) >= 96:
            data_dict[id]['letter_grade'] = 'A'
        elif round(data_dict[id]['grade_total']) >= 91:
            data_dict[id]['letter_grade'] = 'A-'
        elif round(data_dict[id]['grade_total']) >= 86:
            data_dict[id]['letter_grade'] = 'B+'
        elif round(data_dict[id]['grade_total']) >= 81:
            data_dict[id]['letter_grade'] = 'B'
        elif round(data_dict[id]['grade_total']) >= 76:
            data_dict[id]['letter_grade'] = 'B-'
        elif round(data_dict[id]['grade_total']) >= 71:
            data_dict[id]['letter_grade'] = 'C+'
        elif round(data_dict[id]['grade_total']) >= 66:
            data_dict[id]['letter_grade'] = 'C'
        elif round(data_dict[id]['grade_total']) >= 61:
            data_dict[id]['letter_grade'] = 'C-'
        elif round(data_dict[id]['grade_total']) >= 56:
            data_dict[id]['letter_grade'] = 'D+'
        elif round(data_dict[id]['grade_total']) >= 51:
            data_dict[id]['letter_grade'] = 'D'
        else:
            data_dict[id]['letter_grade'] = 'F'

    # test if this works
    for id in id_list:
        print str(id) + ' ' + str(data_dict[id]['grade_total'])+ ' ' + data_dict[id]['letter_grade']


    # rank students

    sys.exit("This is as far as it goes right now.")

    # course average
    # rank students
    # identify best, worst students
    # test CSV files at different stages of semester

    # figure out in detail what we want to do
    # follow progress throughout the semester - here we will need an order criterion
    # test different grading schemes 
    

    tmp_str = "... finished."
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')


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
    