#!/usr/bin/env python

SCRIPT_NAME = "grademaster"
SCRIPT_VERSION = "v0.2.2"
REVISION_DATE = "2016-11-28"
AUTHOR = """
Johannes Hachmann (hachmann@buffalo.edu) with contributions by:
   Mojtaba Haghighatlari (jobfile, Pandas dataframe) 
"""
DESCRIPTION = "This little program is designed to help manage course grades, make grade projections, etc."

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
# v0.2.0  (2015-10-12): major overhaul introducing contributions from students; rename to grademaster; introduce jobfile; use of Pandas dataframes 
# v0.2.1  (2015-10-25): add requestmeeting; generalize for HW>5
# v0.2.2  (2016-11-28): generalize for >M2

###################################################################################################
# TASKS OF THIS SCRIPT:
# -assorted collection of tools for the analysis of grade data
###################################################################################################

import sys
import os
import time
import string
import math
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
from collections import defaultdict
from operator import itemgetter
from math import sqrt
from lib_jcode import (banner,
                       print_invoked_opts,
                       tot_exec_time_str,
                       intermed_exec_timing,
                       std_datetime_str,
                       chk_rmfile
                       )

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
     
###################################################################################################

def percent2lettergrade(percentgrade):
    """(percent2lettergrade):
        This function converts percentgrades into lettergrades according to a given conversion scheme.
    """
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

###################################################################################################

def distribution_stat(val_list):
    """(distribution_stat):
        Takes a list and returns some distribution statistics in form of a dictionary. 
    """
    n_vals = len(val_list)
    
    if n_vals == 0:
        stat = {'n': 0, 'av': None, 'median': None, 'min': None, 'max': None, 'mad': None, 'rmsd': None, 'spread': None}
    else:
	minimum = min(val_list)
	maximum = max(val_list)
        average = sp.average(val_list) 

        median = sp.median(val_list)

        spread = sp.ptp(val_list)

        mad = 0.0
        for val in val_list:
            mad += abs(val-average)
        mad = mad/n_vals

        rmsd = 0.0
        for val in val_list:
            rmsd += (val-average)**2
        rmsd = sqrt(rmsd/n_vals)

        stat = {'n': n_vals, 'av': average, 'median': median, 'min': minimum, 'max': maximum, 'mad': mad, 'rmsd': rmsd, 'spread': spread}
    print stat
    return stat

###################################################################################################

def histogram(val_list):
    """(histogram_dict):
        Takes a list and returns a dictionary with histogram data. 
    """
    dic = {}
    for x in val_list:
        if x in dic:
            dic[x] += 1
        else:
            dic[x] = 1
    print dic
    return dic


###################################################################################################

def print_df(dataframe): 

    pd.set_option('display.max_rows', len(dataframe))
    print(dataframe)
    pd.reset_option('display.max_rows')
    return 

###################################################################################################

def main(args,commline_list):
    """(main):
        Driver of the grademaster script.
    """
    time_start = time.time()

    # now the standard part of the script begins
    logfile = open(args.logfile,'a',0)
    error_file = open(args.error_file,'a',0)
    
    banner(logfile, SCRIPT_NAME, SCRIPT_VERSION, REVISION_DATE, AUTHOR, DESCRIPTION)

    # give out options of this run
    print_invoked_opts(logfile,args,commline_list)

    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')

    tmp_str = "Starting data acquisition..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    
    # check that file exists, get filename from optparse
    if args.data_file is None:
        tmp_str = "... data file not specified!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')

        tmp_str = "Aborting due to missing data file!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
