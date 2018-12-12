
from __future__ import (absolute_import, division, print_function)
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import glob
#import geopandas
import pandas as pd
import networkx as nx

from utils import *
from scipy import stats

#import parameters

# Import network
def import_network(filesID, outDir, dirFilteredData, filterBy, zipCode):

    # Read full network 
    fullNetwork = geopandas.read_file(dirShpFile)
    
    
    #Filter TMCs in the bounding box
    if filterBy == 'box':
        filteredNet = fullNetwork.cx[min(lonMin, lonMax):max(lonMin, lonMax), 
                                           min(latMax, latMin):max(latMax, latMin)]
    
        #filteredNet.rename(columns={'Tmc':'TMC'}, inplace=True)
        
        del fullNetwork
        
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        
        # Get edge attributes from net
        filteredNet  = pd.merge(tmcLookup, filteredNet, on='TMC')
    
    elif filterBy == 'zipCode':
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        tmcLookup = tmcLookup[tmcLookup['Zip'].isin(zipCode)]
        tmc_net_list =  tmcLookup['TMC'].tolist()
        
        filteredNet = fullNetwork[fullNetwork['TMC'].isin(tmc_net_list)]
        #filteredNet.rename(columns={'Tmc':'TMC'}, inplace=True)
        
        del fullNetwork
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        
        filteredNet_  = pd.merge(tmcLookup, filteredNet, on='TMC')
        
    elif filterBy == 'county':
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        tmcLookup = tmcLookup[tmcLookup['County'] == County]
        tmc_net_list =  tmcLookup['TMC'].tolist()
        
        filteredNet = fullNetwork[fullNetwork['TMC'].isin(tmc_net_list)]
        #filteredNet.rename(columns={'Tmc':'TMC'}, inplace=True)
        
        del fullNetwork
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        
        filteredNet_  = pd.merge(tmcLookup, filteredNet, on='TMC')
    
    elif filterBy == 'all':
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)
        tmc_net_list =  tmcLookup['TMC'].tolist()
        
        filteredNet = fullNetwork[fullNetwork['TMC'].isin(tmc_net_list)]
        
        del fullNetwork
        # Read master lookup table
        tmcLookup = pd.read_excel(dirTmcLookup)  
        filteredNet_  = pd.merge(tmcLookup, filteredNet, on='TMC')

    # Plot map
    filteredNet.plot()
        
    # Filter the counties in the map
    counties = list(set(filteredNet_['County'].tolist()))
    
    zdump(tmc_net_list, outDir + 'tmc_net_list.pkz')
    zdump(counties, outDir + 'counties.pkz')
    
    # create tmc_att file
    shape = nx.read_shp(dirShpFile)
    edge_attributes = pd.DataFrame(i[2] for i in shape.edges(data=True))
    tmc_att = pd.DataFrame()
    tmc_att = tmc_att.append(edge_attributes[edge_attributes['TMC'].isin(tmc_net_list)])
    zdump(tmc_att, outDir + 'tmc_att' + filesID + '.pkz')


def calculate_ff_speed(filesID, outDir, dirData, percentile_ff):
    #extract data from 2015 database  
    df = pd.DataFrame()
    cnt = 0
    filtered_files_list = []
    dir_ = os.path.join(dirData)
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    counties = zload(outDir + 'counties.pkz')
    for root,dirs,files in os.walk(dir_):
        for file in files:
            #df = pd.DataFrame()
            if file.endswith(".csv"):
                iter_csv = pd.read_csv(root + '/' +  file, iterator=True, chunksize=200000)
                for chunk in iter_csv:
                    chunk['measurement_tstamp']=pd.to_datetime(chunk['measurement_tstamp'], format='%Y-%m-%d %H:%M:%S')
                    #chunk = chunk.set_index('tmc_code')
                    chunk = chunk[['tmc_code', 'speed']]
                    df = df.append(chunk)
                    cnt = cnt + 1
                    filtered_files_list.append( outDir + 'filtered_tmc_date_' + file[:-4]  +'.pkz' )
                    print(file + ' : ' + str(cnt))
                print('-----------------------------------------------------')
                #del df

    #Calculate percentiles 
    #df = df.restart_index()
    tmc_free_flow = df.groupby('tmc_code').agg(percentile(percentile_ff))['speed'] 
    nonzero_mean = tmc_free_flow[ tmc_free_flow != 0 ].mean()
    tmc_free_flow.loc[ tmc_free_flow == 0] = nonzero_mean
    tmc_free_flow.name= 'free_flow_speed'
    pd.to_pickle(tmc_free_flow, outDir + 'free_flow_speed_ ' + filesID + '.pkz')
    


