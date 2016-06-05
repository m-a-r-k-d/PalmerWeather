# -*- coding: utf-8 -*-
"""
Created on Thu May 26 15:17:21 2016

@author: owner
"""

'''
This program is used to enter the monthly summary data from 1989 to 2003
into an SQLite database. It prints output to the screen and also to a log 
file. The database file is called "MonthlySummary_db.sqlite". The table
for this data is Summary1989_2003. 

This was the time period that the RA created the summary using analog 
instruments- i.e. no automatic weather station. All data collected using 
chart recorders, etc.

The program first reads the file in and determines what line to start
the import. It handles the exception if the file does not exist. The file 
is read line by line and a regular expression scans the line and determines
the number of groups found. This is looking for the start of the columns
of data. 

Next, the file is read in using the read_csv function of pandas starting
at the row found previously. Once the data is in a dataframe, it is 
manipulated and put into the proper form.
'''

import re
import pandas as pd
import numpy as np
import sqlite3

#import sqlite3
#import datetime
#import pytz

logfilepath = 'C:\\Weather - Palmer\\MonthlySummary\\logfile.txt'
log = open(logfilepath, 'w')

dbpath = 'C:\\Weather - Palmer\\MonthlySummary\\'
dbfile = 'MonthlySummary_db.sqlite'

filepath = "C:\\Weather - Palmer\\MonthlySummary\\%s\\"

#These column names must match the names used in the SQLite db.
columns2003 = ['Day', 'Temp_High', 'Temp_Low', 'Temp_Avg', \
    'P_High', 'P_Low', 'P_Avg', 'Wind_Peak', \
    'Wind_Peak_Dir', 'Wind_Avg', 'Wind_Prev_Dir', \
    'Precip_Melted', 'Precip_Snow', 'Depth_SnowStake', \
    'Sky_Coverage', 'SST', 'SeaIce']

filename = 'WX%s%s.PRN'

monthlist = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

for year in range(1989,2004, 1):
    
    for month in monthlist:
                    
        print('Year:', year, '\x20month: ', month, end = '')
        print('Year:', year, '\x20month: ', month, end = '', file=log)
        
        try:
            fin = open((filepath + filename) % (year, year, month), 'r')
        except FileNotFoundError:
            print("\t\tFILENOTFOUND!")
            print("\t\tFILENOTFOUND!", file=log)
        else:
#The for loop below finds the line to start the import at. It looks for
#groups of data. If there are 15 or more groups on the line, it indicates
#that it's a data line. In the summary files, the lines in the header
#have less than 15 groups.
            i = 0
            flag = 0
            for line in fin:
            #    print(i, '\t', line)
                groups = len(re.findall(\
                r'([0-9]{5})|([0-9/]{5})|(\d+\.\d*)|(\d+)|(\w+)', line))
            #    print('GROUPS = ', groups)
                if (groups >= 15) and (flag == 0):
                    startrow = i
                    print('\x20import @ ', startrow, end = '')
                    print('\x20import @ ', startrow, end = '', file = log)
                    flag = 1
                    break
                i += 1
            fin.close()
            
#Read the file into a dataframe            
            MonthData = pd.read_csv((filepath + filename) % (year, year, month), \
                sep = '\s+', skiprows = startrow, header = None, \
                dtype = {15:object})

#Insert a new column for the SST data
            MonthData.insert(15, '', value = '')
                    
#Create two series that will be used to hold SST and SeaIce data
            SSTseries = pd.Series(data=np.zeros(MonthData.shape[0]), dtype = object)
            SeaIceseries = pd.Series(data=np.zeros(MonthData.shape[0]), dtype = object)
#Create a series of Booleans that indicate it the entry in column 15 is NaN
            #The NaN values should not be converted to SST and SeaIce
            SST_SeaIce_Bool = MonthData.iloc[:,16].notnull()

#Loopover the Boolean series. Those values that are 'notnull' will be put into
# SSTseries and SeaIceseries
            for i, boolean in enumerate(SST_SeaIce_Bool):
                if boolean:
            #Now, convert the SST value to a number. The SST data is 
            #in this form:
            # ssnnn where ss indicates the sign, 00 is positive, 01 is negative
            #             nnn is the value in tenths

                    SSTseries[i] = MonthData.iloc[i,16][:5]
                    if SSTseries[i][:2] == '01':
                        SSTseries[i] = -1*int(SSTseries[i][2:])/10
                    elif SSTseries[i][:2] == '00':
                        SSTseries[i] = int(SSTseries[i][2:])/10
                    else:
                        SSTseries[i] = np.nan                    
                    SeaIceseries[i] = MonthData.iloc[i,16][5:]                   
                else:
                    SSTseries[i] = np.nan    
                    SeaIceseries[i] = np.nan

#Name the columns in the data frame using the column list defined above.
            MonthData.columns = columns2003
            
            MonthData['SeaIce'] = SeaIceseries            
            MonthData['SST'] = SSTseries
            MonthData['SST'] = MonthData['SST'].astype(float)
                        
#Remove the 'T' in Precip columns that was used indicate trace amounts.
#This was stopped someplace in the 2000's anyways. At that point, the RA
                        #started reporting trace amounts as zero
            MonthData['Precip_Melted'] = MonthData['Precip_Melted'].replace('T', value='0.0')
            MonthData['Precip_Snow'] = MonthData['Precip_Snow'].replace('T', value='0')

#Change the data types to float and integer           
            MonthData['Precip_Melted'] = MonthData['Precip_Melted'].astype(float)
            MonthData['Precip_Snow'] = MonthData['Precip_Snow'].astype(float)

            MonthData.insert(0, 'Month', int(month))
            MonthData.insert(0, 'Year', year)

#Make a Date column that will a string indicating yyyy-mm-dd            
            MonthData.insert(0, 'Date', \
                str(year)+'-'+month+'-'+MonthData['Day'].astype(str))
            
            MonthData.insert(1,'Timestamp', \
                pd.to_datetime(MonthData['Date'], utc = True, yearfirst = True))
            MonthData['Timestamp'] = \
                pd.DatetimeIndex(MonthData['Timestamp']).astype(np.int64)//10**9
            
            print('\tDF Done.', end = '')
            print('\tDF Done.', end = '', file=log)
#Now, write to the table in the sqlite database!!!
            
            conn = sqlite3.connect(dbpath + dbfile)
            MonthData.to_sql('Summary1989_2003', conn, flavor = 'sqlite', \
                if_exists = 'append', index = False)
            conn.close()
            print('\tDB Done.')
            print('\tDB Done.', file = log)
            
log.close()            
        