# TODO: This should better be done by exception handling
        
    
    tmp_str = "   ...reading in data..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # open CSV file with raw data
    rawdata_df = pd.read_csv(opts.data_file)

    tmp_str = "   ...cleaning data structure..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # remove empty entries
    for i in rawdata_df.columns:
        if 'Unnamed'in i:
            rawdata_df = rawdata_df.drop(i,1)
    rawdata_df = rawdata_df.dropna(how='all')

    tmp_str = "   ...identify keys..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # read top line of data file, which defines the keys
    keys_list = list(rawdata_df.columns)   
    n_keys = len(keys_list)

    tmp_str = "   ...checking validity of data structure..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    if "Last name" not in keys_list[0:4]:
        tmp_str = "   ...'Last name' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to invalid data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    elif "First name" not in keys_list[0:4]:
        tmp_str = "   ...'First name' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to invalid data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    elif "Student ID" not in keys_list[0:4]:
        tmp_str = "   ...'Student ID' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to invalid data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)
    elif "email" not in keys_list[0:4]:
        tmp_str = "   ...'email' missing in data structure!"
        print tmp_str
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        tmp_str = "Aborting due to invalid data structure!"
        logfile.write(tmp_str + '\n')
        error_file.write(tmp_str + '\n')
        sys.exit(tmp_str)

    
    # check if all the grades are in float type (not object)
    for i in keys_list[4:]:
        if rawdata_df[i].dtypes == object:  
            tmp_str = "Aborting due to unknown grade format in column %s!" %i 
            logfile.write(tmp_str + '\n')
            error_file.write(tmp_str + '\n')
            sys.exit(tmp_str)  

    # some bookkeeping on where we stand in the semester
    n_hws = 0
    n_midterms = 0
    n_final = 0
    for key in keys_list[4:]:
        if "HW" in key:
            n_hws += 1
        elif "M" in key:
            n_midterms += 1  
        elif "Final" in key:
            n_final += 1
        else:                
            tmp_str = "Aborting due to unknown key!"
            logfile.write(tmp_str + '\n')
            error_file.write(tmp_str + '\n')
            sys.exit(tmp_str)
 
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
    
    tmp_str = "   Number of students:  " + str(len(rawdata_df))
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of homeworks: " + str(n_hws)
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of midterms:  " + str(n_midterms)
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "   Number of finals:    " + str(n_final)
    print tmp_str
    logfile.write(tmp_str + '\n')

    #################################################################################################


    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "Starting calculation of grades and grade projections..."
    print tmp_str
    logfile.write(tmp_str + '\n')

    # Set up projection dataframe   
    hwdata_df = rawdata_df.copy()
    examdata_df = rawdata_df.copy()
    # empty all data fields in projection_df
    for i in xrange(4,n_keys):
        key = keys_list[i]
        if 'HW' in key[0:2]:
            examdata_df.drop(key, axis=1, inplace=True)
        elif key in ('M1', 'M2','Final'):
            hwdata_df.drop(key, axis=1, inplace=True)
            
    hwkeys_list = list(hwdata_df.columns)   
    n_hwkeys = len(hwkeys_list)  

    examkeys_list = list(examdata_df.columns)   
    n_examkeys = len(examkeys_list)  

    acc_hwdata_df = hwdata_df.copy()
    acc_examdata_df = examdata_df.copy()
    
    for i in xrange(4,n_hwkeys):
        key = hwkeys_list[i]
        if key == 'HW1':
            continue
        else:
            prevkey = hwkeys_list[i-1]            
            acc_hwdata_df[key] += acc_hwdata_df[prevkey]

    for i in xrange(4,n_examkeys):
        key = examkeys_list[i]
        if key == 'M1':
            continue
        else:
            prevkey = examkeys_list[i-1]            
            acc_examdata_df[key] += acc_examdata_df[prevkey]          # this is used to get the cumulative grades 

    av_hwdata_df = acc_hwdata_df.copy()
    av_examdata_df = acc_examdata_df.copy()
    minmax_midtermdata_df = examdata_df.copy()

    for i in xrange(4,n_hwkeys):
        key = hwkeys_list[i]
        hw_n = int(key[2:])
        av_hwdata_df[key] = 1.0*av_hwdata_df[key]/hw_n

    for i in xrange(4,n_examkeys):
        key = examkeys_list[i]
        if key == 'Final':
            av_examdata_df[key] = 1.0*av_examdata_df[key]/3            
        else:
            exam_n = int(key[1:])
            av_examdata_df[key] = 1.0*av_examdata_df[key]/exam_n      # getting the averages after each assignment/exam. 
    projection_df = rawdata_df.copy()
    for i in xrange(4,n_keys):
        key = keys_list[i]
        projection_df[key] = 0
        if key in ('HW1','HW2','HW3','HW4'):
            projection_df[key] = av_hwdata_df[key]
        elif key == 'M1':
            projection_df[key] = 0.2*av_hwdata_df['HW4']+0.8*av_examdata_df['M1']
        elif key in ('HW5', 'HW6','HW7','HW8'):
            projection_df[key] = 0.2*av_hwdata_df[key]+0.8*av_examdata_df['M1']
        elif key == 'M2':
            projection_df[key] = 0.2*av_hwdata_df['HW8']+0.8*av_examdata_df['M2']
        elif key in ('HW9', 'HW10'):
            projection_df[key] = 0.2*av_hwdata_df['HW10']+0.8*av_examdata_df['M2']
        elif key == 'Final':
             projection_df[key] = 0.2*av_hwdata_df['HW10']+0.2*av_examdata_df['M1']+0.2*av_examdata_df['M2']+0.3*av_examdata_df['Final']
    
    print "\n\nThese are the grade projections as of now\n\n" , projection_df
    
    print "\n\n\nSending individual mails to all the students... \n\n"
    
    email_id = raw_input("\n Please enter the Buffalo email id with which you want to send the mails: \n")
    password = raw_input("\n Please enter the password for the given email id: \n")
    
    for index in rawdata_df.index:
        if index > 5:
            break
        tmp_str = rawdata_df.loc[index, 'email']
        update_n = n_hws + n_midterms + n_final 
        tmp_str += "\n Grade summary and projection for CE 317 (#" + str(update_n) + ")" 

        firstname = rawdata_df.loc[index, 'First name'].split()[0]
        if firstname == ".":
            firstname = rawdata_df.loc[index, 'Last name'].split()[0]
        
        tmp_str += "\n Dear " + firstname + ","
        
        tmp_str += "\n \n I'm writing to give you a brief update on where you stand in CE 317. Here are the marks I have on record for you so far: \n" 

        for i in xrange(4,n_keys):
            key = keys_list[i]
            tmp_str += key + ": " 
            if len(key) == 2:
                tmp_str += " " 
            tmp_str += "\n \n %5.1f " %(rawdata_df.iloc[index, i])

        tmp_str += "\n In the following you can find the class statistics for each assignment/exam:" 
 
        pd.options.display.float_format = '{:7.2f}'.format
        tmp_str += "\n" + str(rawdata_df.loc[:,'HW1':].describe())

        tmp_str += "\n Based on your assignment marks, I arrived at the following grade projections: \n" 

        for i in xrange(4,n_keys):
            key = keys_list[i]
            tmp_str += "\n Grade projection after " + key + ": " +"\n"
            if len(key) == 2:
                tmp_str += " " 
            tmp_str += " %5.1f " %(projection_df.iloc[index, i])
            tmp_str += "(" + percent2lettergrade(projection_df.iloc[index, i]) + ")" + "\n"
    
        if percent2lettergrade(projection_df.iloc[index, i]) == 'A':
            tmp_str += "Well done - excellent job, " + firstname + "! Keep up the good work! \n"  

        tmp_str += "\n\n Note: These grade projections are based on default 5-point lettergrade brackets as well as the weights for exams and homeworks indicated in the course syllabus. " 
        tmp_str += "\n Your prior homework and exam averages are used as placeholders for the missing homeworks and exams, respectively. \n" 
        tmp_str += "They do NOT yet incorporate extra credit for in-class participation, nor do they consider potential adjustments to the grade brackets. \n"
        tmp_str += "I'm providing the grades after each assignment to give you an idea about your progress. "
        tmp_str += "It is worth noting that grades tend to pick up after the first midterm.\n"
        tmp_str += "Please let me know if you have any questions or concerns."

        if args.requestmeeting is True:
            if projection_df.iloc[index, i] < 66:
                tmp_str = "\n \n" + firstname + ", since you are current not doing so great, I wanted to offer to have a meeting with you to see what we can do to improve things. Please let me know what you think."   

        tmp_str += "\n\n Best wishes,"

        tmp_str += "\n JH"
        tmp_str += "\n ------------------------------------------------------------------------------ "
        
	fromaddress = str(email_id)
	toaddress = rawdata_df.loc[index , 'email']
        msg = MIMEMultipart()
	msg['From'] = fromaddress
	msg['To'] = toaddress
	msg['Subject'] = "Grade summary and projections"
	body = tmp_str
	msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.buffalo.edu', 25)
        server.starttls()
        server.login(str(email_id), str(password))
        text = msg.as_string()
	server.sendmail(str(email_id), rawdata_df.loc[index, 'email'], text)
    server.quit() 

    tmp_str = "...calculation of grades and grade projections finished."
    print tmp_str
    logfile.write(tmp_str + '\n')


