#!/usr/bin/env python

SCRIPT_NAME = "grade_master"
SCRIPT_VERSION = "v0.1.16"
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
# v0.1.13 (2015-03-09): continue cleanup and rewrite beyond data acquisition 
# v0.1.14 (2015-03-09): continue cleanup and rewrite beyond grade calculation; make letter grade conversion into function 
# v0.1.15 (2015-03-09): continue cleanup and rewrite beyond letter grade conversion; introduce custom statistics function 
# v0.1.16 (2015-03-09): continue cleanup and rewrite beyond grade statistics 

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

from math import sqrt
# import numpy as np

from lib_jcode import (banner,
                       print_invoked_opts,
                       tot_exec_time_str,
                       intermed_exec_timing,
                       std_datetime_str,
                       chk_rmfile
                       )
     

###################################################################################################

def percent2lettergrade(percentgrade):
    """(percent2lettergrade):
        This function converts percentgrades into lettergrades according to a given conversion scheme.
    """
# TODO: this is the place to realize different grading-schemes in a more general fashion
    if round(percentgrade) >= 96:
        return 'A'
    elif round(percentgrade) >= 91:
        return 'A-'
    elif round(percentgrade) >= 86:
        return 'B+'
    elif round(percentgrade) >= 81:
        return 'B'
    elif round(percentgrade) >= 76:
        return 'B-'
    elif round(percentgrade) >= 71:
        return 'C+'
    elif round(percentgrade) >= 66:
        return 'C'
    elif round(percentgrade) >= 61:
        return 'C-'
    elif round(percentgrade) >= 56:
        return 'D+'
    elif round(percentgrade) >= 51:
        return 'D'
    else:
        return 'F'


# TODO: we should really use a library/module for this rather than coding it by hand (this is just for exercise)
def median_func(val_list):
    """(median function):
        Takes a list of values and returns the median. 
    """
    val_list = sorted(val_list)
    # different cases
    # empty list
    if len(val_list) < 1:
        return None
    # list with odd numbers of values
    if len(val_list) %2 == 1:   
        return val_list[((len(val_list)+1)/2)-1]
    # list with even numbers of values
    if len(val_list) %2 == 0:
        return float(sum(val_list[(len(val_list)/2)-1:(len(val_list)/2)+1]))/2.0


def distribution_stat(val_list):
    """(distribution_stat):
        Takes a list and returns some distribution statistics in form of a dictionary. 
    """
    n_vals = len(val_list)
    
    if n_vals == 0:
        stat = {'n': 0, 'av': None, 'median': None, 'min': None, 'max': None, 'mad': None, 'rmsd': None, 'spread': None}
    else:
        average = 0.0
        for val in val_list:
            average += val
        average = average/n_vals 

        median = median_func(val_list)

        val_list.sort()
        min = val_list[0]
        max = val_list[-1]
        spread = abs(max - min)

        mad = 0.0
        for val in val_list:
            mad += abs(val-average)
        mad = mad/n_vals

        rmsd = 0.0
        for val in val_list:
            rmsd += (val-average)**2
        rmsd = sqrt(rmsd/n_vals)

        stat = {'n': n_vals, 'av': average, 'median': median, 'min': min, 'max': max, 'mad': mad, 'rmsd': rmsd, 'spread': spread}
    return stat


