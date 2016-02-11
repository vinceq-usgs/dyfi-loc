#! /usr/local/bin/python3

"""
Given an event, run the locator continuously every 3 minutes 
until all locations are used.

"""

import argparse
import sys
import json
import locate_dyfi

# INITIAL SETUP

# TODO: Make these variables into CLI arguments
T_INTERVAL = 60
MIN_PTS_DIFF = 5
T_MAX = 60 * 20

parser = argparse.ArgumentParser(
    description = 'Run the locator on an event')
parser.add_argument('infile',
                    help = 'inputfile (must be mysqldump)')

parser.add_argument('--iterations',
                    type=int,
                   help = 'optional number of iterations',
                   default=0)

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

while (lastrun_npts < npts and t < T_MAX):
    t += T_INTERVAL

    # Create a new datapts that only has the entries in the time window
    
    this_pts = [ pt for pt in allpts if pt['properties']['t'] <= t ]
    this_npts = len(this_pts)
    if this_npts <= lastrun_npts + MIN_PTS_DIFF: continue

    iterations += 1
    best_result = False
    print('%i: Running otime + %i mins (%i entries)...' % (iterations,t/60,this_npts))
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


        

