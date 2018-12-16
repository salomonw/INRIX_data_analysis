# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 20:49:51 2018

@author: Salomon Wollenstein
"""


# Import libraries
import os 
os.chdir('G:/My Drive/Github/INRIX_vis/main')
from utils import *
execfile('parameters.py')
execfile('functions.py')

import geopandas

## Preprocessing - calculate percentiles by looking at at smaller files
# creating a new dir
if os.path.isdir(outDir) == False:
    os.mkdir(outDir)
    os.mkdir(dirFilteredData)

# importing network and tmc's
import_network(filesID, outDir, dirFilteredData, 'all' , [])

# unzip 2012 data
unzip_2012_data(outDir, dirData_l, dirFilteredData)

# compute percentiles for free flow speed
calculate_ff_speed(filesID, outDir, dirData, percentile_free_flow)

# compute capacity data
capacity_data(dirCapaData, filesID, outDir)


# calculate congestion counts
for instance in timeInstances.keys():
    x = calculate_cong_hrs(filesID, outDir, dirData_l, percentile_free_flow, timeInstances[instance])
    zdump(x, outDir + 'cong_count_' + instance + '.pkz' )

# in case one want to paralellize
instance = "all"
x = calculate_cong_hrs(filesID, outDir, dirData_l, percentile_free_flow, timeInstances[instance])
zdump(x, outDir + 'cong_count_' + instance + '.pkz' )

    
# calculate average travel times 
for instance in timeInstances.keys():
	travel_t_x = calculate_travelt_avg(filesID, outDir, dirFilteredData, percentile_free_flow, timeInstances[instance]) # for 2012 dirFilteredData for 2015 dirData_l
	zdump(travel_t_x, outDir + 'avg_speed_' + instance + '_' + filesID +  '.pkz') 



create_cong_shpFiles(outDir, filesID, dirShpFile, timeInstances)

create_travelT_shpFiles(outDir, filesID, dirShpFile, timeInstances)


execfile('comparisonYears.py')