def histogram(val_list):
    """(histogram_dict):
        Takes a list and returns a dictionary with histogram data. 
    """
    dict = {}
    for x in val_list:
        if x in dict:
            dict[x] += 1
        else:
            dict[x] = 1
    return dict


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
                tmp_str = "Aborting due to unknown key!"
                logfile.write(tmp_str + '\n')
                error_file.write(tmp_str + '\n')
                sys.exit(tmp_str)

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
    tmp_str = "Starting calculation of grades and grade projections..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    

    # create lists of various grades
    for id in id_list:
        data_dict[id]['hw_grade_av'] = []
        data_dict[id]['overall_grade'] = []
        data_dict[id]['overall_lettergrade'] = []


    # create assignment keys list for better readability; introduce assignment keys list; note: we trade resources for readability 
    assignment_keys_list = keys_list[3:]
    n_assignment_keys = len(assignment_keys_list)

    
    # we want grades for every point during the semester, so we successively go through list of assignments and compute grade after each     
    for i in xrange(n_assignment_keys):        
        # determine number of homeworks at any point in semester
        n_hw = 0
        for key in assignment_keys_list[0:i+1]:
            if "HW" in key: n_hw +=1        
        for id in id_list:
        # distinguish different cases for grade projections, depending on where we stand in the semester
            if 'Final' in assignment_keys_list[0:i+1]:  # i.e., this is the final grade after all assignments are in 
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = max(data_dict[id]['midterm_grades'])
                midterm_min = min(data_dict[id]['midterm_grades'])
                final = data_dict[id]['final_grade']    # this is really for readability    
            elif 'M2' in assignment_keys_list[0:i+1]:
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = max(data_dict[id]['midterm_grades'])
                midterm_min = min(data_dict[id]['midterm_grades'])
                final = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])
            elif 'M1' in assignment_keys_list[0:i+1]:
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = max(data_dict[id]['midterm_grades'])
                midterm_min = min(data_dict[id]['midterm_grades'])
                final = sum(data_dict[id]['midterm_grades'])/len(data_dict[id]['midterm_grades'])    
            elif 'HW1' in assignment_keys_list[0:i+1]:
                hw_average = sum(data_dict[id]['hw_grades'][0:n_hw])/len(data_dict[id]['hw_grades'][0:n_hw])
                midterm_max = hw_average
                midterm_min = hw_average
                final = hw_average
            else:
                tmp_str = "Aborting due to lack of reported grades!"
                logfile.write(tmp_str + '\n')
                error_file.write(tmp_str + '\n')
                sys.exit(tmp_str)
                
            # implement grading scheme: HW: 20%, better midterm 35%, worse midterm 15%, final: 30%
            overall_grade = 0.2*hw_average + 0.35*midterm_max + 0.15*midterm_min + 0.3*final
# TODO: instead of hardwiring, we may want to build more flexibility in here 
            
            overall_lettergrade = percent2lettergrade(overall_grade)

            # add computed information to data dictionary
            data_dict[id]['hw_grade_av'].append(hw_average)
# TODO: we should take out the rounding here
            data_dict[id]['overall_grade'].append(round(overall_grade,1))
            data_dict[id]['overall_lettergrade'].append(overall_lettergrade)


#     # output for testing
#     for id in id_list:
#         print str(id) + ' ' + str(data_dict[id]['overall_grade'])+ ' ' + str(data_dict[id]['overall_lettergrade'])

    tmp_str = "...calculation of grades and grade projections finished."
    print tmp_str
    logfile.write(tmp_str + '\n')


    #################################################################################################


    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "Starting calculation of course statistics..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    
#     tmp_str = "   ...computing basic distribution statistics..."
#     print tmp_str
#     logfile.write(tmp_str + '\n')

    # create lists of lists with all the overall grades
    course_overall_grade_list = []
    course_overall_lettergrade_list = []
    course_overall_grade_stat_list = []

    # iterate through all assignments
    for j in xrange(n_assignment_keys):
        course_overall_grade_list.append([])
        course_overall_lettergrade_list.append([])
        for id in id_list:
            course_overall_grade_list[j].append(data_dict[id]['overall_grade'][j])
            course_overall_lettergrade_list[j].append(data_dict[id]['overall_lettergrade'][j])
            

        stat = distribution_stat(course_overall_grade_list[j])
        course_overall_grade_stat_list.append(stat)

        course_overall_grade_stat_list[j]['letter_av'] = percent2lettergrade(course_overall_grade_stat_list[j]['av'])
        course_overall_grade_stat_list[j]['letter_median'] = percent2lettergrade(course_overall_grade_stat_list[j]['median'])
        course_overall_grade_stat_list[j]['letter_min'] = percent2lettergrade(course_overall_grade_stat_list[j]['min'])
        course_overall_grade_stat_list[j]['letter_max'] = percent2lettergrade(course_overall_grade_stat_list[j]['max'])
                
        course_overall_grade_stat_list[j]['letter_dist'] = histogram(course_overall_lettergrade_list[j])

        print course_overall_grade_stat_list[j]
        print 
        sys.exit("This is as far as it goes right now.")


    tmp_str = "   ...computing letter grade distribution..."
    print tmp_str
    logfile.write(tmp_str + '\n')


    


# perform statistics, analysis, projections
# compute current average according to grading rules 
# rank students
# identify best, worst students
# compile info for each student
# visualize trends
# add course participation into grading scheme

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
    