def capacity_data(dir_capacity_data, filesID, outDir):  
    # tmc and roadinv lookup'
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    lookup_tmc_roadinv = pd.read_excel(dir_capacity_data + 'roadinv_id_to_tmc_lookup.xlsx', index_col=None, na_values=['NA'], parse_cols = "A,D")
    lookup_tmc_roadinv = lookup_tmc_roadinv.set_index('ROADINV_ID')
    lookup_tmc_roadinv = lookup_tmc_roadinv[lookup_tmc_roadinv['TMC'].isin(tmc_net_list)]
    
    # Load capacity file'
    
    cap_data = pd.read_excel(dir_capacity_data + 'capacity_attribute_table.xlsx', index_col=None, na_values=['NA'], parse_cols = "B,H,J,L,N,P,R,T,V,X,Z")
    cap_data.rename(columns={'SCEN_00_AB': "AB_AMLANE", 'SCEN_00_A1': "AB_MDLANE", 'SCEN_00_A2': 'AB_MDLANE', 'SCEN_00_A3': 'AB_PMLANE' }, inplace=True)
    
    cap_data = cap_data.set_index('ROADINVENT')
    cap_data.index = cap_data.index.fillna(0).astype(np.int64)
        
     # take the period capacity factor into consideration
    cap_data.AB_AMCAPAC = (1.0/2.5) * cap_data.AB_AMCAPAC 
    cap_data.AB_MDCAPAC = (1.0/4.75) * cap_data.AB_MDCAPAC
    cap_data.AB_PMCAPAC = (1.0/2.5) * cap_data.AB_PMCAPAC
    cap_data.AB_NTCAPAC = (1.0/7.0) * cap_data.AB_NTCAPAC
    
    result = cap_data
    result  = result.join(lookup_tmc_roadinv, how='inner')
    result = result.set_index('TMC')


    pd.to_pickle(lookup_tmc_roadinv,  outDir + 'lookup_tmc_roadinv' + filesID + '.pkz')
    pd.to_pickle(result, outDir + 'capacity_data_' + filesID + '.pkz')
    pd.to_pickle(cap_data, outDir + 'cap_data' + filesID + '.pkz')
    
    

def calculate_cong_hrs(filesID, outDir, dirData_b, percentile_ff, time_instance):
    #extract data from 2015 database  
    df = pd.DataFrame()
    cnt = 0
    filtered_files_list = []
    dir_ = os.path.join(dirData_b)
    print(dir_ )
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    counties = zload(outDir + 'counties.pkz')
    tmc_free_flow = pd.read_pickle(outDir + 'free_flow_speed_ ' + filesID + '.pkz')
    free_flow_ov_mean = tmc_free_flow.mean()
    tmc_free_flow[tmc_free_flow==0] = free_flow_ov_mean  #delete zeros
    tmc_free_flow = tmc_free_flow.to_dict()
    
    capacity_data = pd.read_pickle( outDir + 'capacity_data_' + filesID + '.pkz')
    capacity_data = capacity_data[['LENGTH', 'AB_AMCAPAC']]
    capacity_data_c = capacity_data['AB_'+ 'AM' +'CAPAC'].to_dict()
    capacity_data_l = capacity_data['LENGTH'].to_dict()
    
    length_mode = stats.mode(capacity_data_l.values()).mode[0]
    
    
    del capacity_data
    
    #define dictionary
    x = {}
    for tmc in tmc_net_list:
        x[tmc] = {}
        x[tmc]['cong'] = 0 
        x[tmc]['no_cong'] = 0 
    
    for root,dirs,files in os.walk(dir_):
        for file in files:
            #df = pd.DataFrame()
            if file.endswith(".csv"):
                iter_csv = pd.read_csv(root + '/' +  file, iterator=True, chunksize=200000)
                for chunk in iter_csv:
                    if  len(chunk) == 0:
                        continue
                   # chunk['tmc_code'] = chunk['tmc']
                   # chunk['year'] = (len(chunk))*[2012]
                   # chunk['measurement_tstamp'] = pd.to_datetime(chunk[['year', 'month', 'day', 'hour', 'minute']]) # ONLY FOR 2012
                    chunk = chunk[['tmc_code', 'measurement_tstamp', 'speed']]
                    chunk['measurement_tstamp'] = pd.to_datetime(chunk['measurement_tstamp'], format='%Y-%m-%d %H:%M:%S')
                    chunk = chunk.set_index('measurement_tstamp')
                    chunk['dayWeek'] = chunk.index.dayofweek
                    chunk = chunk[chunk['dayWeek'].isin(daysWeek)]
                    if  len(chunk) == 0:
                        continue
                    chunk['hr'] = chunk.index.hour
                    chunk = chunk[['tmc_code', 'hr', 'speed']]
                    chunk = chunk.reset_index()
                    chunk = chunk.set_index('measurement_tstamp')
                    
                    
                    chunk = chunk[chunk['hr'].isin(time_instance)] #filter for AM
                    
                    if  len(chunk) == 0:
                        continue
        
                    for idx, row2 in chunk.iterrows():
                        tmc = row2['tmc_code']
                        try:
                            capacity = capacity_data_c[tmc]
                        except:
                            capacity = 2000
                        try:
                            length = capacity_data_l[tmc]
                        except:
                            length = length_mode 
                        try:
                            free_flow_sp = tmc_free_flow[tmc]
                        except:
                            free_flow_sp = free_flow_ov_mean
                        
                        speed = row2['speed']
                        if speed == 0:
                            speed = 1
                        #avg_speed = row2['avg_speed_day']
                        x_flow = greenshield(min(speed, free_flow_sp) , capacity , free_flow_sp)
                        density = greenshield_density([min(speed, free_flow_sp)], capacity, free_flow_sp, length, 1)
                        speed = max(speed, 1)
    
                        if density[0] >= capacity:
                            try:
                                x[tmc]['cong'] += 1
                            except:
                                x[tmc] = {}
                                x[tmc]['cong'] = 1
                                x[tmc]['no_cong'] = 0 
                        else:
                            try:
                                x[tmc]['no_cong'] += 1
                            except:
                                x[tmc] = {}
                                x[tmc]['cong'] = 0
                                x[tmc]['no_cong'] = 1
                        
                        cnt += 1
                    print(file + ":" + str(cnt))

    return x


