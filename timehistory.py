#!/anaconda/bin/python3
# -*- coding: utf-8 -*-
"""
timehistory.py

Created on Wed Apr 13 16:54:34 2016

@author: vinceq
"""

import os
import geojson
from shutil import copyfile

alldata = {}
inputdir = './input'
outputfilename = './timehistory.json'

def main():
    for i in os.listdir(inputdir):
        if not '.geojson' in i: 
            continue
        i = inputdir + '/' + i
        print('Opening ' + i)
        data = geojson.load(open(i))
    
        outdata = extractdata(data)
        if outdata:
            evid = outdata['evid']
            alldata[evid] = outdata
        
    print('Writing to ' + outputfilename)
    with open(outputfilename,'w') as outfile:
        geojson.dump(alldata,outfile)
    print('Finished writing to ' + outputfilename)
    copyfile(outputfilename,'./leaflet/data/timehistory.json')

def extractdata(data):
    epicenter = ''
    times = []
    f = data['features']
    for feature in f:
        if 'is_epicenter' in feature.properties:
            epicenter = feature
            continue
        t = feature.properties['t']
        times.append(t)

    times.sort()
    ep = epicenter.properties

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

    out = {
        'evid' : evid,
        'region' : region,
        'mag' : ep['mag'],
        'times' : times,
    }
    for n in ((1,10,20,30,40,50,60,70,80,90,100)):
        t = timeToN(n,times)
        if t:
            out[n] = t

    return out    

def timeToN(n,times):
    if len(times) <= n:
        return 0
    if times[n]:
        return times[n]
    return 0

# Start program here

main()
            
