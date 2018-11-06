# -*- coding: utf-8 -*-
"""
Created on Fri Nov 02 00:18:55 2018

@author: Salomon Wollenstein
"""

# Import libraries
from utils import *
execfile('parameters.py')
execfile('functions.py')

import geopandas

filesID_2012 = '2012_4-6_' 
filesID_2015 = '2015_4-6_new'
zipCodeDir = '../zipCodeShp/'
zipCodeFile = 'ZIPCODES_NT_POLY.shp'


outDir_2012 = outDir = '../results/' + filesID_2012 + '/' 
outDir_2015 = outDir = '../results/' + filesID_2015 + '/' 
outDir = '../results/comparison_2012_2015/' 

if os.path.isdir(outDir) == False:
    os.mkdir(outDir)

zipCodes = geopandas.read_file(zipCodeDir  + zipCodeFile )

for instance in timeInstances.keys():
   # x = zload(outDir + 'cong_count_' + instance + '.pkz' )
    dataZip = geopandas.GeoDataFrame()
    data2012 = geopandas.read_file(outDir_2012  + "cong_" + instance + '_' +  filesID_2012 + ".shp")
    data2015 = geopandas.read_file(outDir_2015 + "cong_" + instance + '_' +  filesID_2015 + ".shp")
    data2015 = data2015.drop(columns = 'geometry')
    
    data2012 = data2012.rename(columns={'cong_time':'cong_2012'})
    data2015 = data2015.rename(columns={'cong_time':'cong_2015'})
    
    data = pd.merge(data2012, data2015, on="TMC")
    data["cong_diff"] = data["cong_2015"] - data["cong_2012"] 
    data.to_file(outDir + "cong_comparison_" + instance + ".shp")
'''  
    dataZip = data
    dataZip['congZip2012_'] = data["cong_2012"] * data["Shape_Leng_x"]
    dataZip['congZip2015_'] = data["cong_2015"] * data["Shape_Leng_x"]
    
    dataZip = data.groupby('ZIP_x').agg(np.sum)
    
    dataZip['congZip2012'] = dataZip["congZip2012_"] / dataZip["Shape_Leng_x"]
    dataZip['congZip2015'] = dataZip["congZip2015_"] / dataZip["Shape_Leng_x"]
    
    dataZip['congDiff'] = dataZip['congZip2015']  - dataZip['congZip2012'] 
    dataZip['congPercent'] = dataZip['congZip2015'] / dataZip['congZip2012'] 
    dataZip = dataZip.reset_index()
    dataZip["ZIP"] = dataZip["ZIP_x"]
    zipCodes["ZIP"] = zipCodes["POSTCODE"].str[1:]
    
    zipCodes_ = pd.merge(zipCodes, dataZip, on="ZIP")
'''    
    
   # zipCodes_.to_file(outDir + "zip_comparison_" + instance + ".shp")
    
    
    
    
    
    
    
    
    