def calculate_travelt_avg(filesID, outDir, dirData_b, percentile_ff, time_instance):
    #extract data from 2015 database  
    df = pd.DataFrame()
    cnt = 0
    filtered_files_list = []
    dir_ = os.path.join(dirData_b)
    print(dir_ )
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    counties = zload(outDir + 'counties.pkz')
    tmc_free_flow = pd.read_pickle(outDir + 'free_flow_speed_ ' + filesID + '.pkz')
    free_flow_ov_mean = tmc_free_flow.mean()
    tmc_free_flow[tmc_free_flow==0] = free_flow_ov_mean  #delete zeros
    tmc_free_flow = tmc_free_flow.to_dict()
    
    capacity_data = pd.read_pickle( outDir + 'capacity_data_' + filesID + '.pkz')
    capacity_data = capacity_data[['LENGTH', 'AB_AMCAPAC']]
    capacity_data_c = capacity_data['AB_'+ 'AM' +'CAPAC'].to_dict()
    capacity_data_l = capacity_data['LENGTH'].to_dict()
    
    length_mode = stats.mode(capacity_data_l.values()).mode[0]
    
    
    del capacity_data
    
    #define dictionary
    x = {}
    travel_time_s = {}
    travel_time_cnt = {}
    for tmc in tmc_net_list:
        x[tmc] = []
        travel_time_s[tmc]  = 0
        travel_time_cnt[tmc]  = 0
        #x[tmc]['cong'] = 0 
        #x[tmc]['no_cong'] = 0 
    
    for root,dirs,files in os.walk(dir_):
        for file in files:
            #df = pd.DataFrame()
            if file.endswith(".csv"):
                iter_csv = pd.read_csv(root + '/' +  file, iterator=True, chunksize=200000)
                for chunk in iter_csv:
                    if  len(chunk) == 0:
                        continue
                    chunk['tmc_code'] = chunk['tmc']# ONLY FOR 2012
                    chunk['year'] = (len(chunk))*[2012]# ONLY FOR 2012
                    chunk['measurement_tstamp'] = pd.to_datetime(chunk[['year', 'month', 'day', 'hour', 'minute']]) # ONLY FOR 2012
                    chunk = chunk[['tmc_code', 'measurement_tstamp', 'travel_time']] #for 2012
                    
                    #chunk = chunk[['tmc_code', 'measurement_tstamp', 'travel_time_minutes']] # For 2015
                    #chunk['travel_time'] = chunk['travel_time_minutes'] # for 2015
                    #chunk['measurement_tstamp'] = pd.to_datetime(chunk['measurement_tstamp'], format='%Y-%m-%d %H:%M:%S') #for 2015
                    
                    chunk = chunk.set_index('measurement_tstamp')
                    chunk['dayWeek'] = chunk.index.dayofweek
                    chunk = chunk[chunk['dayWeek'].isin(daysWeek)]
                    if  len(chunk) == 0:
                        continue
                    chunk['hr'] = chunk.index.hour
                    chunk = chunk[['tmc_code', 'hr', 'travel_time']]
                    chunk = chunk.reset_index()
                    df = chunk.set_index('measurement_tstamp')
                    df['count'] = 1
                    
                    df = df[df['hr'].isin(time_instance)] #filter for AM
                    
                    df = df.groupby('tmc_code').sum()
                    
                    df = df.reset_index()
                    
                    if  len(df) == 0:
                        continue
                    
                    tmcs = travel_time_s.keys()
                    for tmc in list(df['tmc_code']):
                        if tmc not in tmcs:
                            travel_time_s[tmc] = 0
                            travel_time_cnt[tmc] = 0
                    for idx, row2 in df.iterrows():
                        
                        tmc = row2['tmc_code']          
                        travel_time = row2['travel_time']
                        counts = row2['count']
                            
                        travel_time_s[tmc] += travel_time
                        travel_time_cnt[tmc]  += counts
                        
                        cnt += counts
                        
                    print(file + ":" + str(cnt))
    
    for tmc in travel_time_s.keys():
        x[tmc] = 0
        try:
            x[tmc] = travel_time_s[tmc] / travel_time_cnt[tmc]
        except:
            x[tmc] = "NA"

    return x



