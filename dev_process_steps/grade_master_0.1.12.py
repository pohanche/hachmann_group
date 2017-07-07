#!/usr/bin/env python

SCRIPT_NAME = "grade_master"
SCRIPT_VERSION = "v0.1.12"
REVISION_DATE = "2015-03-09"
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
# v0.1.9 (2015-03-05): some more analysis
# v0.1.10 (2015-03-05): student ranking
# v0.1.11 (2015-03-09): grades throughout the semester
# v0.1.12 (2015-03-09): cleanup and rewrite; also, clean up the print statements; introduce two other input file for debugging that are more realistic, easier; 
                         #build in a few extra safety checks  

###################################################################################################
# TASKS OF THIS SCRIPT:
# -assorted collection of tools for the analysis of grade data
###################################################################################################

###################################################################################################
#TODO:
# -replaced optparse with argparser
# -make use of different print levels
###################################################################################################

import sys
import os
import time
import string
# TODO: this should at some point replaced with argparser
# import argparse
from optparse import OptionParser
from collections import defaultdict
from operator import itemgetter
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
    tmp_str = "Starting data acquisition..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    
    # check that file exists, get filename from optparse
    if opts.data_file is None:
        tmp_str = "... data file not specified!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')

        tmp_str = "Aborting due to missing data file!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
# TODO: This should better be done by exception handling
        
        
    # open CSV file with raw data
    data_file = open(opts.data_file,'r')


    tmp_str = "   ...reading in data structure..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # read top line of data file, which defines the keys
    line = data_file.readline()
    # use commas for split operation
    words = line.split(',')
    # extract keys, get rid of empty entries
    keys_list = []
    for word in words:
        if word != '' and word != '\r\n':
            keys_list.append(word)
    n_keys = len(keys_list)    


    tmp_str = "   ...checking validity of data structure..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    # check that the standard keys are amongst the first three keys, because that's all we have implemented so far 
    if "Last name" not in keys_list[0:3]:
        tmp_str = "   ...'Last name' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to unknown data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    elif "First name" not in keys_list[0:3]:
        tmp_str = "   ...'First name' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to unknown data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    elif "Student ID" not in keys_list[0:3]:
        tmp_str = "   ...'Student ID' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to unknown data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    
     
    # suitable data structure for raw and derived data: dictionary of dictionaries with mixed arguments -> stackoverflow
    # template:
    # data_dict['ID']['first_name'] = "xxx"
    # data_dict['ID']['last_name'] = "yyy"
    # data_dict['ID']['hw_grades'] = []    list of variable entries
    # data_dict['ID']['midterm_grades'] = []    list of variable entries
    # data_dict['ID']['final_grade'] = z   some number
    data_dict = defaultdict(lambda : defaultdict(int))  # note: we use the anonymous function construct lambda here

    # make ID list since this is our distinguishing dictionary key 
    id_list = []


    tmp_str = "   ...reading in bulk of data..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # use standard read in with infinite loop construct
    while 1:
        line = data_file.readline()
        if not line: break        
        words = line.split(',')
        # temporary data list
        data_list = []
        for word in words:
            # get rid of junk data
            if word != '' and '\r\n' not in word:   # note: we had to make junk removal more general
                # populate the temporary data_list
                data_list.append(word)  

        
        # continue if data_list is emptycheck that we don't have an empty list
        if len(data_list) == 0:
            continue
        # check that the data_list and key_list have to have the same lenght
        elif len(data_list) != n_keys:
            tmp_str = "   ...invalid data entry (wrong number of data entries): " + line
            print tmp_str
            logfile.write(tmp_str + '\n')
            error_file.write(tmp_str + '\n')
            tmp_str = "Aborting due to invalid data entry!"
            logfile.write(tmp_str + '\n')
            error_file.write(tmp_str + '\n')
            sys.exit(tmp_str)
        # TODO: think about a more sophisticated handling in case of problems


        # find index of list element in keys_list that contains the id
        id_index = keys_list.index("Student ID")                    
        # get id
        id = data_list[id_index]
        # add id to id_list
        id_list.append(id)
        # set up hw and midterm lists to get added to dictionary later
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
            elif (key == 'M1') or (key == 'M2'):    
                midterm_list.append(float(data))    # don't forget to convert string to float
            elif key == 'Final':
                data_dict[id]['final_grade'] = float(data)  # don't forget to convert string to float
            else:
                sys.exit("Aborting due to unknown key!")

        # now we have to put lists into dictionary                    
        data_dict[id]['hw_grades'] = hw_list
        data_dict[id]['midterm_grades'] = midterm_list

 
    # close file
    data_file.close()

    tmp_str = "...data acquisition finished."
    print tmp_str
    logfile.write(tmp_str + '\n')
    

    #################################################################################################


    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "Summary of acquired data:"
    print tmp_str
    logfile.write(tmp_str + '\n')
    
    tmp_str = "   Number of students:  " + str(len(id_list))
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of homeworks: " + str(len(hw_list))
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of midterms:  " + str(len(midterm_list))
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of finals:    " + str(int(key == 'Final'))
    print tmp_str
    logfile.write(tmp_str + '\n')
