#! /usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 10 17:51:20 2016

@author: vinceq

Given an event, run the locator continuously every T_INTERVAL
minutes until all locations are used.

This script only iterates through the input response data,
filtering by entry time at each iteration to simulate a growing
number of responses. All the heavy lifting of the B&W algorithm
is in modules/locate_dyfi.py

Input is a GeoJSON FeatureCollection of Point Features (individual
DYFI observations). Each Point requires two properties:
 
    'user_cdi'  calculated CDI of that entry
    't'         entry time in seconds past origin time

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
tmpipefile = 'tmp/ipeline.json'

# INITIAL SETUP

parser = argparse.ArgumentParser(
    description = 'Run the locator on an event')
parser.add_argument('evid',
    help = 'comcat event ID OR inputfile (GeoJSON FeatureCollection)')
parser.add_argument('--iterations',
    type = int,
    metavar = 'n',
    help = 'run n iterations (0 = run until done)',
    default = 0)
parser.add_argument('--interval',
    type = int,
    metavar = 't',
    help = 'run iterations every t seconds (default 60)',
    default = 60)
parser.add_argument('--ptdiff',
    type = int,
    metavar = 'n',
    help = "skip unless there's n+ new points since last run (default 5)",
    default = 5)
parser.add_argument('--maxtime',
    type = int,
    metavar = 't',
    help = 'stop t seconds after first entry (default 1200)',
    default = 60 * 20)
parser.add_argument('--utmspan',
    type = int,
    metavar = 'n',
    help = 'Size of geocoded boxes in km (default 1)',
    default = 1)
parser.add_argument('--outputfile',
    type = str,
    metavar = 's',
    help = 'output file (default is "output/out.[evid].geojson")')

try:
    args = parser.parse_args()
except:
    print('Exiting...')
    sys.exit()
    
if args.iterations: 
    print('Running %i iterations.' % (args.iterations))
else:
    print('Running through all entries.')
    args.iterations

evid = args.evid
if 'geojson' in evid:
    infile = evid
    evid = os.path.basename(evid).split('.')[-2]
else:
    infile = './input/' + evid + '.geojson'

data = geojson.load(open(infile))

outfilename = 'output/out.' + evid + '.geojson'
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
all_npts = len(allpts)
print('Finished loading, got %i pts.' % all_npts)

solutions = [ evdata ]

# Now loop over each time interval, figure out which subset
# of observations to run in that interval, and run the locator 
           
def main():

    lastrun_npts = 0    # Number of points of last run
    iterations = 0      # Number of iterations of locator algorithm
    t = 0               # Now computing location for first t seconds of event

    while (lastrun_npts < all_npts and (args.maxtime == 0 or t < args.maxtime)):
        t += args.interval
    
        # Create a new datapts that only has the entries in the time window
        
        this_pts = [ pt for pt in allpts if pt['properties']['t'] <= t ]
        this_npts = len(this_pts)
        if this_npts <= lastrun_npts + args.ptdiff: continue
    
        iterations += 1
        print('%i: Running otime + %i mins (%i entries in %i locations)...' %
            (iterations,t/60,this_npts,len(this_pts)))
        locateAndSave(this_pts,t)

        lastrun_npts = this_npts
        if args.iterations and iterations >= args.iterations: break

    # Add one more solution with ALL entries

    locateAndSave(allpts,args.maxtime + args.interval)
    print(solutions)
    print('Done.')


def locateAndSave(raw_pts,t):

    aggregated_pts = aggregate.aggregate(raw_pts,args.utmspan)
    result = locate_dyfi.locate(aggregated_pts)
    
    # Copy solution grid and ipe line to leaflet output

    webtddir = 'leaflet/data/timedependent/' + evid;
    os.makedirs(webtddir,exist_ok=True)
    webgridfile = webtddir + '/grid.' + str(t) + '.geojson'
    copyfile(tmpgridfile,webgridfile)    
    webgridfile = webtddir + '/ipeline.' + str(t) + '.geojson'
    copyfile(tmpipefile,webgridfile)    

    # Now aggregated_pts should have additional data (distance, mag, etc.)
    # from the locate function
    # Save responses (with results) and copy to leaflet output
 
    responsesfilename = 'output/responses.' + evid + '.geojson'   
    print('Writing to ' + responsesfilename)
    responsesgeojson = geojson.FeatureCollection(aggregated_pts)
    with open(responsesfilename, 'w') as outfile:
        geojson.dump(responsesgeojson, outfile)

    webfilename = 'leaflet/data/aggregated.' + evid + '.geojson'
    copyfile(responsesfilename,webfilename)
    webfilename = webtddir + '/responses.' + str(t) + '.geojson'
    copyfile(responsesfilename,webfilename)
    
    # Save this solution

    result['properties']['t'] = t
    result['properties']['npts'] = len(raw_pts)
    solutions.append(result)
    print('Result: ',result)

    # Overwrite the solutions output file at each step. It should be 
    # usable even if processing is interrupted.

    allgeojson = { 'type': 'FeatureCollection', 'features' : solutions }
    
    print('Writing to ' + outfilename)
    with open(outfilename, 'w') as outfile:
        geojson.dump(allgeojson, outfile)

    webfilename = 'leaflet/data/out.' + evid + '.geojson'
    copyfile(outfilename,webfilename)



# Now execute

main()