def calculate_travelt_vec(filesID, outDir, dirData_b, percentile_ff, time_instance):
    #extract data from 2015 database  
    df = pd.DataFrame()
    cnt = 0
    filtered_files_list = []
    dir_ = os.path.join(dirData_b)
    print(dir_ )
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    counties = zload(outDir + 'counties.pkz')
    tmc_free_flow = pd.read_pickle(outDir + 'free_flow_speed_ ' + filesID + '.pkz')
    free_flow_ov_mean = tmc_free_flow.mean()
    tmc_free_flow[tmc_free_flow==0] = free_flow_ov_mean  #delete zeros
    tmc_free_flow = tmc_free_flow.to_dict()
    
    capacity_data = pd.read_pickle( outDir + 'capacity_data_' + filesID + '.pkz')
    capacity_data = capacity_data[['LENGTH', 'AB_AMCAPAC']]
    capacity_data_c = capacity_data['AB_'+ 'AM' +'CAPAC'].to_dict()
    capacity_data_l = capacity_data['LENGTH'].to_dict()
    
    length_mode = stats.mode(capacity_data_l.values()).mode[0]
    
    
    del capacity_data
    
    #define dictionary
    x = {}
    for tmc in tmc_net_list:
        x[tmc] = []
        #x[tmc]['cong'] = 0 
        #x[tmc]['no_cong'] = 0 
    
    for root,dirs,files in os.walk(dir_):
        for file in files:
            #df = pd.DataFrame()
            if file.endswith(".csv"):
                iter_csv = pd.read_csv(root + '/' +  file, iterator=True, chunksize=200000)
                for chunk in iter_csv:
                    if  len(chunk) == 0:
                        continue
                    chunk['tmc_code'] = chunk['tmc']# ONLY FOR 2012
                    chunk['year'] = (len(chunk))*[2012]# ONLY FOR 2012 
                    chunk['measurement_tstamp'] = pd.to_datetime(chunk[['year', 'month', 'day', 'hour', 'minute']]) # ONLY FOR 2012
                    chunk = chunk[['tmc_code', 'measurement_tstamp', 'speed']]
                    chunk['measurement_tstamp'] = pd.to_datetime(chunk['measurement_tstamp'], format='%Y-%m-%d %H:%M:%S')
                    chunk = chunk.set_index('measurement_tstamp')
                    chunk['dayWeek'] = chunk.index.dayofweek
                    chunk = chunk[chunk['dayWeek'].isin(daysWeek)]
                    if  len(chunk) == 0:
                        continue
                    chunk['hr'] = chunk.index.hour
                    chunk = chunk[['tmc_code', 'hr', 'speed']]
                    chunk = chunk.reset_index()
                    chunk = chunk.set_index('measurement_tstamp')
                    
                    
                    chunk = chunk[chunk['hr'].isin(time_instance)] #filter for AM
                    
                    if  len(chunk) == 0:
                        continue
        
                    for idx, row2 in chunk.iterrows():
                        tmc = row2['tmc_code']
                        try:
                            length = capacity_data_l[tmc]
                        except:
                            length = length_mode                   
                        speed = row2['speed']
                        speed = max(speed, 2)
                        travel_time = length/speed
                        try:
                            x[tmc].append(travel_time)
                        except:
                            x[tmc] = []
                            x[tmc].append(travel_time)
                        cnt += 1
                    print(file + ":" + str(cnt))
    return x



