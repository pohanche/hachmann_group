import sys
import os
import time
import string
import math
# import shutil
import scipy as sp
import numpy as np
import pandas as pd

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

def main(opts,commline_list):
    logfile = open(opts.logfile,'a',0)
    error_file = open(opts.error_file,'a',0)

    tmp_str = "------------------------------------------------------------------------------ "
    print(tmp_str)
    logfile.write(tmp_str + '\n')

if __name__ == "__main__":
    usage_str = "usage: %prog [options] arg"
    version_str = "%prog " + SCRIPT_VERSION
    parser = OptionParser(usage=usage_str, version=version_str)

    parser.add_option('--data_file',
                      dest='data_file',
                      type='string',
                      help='specifies the name of the raw data file in CSV format')

    parser.add_option('--job_file',
                      dest='job_file',
                      type='string',
                      help='specifies the name of the job file that specifies sets ')
    # TODO: need to write a parser for the jobfile

    parser.add_option('--requestmeeting',
                      dest='requestmeeting',
                      action='store_true',
                      default=False,
                      help='specifies the a meeting is requested in the student email')

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
                      default='grademaster.log',
                      help='specifies the name of the log-file [default: %default]')

    parser.add_option('--error_file',
                      dest='error_file',
                      type='string',
                      default='grademaster.err',
                      help='specifies the name of the error-file [default: %default]')

    opts, args = parser.parse_args(sys.argv[1:])
    if len(sys.argv) < 2:
        sys.exit("You tried to run grademaster without options.")
    main(opts, sys.argv)

else:
    sys.exit("Sorry, must run as driver...")
