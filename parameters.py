# Parameters
dirShpFile = 'G:/My Drive/MPO/INRIX/INRIX_shapefile_road_network/INRIX_TMC_Road_Network.shp'
dirTmcLookup = 'G:/Team Drives/MPO 2015/INRIX_2015_Shapefile/Master_TMC_Lookup.xlsx'
dirData = 'G:/Team Drives/MPO 2015/INRIX_byQuarter/fewer' 
dirData_l = 'G:/Team Drives/MPO 2015/INRIX_byQuarter/4-6' 

filesID = '2015_4-6_new'
outDir = '../results/' + filesID + '/' 
dirCapaData = 'G:/Team Drives/MPO 2012/capacity data/'
dirFilteredData = outDir + 'filtered_tmc_data'  + '/'
daysWeek = [0,1,2,3,4]  

datesInput = [#{'id':'Jan','start_date': '2015-01-01' , 'end_date':'2015-01-10'}, 
               #{'id':'Feb','start_date': '2015-02-01' , 'end_date':'2015-02-15'}] 
               {'id':'Apr-Jun','start_date': '2012-04-01' , 'end_date':'2012-07-01'}] 
               #{'id':'Aug','start_date': '2015-08-01' , 'end_date':'2015-08-10'}, 
               #{'id':'Nov','start_date': '2015-11-01' , 'end_date':'2015-11-10'}]

timeInstances = {}
timeInstances['AM'] = [7, 8]
timeInstances['MD'] = [11, 12]
timeInstances['PM'] = [17, 18]
timeInstances['NT'] = [21, 22]
timeInstances['all'] = [0, 23]

data_granularity = '10min'

percentile_free_flow = 85

confidence_level = 0
confidence_score_min = 0 
c_value_min = 0