def create_cong_shpFiles(outDir, filesID, dirShpFile, timeInstances):
    # creating shp file
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    for instance in timeInstances.keys():
        cong_hrs = {}
        x = zload(outDir + 'cong_count_' + instance + '.pkz' )
        for tmc in x.keys():
            try:
                cong_hrs[tmc] = round( (x[tmc]['cong'] /(x[tmc]['cong'] + x[tmc]['no_cong'])) * 
                        (timeInstances[instance][1]-timeInstances[instance][0]+1) , 2)
            except:
                cong_hrs[tmc] = 0 
                    
        
        cong_hrs  = pd.DataFrame.from_dict(cong_hrs.items())
        cong_hrs = cong_hrs.rename(index=str, columns={0: "TMC", 1: "cong_time"})
        
        fullNetwork = geopandas.read_file(dirShpFile)
        cong_shp = pd.merge(fullNetwork, cong_hrs, on='TMC')
        cong_shp.to_file(outDir + "cong_" + instance + '_' +  filesID + ".shp")
        
        
        

def create_travelT_shpFiles(outDir, filesID, dirShpFile, timeInstances):
    # creating shp file
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    for instance in timeInstances.keys():
        cong_hrs = {}
        x = zload(outDir+ 'avg_travelT_' + instance + '_' + filesID +  '.pkz' )
        
        x_val = []
        x_tmc = []
        for i in x.keys():
           # try:
           #     x_1 = np.float(x[i])
            #except:
            #    del x[i]
                
            x_ = x[i]
            x_val.append(x_)
        
        x_val = [x_val[i] for i in range(len(x_val)) if str(x_val[i]) != 'nan']
        x_tmc = [x.keys()[i] for i in range(len(x_val)) if str(x_val[i]) != 'nan']

        x_val = [x_val[i] for i in range(len(x_val)) if str(x_val[i]) != 'NA']
        x_tmc = [x.keys()[i] for i in range(len(x_val)) if str(x_val[i]) != 'NA']
        
        
        df = pd.DataFrame()
        df['TMC']  = x_tmc
        df['travelT'] = x_val
        
        fullNetwork = geopandas.read_file(dirShpFile)
        travelT_shp = pd.merge(fullNetwork, df, on='TMC')
        travelT_shp.to_file(outDir + "travelT_" + instance + '_' +  filesID + ".shp")
        
    
def unzip_2012_data(outDir, files_dir, dirFilteredData):
    tmc_net_list = zload(outDir + 'tmc_net_list.pkz')
    cnt = 0 
    for input_file in glob.glob(files_dir+ '/' + '*.csv.gz'):
        cnt +=1
        with gzip.open(input_file, 'rb') as inp, \
                open(dirFilteredData +'filtered_tmc_' + input_file[-22:][:-7] + '.csv', 'wb') as out:
            writer = csv.writer(out)
            for row in csv.reader(inp):
          #      if row[0] in tmc_net_list:
                 writer.writerow(row)
        print(cnt)

    for root,dirs,files in os.walk(outDir +'filtered_tmc_data/'):
        for file in files:
           df = pd.DataFrame()
           if file.endswith(".csv"):                   
               df = pd.read_csv(root + '/' +  file)
               col_names = ['tmc_code', 'month', 'day', 'dow', 'hour', 'minute', 'speed', 'avg_speed', 'ref_speed', 'travel_time', 'confidence_score', 'c_value']
               df.columns = col_names
               df['year'] = (len(df))*[2012]
               df['measurement_tstamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])
               df = df.drop(columns=['year', 'month', 'day', 'hour', 'minute'])
               df = df.rename(columns={'tmc': 'tmc_code', 'c_value': 'cvalue'})
               # Here we will add this function in order to process just once the files
               df = df.set_index('measurement_tstamp')
               #df2 = filter_tmc(df,tmc_net_list,confidence_score_min,c_value_min)   
               
               df2 = df
               #cnt = cnt + 1
               #filtered_files_list.append( out_dir + 'filtered_tmc_date_' + file[:-4]  +'.pkz' )
               pd.to_pickle(df2, outDir +'filtered_tmc_data/' + file[:-4]  +'.pkz')
               #df2.to_csv(out_dir + 'filtered_tmc_' + file[:-4]  +'.csv')
               print(file + ': unzipped !')
