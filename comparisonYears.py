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


capacity_data = pd.read_pickle( outDir + 'capacity_data_' + filesID + '.pkz')
capacity_data = capacity_data[['LENGTH', 'AB_AMCAPAC']]
capacity_data_c = capacity_data['AB_'+ 'AM' +'CAPAC'].to_dict()
capacity_data_l = capacity_data['LENGTH'].to_dict()
    

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
    
    data2012_tT = geopandas.read_file(outDir_2012  + "travelT_" + instance + '_' +  filesID_2012 + ".shp")
    data2015_tT = geopandas.read_file(outDir_2015  + "travelT_" + instance + '_' +  filesID_2015 + ".shp")
    data2015_tT = data2015_tT.drop(columns = 'geometry')
    
    data2012 = data2012.rename(columns={'cong_time':'cong_2012'})
    data2015 = data2015.rename(columns={'cong_time':'cong_2015'})
    
    data2012_tT = data2012_tT.rename(columns={'travelT':'travelT_2012'})
    data2015_tT = data2015_tT.rename(columns={'travelT':'travelT_2015'})   
    
    data = pd.merge(data2012, data2015, on="TMC")
    #data2015.set_index("TMC")
    #data2012.set_index("TMC")
    #cols_to_use = data2015.columns.difference(data2012.columns)
    #data = pd.merge(data2012, data2015[cols_to_use], left_index=True, right_index=True, how='inner')
    #data = data.reset_index()    
    
 #  data = pd.merge(data2012, data2015, on="TMC")
    data["cong_diff"] = data["cong_2015"] - data["cong_2012"] 
    
    
    #data2015_tT.set_index("TMC")
    #data2012_tT.set_index("TMC")
    #cols_to_use = data2012_tT.columns.difference(data2015_tT.columns)
    #dataT = pd.merge(data2015_tT, data2012_tT[cols_to_use], left_index=True, right_index=True, how='inner')
    #dataT = dataT.reset_index()
    
    dataT = pd.merge(data2015_tT, data2012_tT, on="TMC")
    
    dataT['tT_2012'] = dataT['travelT_2012']*60*60
    dataT['tT_2015'] = dataT['travelT_2015']*60*60
    
    #dataT["travelT_increase"] = dataT["travelT_2015"]/dataT["travelT_2012"] 
    
    data["cong_diff"] = data["cong_diff"]*60
    data["cong_2012"] = data["cong_2012"]*60
    data["cong_2015"] = data["cong_2015"]*60
        
    dataT = dataT[['TMC', 'tT_2012', 'tT_2015']]
        
    dataF = pd.merge(data, dataT, on="TMC")
    
    dataF["tT_increase"] = ((dataF["tT_2015"]/dataF["tT_2012"]) - 1) * 100 
    
    dataF["tT_increase_"] = dataF["tT_increase"].astype(int).astype(str) + ' %'
    
    dataF["cong_diff_"] = dataF["cong_diff"].astype(int).astype(str) + " min"
    dataF["cong_2012_"] = dataF["cong_2012"].astype(int).astype(str) + " min"
    dataF["cong_2015_"] = dataF["cong_2015"].astype(int).astype(str) + " min"
    
    dataF.to_file(outDir + "cong_comparison_" + instance + ".shp")
    #dataT.to_file(outDir + "travelT_comparison_" + instance + ".shp")

    # zipcode for congestion 
    dataZip = dataF
    dataZip['congZip2012_'] = dataF["cong_2012"] * dataF["Shape_Leng_x"]
    dataZip['congZip2015_'] = dataF["cong_2015"] * dataF["Shape_Leng_x"]
    
    
    dataZip = dataF.groupby('ZIP_x').agg(np.sum)
    
    dataZip['congZip2012'] = dataZip["congZip2012_"] / dataZip["Shape_Leng_x"]
    dataZip['congZip2015'] = dataZip["congZip2015_"] / dataZip["Shape_Leng_x"]
    
    dataZip['congDiff'] = dataZip['congZip2015']  - dataZip['congZip2012']
    dataZip['congPercent'] = dataZip['congZip2015'] / dataZip['congZip2012'] 
    dataZip = dataZip.reset_index()
    dataZip["ZIP"] = dataZip["ZIP_x"]
    zipCodes["ZIP"] = zipCodes["POSTCODE"].str[1:]
    
    zipCodes_ = pd.merge(zipCodes, dataZip, on="ZIP")
    #zipCodes_.to_file(outDir + "zip_comparison_" + instance + ".shp")
    
    # zipcode for travel time
    dataZipT = dataF
    dataZipT['tTZip2012_'] = dataF["tT_2012"] * dataF["Shape_Leng_x"]
    dataZipT['tTZip2015_'] = dataF["tT_2015"] * dataF["Shape_Leng_x"]
    
    
    dataZipT = dataF.groupby('ZIP_x').agg(np.sum)
    
    dataZipT['tTZip2012'] = dataZipT["tTZip2012_"] / dataZipT["Shape_Leng_x"]
    dataZipT['tTZip2015'] = dataZipT["tTZip2015_"] / dataZipT["Shape_Leng_x"]
    
    dataZipT['travelTPercent'] = ((dataZipT['tTZip2015']  / dataZipT['tTZip2012'])  - 1) * 100
    dataZipT = dataZipT.reset_index()
    dataZipT["ZIP"] = dataZipT["ZIP_x"]
    zipCodes["ZIP"] = zipCodes["POSTCODE"].str[1:]
    
    zipCodes_T = pd.merge(zipCodes, dataZipT, on="ZIP")
    
    zipCodes_T = zipCodes_T[["tTZip2012", "tTZip2015", "travelTPercent",  "ZIP" ]]
    
    zipCodes_F = pd.merge(zipCodes_, zipCodes_T, on="ZIP")
    
    zipCodes_F["tTZip2012"] = zipCodes_F["tTZip2012"].astype(int).astype(str) + " min"
    zipCodes_F["tTZip2015"] = zipCodes_F["tTZip2015"].astype(int).astype(str) + " min"
    zipCodes_F["travelTPercent"] = zipCodes_F["travelTPercent"].astype(int).astype(str) + " %"
    zipCodes_F["CongDiff_"] = zipCodes_F["congDiff"].astype(int).astype(str) + " min"
    zipCodes_F["congZip2012"] = zipCodes_F["congZip2012"].astype(int).astype(str) + " min"
    zipCodes_F["congZip2015"] = zipCodes_F["congZip2015"].astype(int).astype(str) + " min"
    
    zipCodes_F.to_file(outDir + "zip_comparison_" + instance + ".shp")
    