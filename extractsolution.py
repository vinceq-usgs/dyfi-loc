#!/anaconda/bin/python3
# -*- coding: utf-8 -*-
"""
extractsolution.py

Created on Wed Apr 13 16:54:34 2016

@author: vinceq
"""

import os
import geojson
from geopy.distance import great_circle
from shutil import copyfile

alldata = {}
inputdir = './output'
outputfilename = './summary.json'

def main():
    for i in os.listdir(inputdir):
        if not '.geojson' in i: 
            continue
        if not 'out.' in i:
            continue
        if 'responses.' in i:
            continue
        i = inputdir + '/' + i
        data = geojson.load(open(i))
        print('Opened ' + i)
    
        outdata = extractdata(data)
        if outdata:
            evid = outdata['evid']
            alldata[evid] = outdata
    
    with open(outputfilename,'w') as outfile:
        geojson.dump(alldata,outfile)
    print('Finished writing to ' + outputfilename)
    copyfile(outputfilename,'./leaflet/data/summary.json')

def extractdata(data):
    epicenter = ''
    best = ''
    f = data['features']
    for feature in f:
        if 'is_epicenter' in feature.properties:
            epicenter = feature
            continue
        npts = feature.properties['npts']
        t = feature.properties['t']
#        if t != 600:
        if t != 1200:
            continue
        if not best or npts > best.properties['npts']:
            best = feature
            continue

    if not best:
        return
    ep = epicenter.properties
    be = best.properties

    evid = ep['evid']
    print('Trying ' + evid)
    if 'ci' in evid:
        region = 'sc'
    elif 'nc' in evid:
        region = 'nc'
    elif 'us' in evid:
        region = 'ok'
    else:
        print('No region for ' + evid + ', skipping.')
        return
    print(evid + ' got region ' + region)
    dist = getdist(epicenter,best)
    magdiff = round(be['mag'] - ep['mag'],1)
    out = {
        'evid' : evid,
        'region' : region,
        'dist' : round(dist,1),
        'mag' : ep['mag'],
        'magdiff' : magdiff,
        'npts' : be['npts']
    }
    return out    

def getdist(p1,p2):
    coord1 = getcoords(p1)
    coord2 = getcoords(p2)
    dist = great_circle(coord1,coord2).kilometers
    return dist

def getcoords(p):
    lat = p.geometry.coordinates[1]
    lon = p.geometry.coordinates[0]
    return (lat,lon)

    

# Start program here

main()
            
