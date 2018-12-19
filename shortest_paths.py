# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 17:19:16 2018

@author: Salomon Wollenstein
"""

# libraries
import os 
os.chdir('G:/My Drive/Github/INRIX_vis/main')

execfile('parameters.py')

import fiona
import networkx as nx
import itertools 
import osmnx as ox
import random
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Point, MultiPoint
import geopandas
import numpy as np
import pandas as pd
import mplleaflet
import json
from utils import *

# functions
def closest_node(G, coord):
    x = coord[0]
    y = coord[0]
    closest_n = {}
    closest_n['dist'] = np.infty
    closest_n['node'] = np.nan
    pos = nx.get_node_attributes(G,'pos')
    
    for node in pos:
        X = node[0]
        Y = node[0]
        dist = (X-x)**2 + (Y-y)**2
        if dist < closest_n['dist']:
            closest_n['dist'] = dist
            closest_n['node'] = node
            
    return closest_n
   

     
'''
# Parameters
filesID_2012 = '2012_4-6_' 
filesID_2015 = '2015_4-6_new'
zipCodeDir = '../zipCodeShp/'
zipCodeFile = 'ZIPCODES_NT_POLY.shp'
'''
outDir = '../results/'

# Reading the shapefles 
ShpFile = 'G:/My Drive/Github/INRIX_vis/results/comparison_2012_2015/cong_comparison_AM.shp'
G = nx.read_shp(ShpFile, simplify=False, geom_attrs=True)
G_gdf = geopandas.read_file(ShpFile)
zipG = geopandas.read_file('G:/My Drive/Github/INRIX_vis/results/comparison_2012_2015/zip_comparison_AM.shp')


# Get the biggest weakly connected subgraph
disj_G = list(nx.weakly_connected_component_subgraphs(G, copy=True))


# find the biggest subgraph
l_max = 0
cnt = 0
for g in disj_G:
    l = len(list(g.nodes()))
    if l>l_max:
        l_max = l
        idx = cnt
    cnt +=1

G = disj_G[idx]
print('the biggest subgraph has: ' + str(l_max) + ' nodes and: ' + str(len(G.edges())) + ' edges')
    


    
# Finding the centroid of each zip code
zipG['centroid'] = zipG.geometry.centroid

# reading the weigths for the 2012 and 2015 grapgs
G_2012 = nx.DiGraph()
G_2015 = nx.DiGraph()
for data in G.edges(data=True):
   G_2012.add_edge(data[0],data[1], weight=data[2]['tT_2012'], pos=data[0])
   G_2015.add_edge(data[0],data[1], weight=data[2]['tT_2015'], pos=data[0])

# getting the position of each node
for data in G.nodes(data=True):
    G_2012.node[data[0]]['pos'] = data[0]
    G_2015.node[data[0]]['pos'] = data[0]

# Find the closest node to the centroid of each zip code
zip_nodes = {}
zip_centroids = {}
len_nodes = len(zipG['centroid'])
cnt = 0
for index, zip_ in zipG.iterrows():
    zip_name = zip_['Zip']
    i = zip_['centroid']
    orgn_node_ = (i.x, i.y)
    zip_centroids[zip_name] = orgn_node_
    orig_node = closest_node(G_2012, orgn_node_)
    zip_nodes[zip_name] = orig_node['node']
    cnt +=1
    print('processed centroid: ' + str(cnt) + ' out of: ' + str(len_nodes))


plt.scatter(*zip(*zip_centroids.values()))
plt.scatter(*zip(*zip_nodes.values()))

print ('----------------------------------')


# Calculate shortest paths. This probably can be imporved my using multi-source shortest path algorithy
n_iter = len(zip_nodes)
routes = {}
cnt = 0
for i in zip_nodes:
    routes[i] = {}
    cnt += 1
    zip_len2 = {}
    zip_len5 = {}
    for j in zip_nodes:
        path = {}
        path['source'] = zip_nodes[i]
        path['target'] =  zip_nodes[j]
        path['zip_source'] =  i
        path['zip_target'] =  j
        try:
            path['path_2012'] = nx.shortest_path(G_2012, zip_nodes[i], zip_nodes[j], weight='weight')
            path['length_2012'] = nx.shortest_path_length(G_2012, zip_nodes[i], zip_nodes[j], weight='weight')
            path['path_2015'] = nx.shortest_path(G_2015, zip_nodes[i], zip_nodes[j], weight='weight')
            path['length_2015'] = nx.shortest_path_length(G_2015, zip_nodes[i], zip_nodes[j], weight='weight')
        except:
            path['path_2012'] = []
            path['length_2012'] = -1
            path['path_2015'] = []
            path['length_2015'] = -1
        
        routes[i][j] = path
        zip_len2[j] = path['length_2012']
        zip_len5[j] = path['length_2015']
    
    gpd = zipG
    gpd = gpd[['Zip', 'City', 'County', 'geometry']]
    gpd['tT_2012'] = gpd['Zip'].map(zip_len2)
    gpd['tT_2015'] = gpd['Zip'].map(zip_len5)
    gpd.to_file(outDir + 'sp/shp/zip_' + str(i) + '.shp')
    zdump(gpd, outDir + 'sp/' + 'zip_'+ str(i) + '.pkz')       
    print('processed: ' + str(cnt) + ' out of: ' + str(n_iter))
        
zdump(routes, 'shortest_paths.pkz')

        


# Plot edges and nodes
G2 = nx.DiGraph()
G2.add_edges_from(G_2015.edges())
nx.write_shp(G2, outDir + '/G2')


# Plot OD nodes
G3 = nx.Graph()
G3.add_nodes_from(zip_nodes.values())
nx.write_shp(G3, outDir + '/G3')



gpd.plot(column='tT_2012', cmap='Blues')
root, ext = os.path.splitext(__file__)
#mplleaflet.display(fig=ax.figure, crs=gpd.crs, tiles='cartodb_positron')
mapfile = 'AAA.html'
#root, ext = os.path.splitext(__file__)
mplleaflet.show(path=mapfile, crs=gpd.crs)


'''        
    gpd = zipG[['Zip', 'City', 'County', 'geometry', 'centroid' ]]
    gpd['travel_time_2012'] = gpd['Zip'].map(zip_len2)
    gpd['travel_time_2015'] = gpd['Zip'].map(zip_len5)
    
    
    f, ax = plt.subplots(1)
    ax = gpd.plot(column='travel_time_2012', cmap='Blues',alpha=0.8)
    mplleaflet.display(fig=ax.figure, crs=gpd.crs, tiles='cartodb_positron')
    #mplleaflet.display(fig=f, crs=gpd.crs)
    mplleaflet.show()
'''

plt.hold(True)        
plt.plot(*zip(*path['path_2012']), color='red')
plt.legend('2012')
plt.plot(*zip(*path['path_2015']), color='blue')
plt.legend('2015')
mapfile = 'AAA.html'
root, ext = os.path.splitext(__file__)
mplleaflet.show(path=mapfile, crs=gpd.crs)


plt.plot(xy[:,0], xy[:,1], 'r.')
plt.plot(xy[:,0], xy[:,1], 'b')





for edge in G_2015.edges(data=True):
    edge = list(edge)
    edge[2] = OrderedDict(sorted(edge[2].items()))
    edge=tuple(edge)