# TODO: this should be better formatted    

    #################################################################################################


    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "Starting calculation of grade projections..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    sys.exit("This is as far as it goes right now.")
    

# perform statistics, analysis, projections
# compute current average according to grading rules 
    # create empty lists of grades
    for id in id_list:
        data_dict[id]['hw_grade_av'] = []
        data_dict[id]['midterm_grade_max'] = []
        data_dict[id]['midterm_grade_min'] = []
        data_dict[id]['grade_total'] = []
    
    # for better readability introduce assignment keys list; trade resources for readability 
    assignment_keys_list = keys_list[3:]
    n_assignment_keys = len(assignment_keys_list)

    print assignment_keys_list
    print n_assignment_keys
    
    for i in xrange(n_assignment_keys):
        print assignment_keys_list[0:i+1]


    # implement grading rules: HW: 20%, better midterm 35%, worse midterm 15%, final: 30%
    # cast this into different scenarios
    # we want grades for every point during the semester, so we create 
    for i in xrange(n_assignment_keys):
        if 'Final' in assignment_keys_list[0:i+1]:
            for id in id_list:
                hw_average = sum(data_dict[id]['hw_grades'])/len(data_dict[id]['hw_grades'])
                midterm_max = max(data_dict[id]['midterm_grades'])
                midterm_min = min(data_dict[id]['midterm_grades'])
                final = data_dict[id]['final_grade']    # this is really for readability
                grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*final
    
                data_dict[id]['hw_grade_av'].append(hw_average)
                data_dict[id]['midterm_grade_max'].append(midterm_max)
                data_dict[id]['midterm_grade_min'].append(midterm_min)
                data_dict[id]['grade_total'].append(grade_total)
                
        elif 'M2' in assignment_keys_list[0:i+1]:
            n_hw = 0
            for key in assignment_keys_list[0:i+1]:
                if "HW" in key:
                    n_hw +=1
            for id in id_list:            
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = max(data_dict[id]['midterm_grades'])
                midterm_min = min(data_dict[id]['midterm_grades'])
                midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])
    
                grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*midterm_average
    
                data_dict[id]['hw_grade_av'].append(hw_average)
                data_dict[id]['midterm_grade_max'].append(midterm_max)
                data_dict[id]['midterm_grade_min'].append(midterm_min)
                data_dict[id]['grade_total'].append(grade_total)
            
        elif 'M1' in assignment_keys_list[0:i+1]:
            n_hw = 0
            for key in assignment_keys_list[0:i+1]:
                if "HW" in key:
                    n_hw +=1
            for id in id_list:
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = data_dict[id]['midterm_grades'][0]
                midterm_min = data_dict[id]['midterm_grades'][0]
                midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])
    
                grade_total = 0.2*hw_average + 0.35*midterm_max+0.15*midterm_min+0.3*midterm_average
    
                data_dict[id]['hw_grade_av'].append(hw_average)
                data_dict[id]['midterm_grade_max'].append(midterm_max)
                data_dict[id]['midterm_grade_min'].append(midterm_min)
                data_dict[id]['grade_total'].append(grade_total)
    
        elif 'HW1' in assignment_keys_list[0:i+1]:
            n_hw = 0
            for key in assignment_keys_list[0:i+1]:
                if "HW" in key:
                    n_hw +=1
            for id in id_list:
    # TODO: test if this really works
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
    #             midterm_max = max(data_dict[id]['midterm_grades'])
    #             midterm_min = min(data_dict[id]['midterm_grades'])
    #             midterm_average = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])
    
                grade_total = hw_average 
    
                data_dict[id]['hw_grade_av'].append(hw_average)
    #             data_dict[id]['midterm_grade_max'] = midterm_max
    #             data_dict[id]['midterm_grade_min'] = midterm_min
                data_dict[id]['grade_total'].append(grade_total)
        else:
            sys.exit("No grades given right now, so there is not much we can do.")



    print id_list 
    # test if this works
    for id in id_list:
        print str(id) + ' ' + str(data_dict[id]['grade_total'])


    
    # translate points into grades
    for id in id_list:
        data_dict[id]['letter_grade'] = []
        for j in xrange(n_assignment_keys):
            if round(data_dict[id]['grade_total'][j]) >= 96:
                data_dict[id]['letter_grade'].append('A')
            elif round(data_dict[id]['grade_total'][j]) >= 91:
                data_dict[id]['letter_grade'].append('A-')
            elif round(data_dict[id]['grade_total'][j]) >= 86:
                data_dict[id]['letter_grade'].append('B+')
            elif round(data_dict[id]['grade_total'][j]) >= 81:
                data_dict[id]['letter_grade'].append('B')
            elif round(data_dict[id]['grade_total'][j]) >= 76:
                data_dict[id]['letter_grade'].append('B-')
            elif round(data_dict[id]['grade_total'][j]) >= 71:
                data_dict[id]['letter_grade'].append('C+')
            elif round(data_dict[id]['grade_total'][j]) >= 66:
                data_dict[id]['letter_grade'].append('C')
            elif round(data_dict[id]['grade_total'][j]) >= 61:
                data_dict[id]['letter_grade'].append('C-')
            elif round(data_dict[id]['grade_total'][j]) >= 56:
                data_dict[id]['letter_grade'].append('D+')
            elif round(data_dict[id]['grade_total'][j]) >= 51:
                data_dict[id]['letter_grade'].append('D')
            else:
                data_dict[id]['letter_grade'].append('F')

    # test if this works
    for id in id_list:
        print str(id) + ' ' + str(data_dict[id]['grade_total'])+ ' ' + str(data_dict[id]['letter_grade'])

    sys.exit("This is as far as it goes right now.")
    # ok this is a mess by, now, so we should really clean up
    

    # course average
    grade_total_list = []
    grade_total_average_list = []
    grade_total_average_letter_list = []
    for j in xrange(n_assignment_keys):
        grade_total_list.append([])
        for id in id_list:
            grade_total_list[j].append(data_dict[id]['grade_total'])

        grade_total_average_list.append(sum(grade_total_list[j])/len(grade_total_list[j]))

        if round(grade_total_average) >= 96:
            grade_total_average_letter = 'A'
        elif round(grade_total_average) >= 91:
            grade_total_average_letter = 'A-'
        elif round(grade_total_average) >= 86:
            grade_total_average_letter = 'B+'
        elif round(grade_total_average) >= 81:
            grade_total_average_letter = 'B'
        elif round(grade_total_average) >= 76:
            grade_total_average_letter = 'B-'
        elif round(grade_total_average) >= 71:
            grade_total_average_letter = 'C+'
        elif round(grade_total_average) >= 66:
            grade_total_average_letter = 'C'
        elif round(grade_total_average) >= 61:
            grade_total_average_letter = 'C-'
        elif round(grade_total_average) >= 56:
            grade_total_average_letter = 'D+'
        elif round(grade_total_average) >= 51:
            grade_total_average_letter = 'D'
        else:
            grade_total_average_letter = 'F'

    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str

    print str(grade_total_average) + '  ' +  grade_total_average_letter
    
    
    # rank students
    # identify best, worst students
    # note: there is no good way to sort a nested dictionary by value, so we just create an auxillary dictionary
    tmp_list = []
    for id in id_list:
        tmp_tuple = (id,data_dict[id]['grade_total'])
        tmp_list.append(tmp_tuple)

    print tmp_list
    print 
    print 

    sorted_tmp_list = sorted(tmp_list, key=itemgetter(1))
    print sorted_tmp_list
    
    # count grades
    a0_count = 0
    am_count = 0
    bp_count = 0
    b0_count = 0
    bm_count = 0
    cp_count = 0
    c0_count = 0
    cm_count = 0
    dp_count = 0
    d0_count = 0
    f0_count = 0
    for id in id_list:
        if data_dict[id]['letter_grade'] == 'A': 
            a0_count +=1    
        elif data_dict[id]['letter_grade'] == 'A-': 
            am_count +=1    
        elif data_dict[id]['letter_grade'] == 'B+': 
            bp_count +=1    
        elif data_dict[id]['letter_grade'] == 'B': 
            b0_count +=1    
        elif data_dict[id]['letter_grade'] == 'B-': 
            bm_count +=1    
        elif data_dict[id]['letter_grade'] == 'C+': 
            cp_count +=1    
        elif data_dict[id]['letter_grade'] == 'C': 
            c0_count +=1    
        elif data_dict[id]['letter_grade'] == 'C-': 
            cm_count +=1    
        elif data_dict[id]['letter_grade'] == 'D+': 
            dp_count +=1    
        elif data_dict[id]['letter_grade'] == 'D': 
            d0_count +=1    
        elif data_dict[id]['letter_grade'] == 'F': 
            f0_count +=1    

    print 'a0_count   ' + str(a0_count)
    print 'am_count   ' + str(am_count)
    print 'bp_count   ' + str(bp_count)
    print 'b0_count   ' + str(b0_count)
    print 'bm_count   ' + str(bm_count)
    print 'cp_count   ' + str(cp_count)
    print 'c0_count   ' + str(c0_count)
    print 'cm_count   ' + str(cm_count)
    print 'dp_count   ' + str(dp_count)
    print 'd0_count   ' + str(d0_count)
    print 'f0_count   ' + str(f0_count)

    
    
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

    parser.add_option('--error_file', 
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
    