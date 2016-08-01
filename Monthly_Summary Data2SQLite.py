# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:17:21 2016

@author: owner
"""

'''Read in and then write the monthly sunnaries back to their files. 
Trap the FileNotFoundErrors and write info to screen and to a file.'''

import re
#import pandas
#import sqlite
#import datetime
#import pytz

logfilepath = "C:\\Weather - Palmer\\MonthlySummary\\logfile.txt"
log = open(logfilepath, 'w')

filepath = "C:\\Weather - Palmer\\MonthlySummary\\%s\\"



filename = 'WX%s%s.PRN'
monthlist = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

for year in range(2002,2003, 1):
    
    for month in monthlist:
                    
        print('Year:', year, '\tmonth: ', month, end = '')
        print('Year:', year, '\tmonth: ', month, end = '', file=log)
        
        try:
            fin = open((filepath + filename) % (year, year, month))
        except FileNotFoundError:
            print("\t\tFILENOTFOUND!")
            print("\t\tFILENOTFOUND!", file=log)
        else:
            
            fin = open((filepath + filename) % (year, year, month), 'r')
            filestr = fin.read()
        #    filestr = filestr.replace('\n\n', '\n')
            fin.close()
            fout = open((filepath + filename) % (year, year, month), 'w')
            fout.write(filestr)
            fout.close()
            print('\t\tDONE')
            print('\t\tDONE', file=log)
        
log.close()            
        