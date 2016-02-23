#! /usr/local/bin/python3

"""
Given an event, run the locator continuously every T_INTERVAL
minutes until all locations are used.

Input is a GeoJSON FeatureCollection of Point Features (individual
DYFI observations). Each Point requires two properties:
 
    'user_cdi'  calculated CDI of that entry
    't'         entry time in seconds past origin time

"""

import argparse
import sys
import json
import locate_dyfi

# INITIAL SETUP

parser = argparse.ArgumentParser(
    description = 'Run the locator on an event')
parser.add_argument('infile',
    help = 'inputfile (must be GeoJSON FeatureCollection)')
parser.add_argument('--iterations',
    type = int,
    metavar = '',
    help = 'run n iterations (0 = run until done)',
    default = 0)
parser.add_argument('--interval',
    type = int,
    metavar = '',
    help = 'run iterations every n seconds',
    default = 60)
parser.add_argument('--ptdiff',
    type = int,
    metavar = '',
    help = "skip unless there's n or more new points since last run",
    default = 5)
parser.add_argument('--maxtime',
    type = int,
    metavar = '',
    help = 'stop n seconds after first entry',
    default = 60 * 20)

try:
    args = parser.parse_args()
except:
    sys.exit()
    
if args.iterations: 
    print('Running %i iterations.' % (args.iterations))
else:
    print('Running through all entries.')
    args.iterations

# DONE INITIAL SETUP

# Load data

data = json.load(open(args.infile))
outfilename = 'out.' + args.infile
allpts = data['features']

# Extract epicenter data

for i in range(0,len(allpts)):
    if 'is_epicenter' in allpts[i]['properties']: break

# Extract epicenter data for checking later
# TODO: If evdata doesn't exist, handle it

evdata = allpts.pop(i)
npts = len(allpts)
print('Finished loading, got %i pts.' % npts)

# Now loop over each time interval, figure out which subset
# of observations to run in that interval, and run the locator 
           
lastrun_npts = 0    # Number of points of last run
iterations = 0      # Number of iterations of locator algorithm
t = 0               # Now computing location for first t seconds of event
allresults=[]

while (lastrun_npts < npts and (args.maxtime == 0 or t < args.maxtime)):
    t += args.interval

    # Create a new datapts that only has the entries in the time window
    
    this_pts = [ pt for pt in allpts if pt['properties']['t'] <= t ]
    this_npts = len(this_pts)
    if this_npts <= lastrun_npts + args.ptdiff: continue

    iterations += 1
    best_result = False
    print('%i: Running otime + %i mins (%i entries)...' %
        (iterations,t/60,this_npts))
    result = locate_dyfi.locate(this_pts)
    
    # TODO: Use GeoJSON property methods for this
    result['properties']['t'] = t
    result['properties']['npts'] = this_npts
    allresults.append(result)
    print('Result: ',result)

    lastrun_npts = this_npts
    if args.iterations and iterations >= args.iterations: lastrun_npts = npts

    # Save each iteration to file just in case we are interrupted

    allgeojson = { 'type': 'FeatureCollection', 'features' : allresults }
    with open(outfilename, 'w') as outfile:
        json.dump(allgeojson, outfile)
        
print(allresults)


        