#################################################################################################


    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "\n\nStarting calculation of course statistics...\n"
    print tmp_str
    logfile.write(tmp_str + '\n')
    dist_stat = distribution_stat(projection_df[keys_list[-1]].values.tolist())
    print "\n\nHistogram for the data\n\n" 
    histogram_data = histogram(projection_df[keys_list[-1]].values.tolist())
    plt.hist(projection_df[keys_list[-1]].values.tolist())
    plt.title('Histogram')
    plt.xlabel('Marks')
    plt.ylabel('Number of students')
    plt.savefig('histogram') 
    tmp_str = "\n\n\n...computing letter grade distribution..."
    print tmp_str
    logfile.write(tmp_str + '\n')
    tmp_str = "------------------------------------------------------------------------------ "
    print tmp_str
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
        
    return 0    #successful termination of program"""
    
#################################################################################################

# TODO: replace with argpass 
if __name__=="__main__":
    usage_str = "usage: %prog [options] arg"
    version_str = "%prog " + SCRIPT_VERSION
    parser = argparse.ArgumentParser(usage=usage_str, version=version_str)    
    
    parser.add_argument('--data_file', 
                      dest='data_file', 
                      type=str, 
                      help="specifies the name of the raw data file in CSV format")

    parser.add_argument('--job_file', 
                      dest='job_file', 
                      type=str, 
                      help='specifies the name of the job file that specifies sets ')
# TODO: need to write a parser for the jobfile

    parser.add_argument('--requestmeeting', 
                      dest='requestmeeting', 
                      action='store_true', 
                      default=False, 
                      help='specifies the a meeting is requested in the student email')


    # Generic options 
    parser.add_argument('--print_level', 
                      dest='print_level', 
                      type=int, 
                      default=2, 
                      help='specifies the print level for on screen and the logfile [default: %default]')
        
    # specify log files 
    parser.add_argument('--logfile', 
                      dest='logfile', 
                      type=str, 
                      default='grademaster.log',  
                      help='specifies the name of the log-file [default: %default]')

    parser.add_argument('--error_file', 
                      dest='error_file', 
                      type=str, 
                      default='grademaster.err',  
                      help='specifies the name of the error-file [default: %default]')

    opts = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 2:
        sys.exit("You tried to run grademaster without options.")
    main(opts,sys.argv)
    
else:
    sys.exit("Sorry, must run as driver...")
