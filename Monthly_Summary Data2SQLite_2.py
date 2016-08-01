# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:17:21 2016

@author: owner
"""

'''This script reads in the files from 1989 to 2003 and then looks for the
number of groups in each line. The groups are defined by the regular
expression: 
r'([0-9]{5})|([0-9/]{5})|(\d+\.\d*)|(\d+)|(\w+)'

This should return 16-17 groups in the data section of the files. When
I ran the script in the files I found that most returned line 50 as the 
one to start importing at. However, some returned 49 or 51, 52. I looked at 
those files, and there was a strange 'extra' line feed or newline for each of 
the data rows, and also on line '=====Daily Weather Data==='. I looked at the
original data files and the extra newline was not there. This seemed to be 
a problem in 2002 and 2003. I jst copied the original files into those
directories, and re-ran the script. It was fine then. I did NOT do the
'pre-reading' - i.i read the file in and then write it back. I tried it and 
this did not cause the extra newline anyways. This problem is still a mystery.

Aha! I just looked at the AMRC site, and these files 2002 jly, Aug, Oct, Nov
have this isue on their site. The extra newlines were generated at AMRC and 
not by the RA. This also happened for some months in 2003.
'''

import re
#import pandas
#import sqlite3
#import datetime
#import pytz

logfilepath = "C:\\Weather - Palmer\\MonthlySummary\\logfile.txt"
log = open(logfilepath, 'w')

filepath = "C:\\Weather - Palmer\\MonthlySummary\\%s\\"



filename = 'WX%s%s.PRN'
monthlist = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

for year in range(2003,2004, 1):
    
    for month in monthlist:
                    
        print('Year:', year, '\tmonth: ', month, end = '')
        print('Year:', year, '\tmonth: ', month, end = '', file=log)
        
        try:
            fin = open((filepath + filename) % (year, year, month))
        except FileNotFoundError:
            print("\t\tFILENOTFOUND!")
            print("\t\tFILENOTFOUND!", file=log)
        else:
            i = 0
            flag = 0
            for line in fin:
            #    print(i, '\t', line)
                groups = len(re.findall(\
                r'([0-9]{5})|([0-9/]{5})|(\d+\.\d*)|(\d+)|(\w+)', line))
            #    print('GROUPS = ', groups)
                if (groups >= 15) and (flag == 0):
                    print('\tstart import here = ', i)
                    print('\tstart import here = ', i, file = log)
                    flag = 1
                i += 1
            fin.close()
        
log.close()            
        