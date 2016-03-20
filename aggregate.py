#! /usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 10 17:51:20 2016

@author: vinceq

Given an FeatureCollection of raw DYFI points, create another file of
aggregated points.

Input is a GeoJSON FeatureCollection of Point Features (individual
DYFI observations). 
"""

import argparse
import os.path
import sys
import geojson
from copy import copy
from shutil import copyfile

from modules import locate_dyfi
from modules import aggregate

tmpgridfile = 'tmp/solutiongrid.geojson'

# INITIAL SETUP

parser = argparse.ArgumentParser(
    description = 'Run the locator on an event')
parser.add_argument('evid',
    help = 'comcat event ID OR inputfile (GeoJSON FeatureCollection)')
parser.add_argument('--utmspan',
    type = int,
    metavar = 'n',
    help = 'Size of geocoded boxes in km (default 1)',
    default = 1)
parser.add_argument('--outputfile',
    type = str,
    metavar = 's',
    help = 'output file (default is "output/aggregated.[evid].geojson")')
    
try:
    args = parser.parse_args()
except:
    print('Exiting...')
    sys.exit()
    
evid = args.evid
if 'geojson' in evid:
    infile = evid
    evid = os.path.basename(evid).split('.')[-2]
else:
    infile = './input/' + evid + '.geojson'

data = geojson.load(open(infile))

outfilename = 'output/aggregated.' + evid + '.geojson'
if args.outputfile:
    print('Using output file %s.' % args.outputfile)
    outfilename = args.outputfile

# DONE INITIAL SETUP

allpts = data['features']

# Extract epicenter data
# TODO: If evdata doesn't exist, handle it
# TODO: Epicenter should have evid; right now, infer from input filename

for i in range(0,len(allpts)):
    if 'is_epicenter' in allpts[i]['properties']: break

evdata = allpts.pop(i)
npts = len(allpts)
print('Finished loading, got %i pts.' % npts)

this_pts = aggregate.aggregate(allpts,args.utmspan)
allgeojson = { 'type': 'FeatureCollection', 'features' : this_pts }
    
print('Writing to ' + outfilename)
with open(outfilename, 'w') as outfile:
    geojson.dump(allgeojson, outfile)

# Copy aggregated grid to leaflet output
webfilename = 'leaflet/data/aggregated.' + evid + '.geojson'
copyfile(outfilename,webfilename)
        
print('Done.')


        

