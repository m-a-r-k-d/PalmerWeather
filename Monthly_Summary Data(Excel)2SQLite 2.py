# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 12:38:03 2016

@author: Mark D

This program reads the Monthly Summary Excel files, manipulates the data
into the proper form and then writes it to an SQLite db.

It was written to read in the data from 2013-2015. During this period, the 
SST data was listed in a separate column from the SeaIce data. 

It's easier to use the Excel files than it is to use the ASCII files. There
are more errors in the ASCII files that are difficult to program around.

"""

import pandas as pd
import numpy as np
import sqlite3

filepath = "C:\\Weather - Palmer\\MonthlySummary\\{0}\\"

#year = 2011
#month = 10
#filename = 'WX201108.xls'

filename = "WX{0}{1:02d}.xls"
yeararr = np.arange(2015,2016,1)
montharr = np.arange(7,9,1)

colnum = 16

dbpath = 'C:\\Weather - Palmer\\MonthlySummary\\'
dbfile = 'MonthlySummary_db.sqlite'
dbtable = 'Summary2003_2015'

#These are the columns in the data file. Sometime in 2004-2005 Sky_Coverage
#stopped being recorded, but it's still included so that all the data from
#2003-2015 can go into the same table.
columns2015 = ['Day', 'Temp_High', 'Temp_Low', 'Temp_Avg', \
    'P_High', 'P_Low', 'P_Avg', \
    'Wind_5sec_Peak', 'Wind_2min_Peak', 'Wind_2min_Peak_Dir', \
    'Wind_Avg', 'Wind_Prev_Dir', \
    'Precip_Melted', 'Precip_Snow', 'Depth_SnowStake', \
    'Sky_Coverage', 'SST', 'SeaIce']
    
for year in yeararr:
    
    for month in montharr:
        
        print('Year:', year, '\x20month: ', month, end = '')        
        
        #The 16th column (labeled 15) is the SST/SeaIce column. It should be imported
        #as a string. This is what the 'converters' argument does.
        MonthData = pd.read_excel(\
            filepath.format(year)+filename.format(year,month), \
            header = None, skiprows = 5, skipfooter = 12, \
            converters = {colnum:str})
            
        #The dataframe, as imported from Excel, has two Day columns one is the first
        # column and one is the last - column label = 16. Drop that last column:
        MonthData = MonthData.drop(colnum + 1,1)
#        
#        #Now, convert the combined SST/SeaIce column into two:
#        SSTseries = pd.Series(data=np.zeros(MonthData.shape[0]), dtype = object)
#        SeaIceseries = pd.Series(data=np.zeros(MonthData.shape[0]), dtype = object)
#        
#        #Create a series of Booleans that indicate if the entry in column 15 is NaN
#        #The NaN values should not (cannot!) be converted to SST and SeaIce. These
#        #only occur in some of the data files.
#        SST_SeaIce_Bool = MonthData.iloc[:,colnum].notnull()
#        
#        for i, boolean in enumerate(SST_SeaIce_Bool):
#            if boolean:
#        #Now, convert the SST value to a number. The SST data is 
#        #in this form:
#        # ssnnn where ss indicates the sign, 00 is positive, 01 is negative
#        #             nnn is the value in tenths
#        
#                SSTseries[i] = MonthData.iloc[i,colnum][:5]
#                if SSTseries[i][:2] == '01':
#                    SSTseries[i] = -1*int(SSTseries[i][2:])/10
#                elif SSTseries[i][:2] == '00':
#                    SSTseries[i] = int(SSTseries[i][2:])/10
#                else:
#                    SSTseries[i] = np.nan                    
#                SeaIceseries[i] = MonthData.iloc[i,colnum][5:]                   
#            else:
#                SSTseries[i] = np.nan    
#                SeaIceseries[i] = np.nan
#        
#        #Insert two columns, one for SST data and one for Sky_Coverage
#        MonthData.insert(colnum, 'Sky_Coverage', np.nan)
#        MonthData.insert(colnum + 1, 'SST', np.nan)
#        
#        MonthData.columns = columns2015
#        
#        MonthData['SST'] = SSTseries
#        MonthData['SeaIce'] = SeaIceseries
        
        MonthData.insert(colnum-1, 'Sky_Coverage', np.nan)
        MonthData.columns = columns2015
        MonthData['SST'] = MonthData['SST'].astype(float)
        
        #Remove the 'T' in Precip columns that was used indicate trace amounts.
        #This was stopped sometime in the 2000's anyways. At that point, the RA
        #started reporting trace amounts as zero
        if MonthData['Precip_Melted'].dtype == 'object':
            MonthData['Precip_Melted'] = MonthData['Precip_Melted'].replace('T', value='0.0')
            MonthData['Precip_Melted'] = MonthData['Precip_Melted'].astype('float')
        if MonthData['Precip_Snow'].dtype == 'object':    
            MonthData['Precip_Snow'] = MonthData['Precip_Snow'].replace('T', value='0')
            MonthData['Precip_Snow'] = MonthData['Precip_Snow'].astype('float')
        
        #Make columns for the month and the year
        MonthData.insert(0, 'Month', month)
        MonthData.insert(0, 'Year', year)
        
        #Make a Date column that will a string indicating yyyy-mm-dd            
        #I don't like the use of the for loop to get this done.
        
        DaysInMonth = MonthData.shape[0]
        Dateseries = pd.Series(np.zeros(DaysInMonth), dtype = object)
        
        for i, day in enumerate(MonthData['Day']):
            Dateseries[i] = "{0}-{1:02d}-{2:02d}".format(year,month,day)
            
        MonthData.insert(0,'Date', Dateseries)
        
        #Make a new column that is the "Date' column converted to POSIX time 
        #(i.e. unix time- number of seconds from 1970 Jan1, utc 00:00 to date.
        #First, create the column called 'Timestamp', and fill it with datetime values
        #derived from the 'Date' column
        MonthData.insert(1,'Timestamp', \
            pd.to_datetime(MonthData['Date'], utc = True, yearfirst = True))
        #Now, convert those time stamps to np.int64. This gives the number of 
        #nanoseconds from Jan 1 1970 00:00, so divide by 10**9
        MonthData['Timestamp'] = MonthData['Timestamp'].astype(np.int64)//10**9
        
        print('\tDF Done.', end = '')        
        
        conn = sqlite3.connect(dbpath + dbfile)
        MonthData.to_sql(dbtable, conn, flavor = 'sqlite', \
            if_exists = 'append', index = False)
        conn.close()
        print('\tDB Done.')