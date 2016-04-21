#! /usr/local/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 10 17:51:20 2016

@author: vinceq

Given a list of geojson points, iterate over them and determine
the best location

Ver. A: Compute residuals of intensity (previous Locator algorithm)
Ver. B: Compute residuals of magnitude (conforms to B&W algorithm)

"""

import math
import json
from geojson import Point,Feature
from geopy.distance import great_circle

from modules import ipes

# Resid type A = residuals of intensities at each observation
# Resid type B = residuals of magnitudes at each observation
RESID_TYPE = 'B'

STARTING_PT_TYPE = 'simple'

FILTERBYLOC = ''

# TODO: Make these parameters configurable

PRECISION = 4
magrange = [ x*0.1 for x in range(18,71) ]   # search parameters for magnitude

IPEDISTS = [ x*0.1 for x in range(1,100)] + list(range(10,100)) + list(range(100,310,10))
GRIDSTEP_INIT = 50
GRIDSTEP_FINAL = 5
#TRYLOCATIONF = 0

def locate(initloc,obs):
    """
    Iterate over observations to determine best location
    Returns GeoJSON Feature: epicenter with mag, resid
    
    Arguments:    
    obs: geojson feature collection (list of GeoJSON points)
    """

    if STARTING_PT_TYPE == 'mean':
        getStartingPt = getStartingPt_mean
    else:
        getStartingPt = getStartingPt_simple

    ipe = chooseIpe(initloc)
    initloc = getStartingPt(obs)
    bestloc = initloc
    saveresults = []

    # Also run a sanity check on locations

    obs = filterObs(obs)
    print('After filtering, left with ' + str(len(obs)) + ' locs.')
    initloc = getStartingPt(obs)

    print(initloc)
    global TRYLOCATIONF
    if RESID_TYPE == 'A':
        TRYLOCATIONF = trylocation_A
    else:
        TRYLOCATIONF = trylocation_B

    initloc = loopGrid(ipe,initloc,obs,GRIDSTEP_INIT,saveresults)
    bestloc = loopGrid(ipe,initloc,obs,GRIDSTEP_FINAL,saveresults)

     # Now we have min(residuals) == rms0[MI-Mi]
    # Calculate rmsMI = rms[MI] = rms[MI-Mi] - rms0 for each trial epicenter

    print(bestloc)
    bestresid = bestloc['properties']['resid']
    for trialloc in saveresults:
        p = trialloc['properties']
        p['rmsMI'] = p['resid'] - bestresid

    # Recalculate distances in each observation (this will get saved later)
    # And get a line of points for plotting

    getDistancesWts(bestloc['geometry'],obs)
    bestmag = bestloc['properties']['mag']
    ipeline = getipeline(ipe,bestmag,IPEDISTS)

    # Save the trial grid and ipe for this set of observations

    tmpfilename = 'tmp/solutiongrid.geojson'
    allgeojson = { 'type' : 'FeatureCollection', 'features' : saveresults }
    with open(tmpfilename,'w') as outfile:
        json.dump(allgeojson,outfile)

    tmpfilename = 'tmp/ipeline.json'
    with open(tmpfilename,'w') as outfile:
        json.dump(ipeline,outfile)

    # Return the best trial epicenter

    return bestloc

def loopGrid(ipe,initloc,obs,gridstep,saveresults):

    counter = 0
    bestloc = initloc
    print('Bestloc is:')
    print(bestloc)
    bestresid = 9999

    xgridrange = [ x * gridstep for x in range(-10,11) ]
    ygridrange = [ x * gridstep for x in range(-10,11) ]
    for ix in xgridrange:
        for iy in ygridrange:
            counter += 1
            p = bestloc['properties']
            if counter % 100 == 0:
                print('%i: Best loc: (%i,%i)' % 
                    (counter,p['ix'],p['iy']))

            tryloc = getOffsetPt(initloc,ix,iy)

            # Calculate distances and weights only once per trial epicenter
            getDistancesWts(tryloc,obs)
            
            # Now calculate the magnitude and residual for this trial
            # epicenter by iterating through each observation
            result = TRYLOCATIONF(ipe,obs)
            resid = result['resid']
            props = {
                'mag' : result['mag'],
                'resid' : resid, 
                'ix': ix, 'iy' : iy 
            }
            loc = Feature(geometry=tryloc,properties=props)
            saveresults.append(loc)

            # Keep track of the best trial epicenter
            if (resid < bestresid):
                bestresid = resid
                bestloc = loc

    return bestloc
                
def getStartingPt_simple(pts):
    """
    Find best location from observations (i.e. highest intensity)
    Returns GeoJSON point

    Arguments:
    pts: geojson feature collection (list of GeoJSON points)
    """
    
    maxcdi = 0.0
    bestpt = 0
    for pt in pts:
        cdi = pt['properties']['cdi']
        if cdi > maxcdi:
            maxcdi = cdi
            bestpt = pt
            print('Best starting cdi: ' + str(cdi))
            print(bestpt['properties'])
            
    return bestpt

def getOffsetPt(initloc,ix,iy):
    """
    Get longitude/latitude from epicenter and x/y offset (in km)
    Returns GeoJSON point
    
    Arguments:
    initloc     initial point in GeoJSON format (dict)
    ix          x-offset in km (positive is East)
    iy          y-offset in km (positive is North)
    """
    
    lat0 = initloc['geometry']['coordinates'][1]
    lon0 = initloc['geometry']['coordinates'][0]
    lat = lat0 + (iy / 111.12)
    lon = lon0 + (ix / 111.12) * math.cos(lat * 0.0174532925);
    lat = round(lat,PRECISION)
    lon = round(lon,PRECISION)
    result = Point((lon,lat))
    return result
    
def trylocation_A(ipe,pts):
    """
    This implements BW1997 but calculating residuals of intensity
    Given a trial epicenter, calculate best magnitude and residual
    Result is the best value for this trial location
    returns [ 'mag' : best magnitude, 'resid' : lowest residual ]
        
    Arguments:
    pts    GeoJSON feature collection (list of GeoJSON points)
    loc    GeoJSON point (dict)
    """
    
    bestresid2 = 9999       # Best squared resid so far
    bestmag = 0             # Best mag so far

    for trymag in magrange:    
        # Now iterate through each point and add up the resids
        totalresid2 = 0     # Cumulative total of squared resids
        totalwt2 = 0        # Cumulative total of squared weights
        for pt in pts:
            # Todo: Implement this as Point object property            
            ii = pt['properties']['cdi']
            dist = pt['properties']['_dist']
            tryii = ipe(trymag,dist,False)
            
            wt = pt['properties']['_wt']
            totalresid2 += wt*(ii - tryii)**2
            totalwt2 += wt**2

        totalresid2 /= totalwt2
        if totalresid2 < bestresid2:
            bestmag = trymag
            bestresid2 = totalresid2
            
    resid = round(math.sqrt(bestresid2),PRECISION)
    results = { 'mag': bestmag, 'resid' : resid }
    return results
 
def trylocation_B(ipe,obs):
    """
    This implements BW1997 calculating residuals of magnitude
    Given a trial epicenter, calculate best magnitude and residual
    Result is the best value for this trial location
    returns [ 'mag' : best magnitude, 'resid' : lowest residual ]
        
    Arguments:
    trialloc    GeoJSON point (dict)
    obs         GeoJSON feature collection (list of GeoJSON points)
    """
    

    # First iterate through each point and calculate the estimated mag
    # for each observation

    totalmag = 0
    totalwt = 0
    for ob in obs:
        # Todo: Implement this as Point object property            
        ii = ob['properties']['cdi']
        dist = ob['properties']['_dist']

        trymag = ipe(ii,dist,True)
        ob['properties']['_mag'] = trymag        
        #nresp = ob['properties']['nresp']
        totalmag += trymag
        totalwt +=  1

    # Calculate the mean of M derived from observations
    # This is the M assigned to that trial epicenter
    meanmag = totalmag/totalwt


    # Residual at this trial epicenter := rms[ MI - Mi ] 
    #   = sqrt( sum( (wt*(MI-Mi))**2 ) / sum(wt**2) )
    #   where   Mi = M derived from the ith observation
    #           MI = mean(Mi)
    # This quantifies how well this trial magnitude fits
    # the observations (weighted by distance of the obs)

    totalresid2 = 0
    totalwt2 = 0
    for ob in obs:
        wt = ob['properties']['_wt']
        thismag = ob['properties']['_mag']
        totalresid2 += (wt * (thismag - meanmag))**2
        totalwt2 += wt**2

    resid = math.sqrt(totalresid2 / totalwt2)
    results = { 
        'mag': round(meanmag,1), 
        'resid' : round(resid,PRECISION) 
    }
    return results
       
def getDistancesWts(trialloc,pts):
    """
    Iterate through all observations and calculate distance to trialloc
    Also calculates distance-based weight (see BW1997)
    Returns number of points calculated
    Weight is NOT modified by nresp 
    
    Arguments:
    trialloc    geojson point (dict)
    pts         geojson feature collection (list of GeoJSON points)
    """
    
    counter = 0    
    lat0 = trialloc['coordinates'][1]
    lon0 = trialloc['coordinates'][0]
    
    for pt in pts:
        lat1 = pt['geometry']['coordinates'][1]
        lon1 = pt['geometry']['coordinates'][0]
        dist = great_circle((lat0,lon0),(lat1,lon1)).kilometers
        
        if dist >= 150:
            wt = 0.1
        else:
            wt = 0.1 + math.cos(math.pi/2*dist/150)
#        try:
#            nresp = pt['properties']['nresp']
#            if nresp > 0: wt *= nresp
#        except KeyError: pass

        dist = round(dist,PRECISION)
        wt = round(wt,PRECISION)
        pt['properties']['_dist'] = dist
        pt['properties']['_wt'] = wt        
        counter += 1

    return(counter)

def getStartingPt_mean(pts):
    """
    Find best location from observations. This will attempt to find
    the median centroid of all observations weighted by intensity
    (higher intensities are more important).
    
    NOTE: This will also modify xgridrange and ygridrange values.
    
    Returns GeoJSON point

    Arguments:
    pts: geojson feature collection (list of GeoJSON points)
    """
    
    maxcdi = 0.0
    startpt = 0
    for pt in pts:
        cdi = pt['properties']['cdi']
        if cdi > maxcdi:
            maxcdi = cdi
            bestpt = pt

    print('Now bestpt is:')
    print(bestpt)
    startpt = bestpt

    for pt in pts:
        if pt == startpt: continue
        bestpt = addpts(bestpt,pt,cdiwt(cdi))
            
    print('Best starting point:')
    print(bestpt)
    return bestpt

def cdiwt(cdi):
#    if cdi >= 9: return 1
#    if cdi <= 1: return 0
    return cdi/10

def addpts(pt1,pt2,wt):
    lat1 = pt1['geometry']['coordinates'][1]
    lat2 = pt2['geometry']['coordinates'][1]
    
    lon1 = pt1['geometry']['coordinates'][0]
    lon2 = pt2['geometry']['coordinates'][0]

    newlat = (lat1 * (1-wt)) + lat2*wt
    newlon = (lon1 * (1-wt)) + lon2*wt
    
    newpt = Feature(geometry=Point((newlon,newlat)))
    return newpt

def getipeline(ipe,mag,dists):
    metadata = {
        'name' : ipe.name,
        'mag' : mag
    }
    values = []
    for dist in dists:
        ii = ipe(mag,dist,False)
        if ii < 2: continue
        ii = round(ii,2)
        values.append({ 'x':dist, 'y':ii})
    
    return { 'metadata' : metadata, 'values' : values }

def chooseIpe(loc):
    global FILTERBYLOC
    print(loc)
    lon = loc['geometry']['coordinates'][0]
    print('Got lon:' + str(lon))
    print(loc)
    if lon < -114: 
        ipe = ipes.aww2014wna
        FILTERBYLOC = filterLocWna
    else:
        ipe = ipes.aww2014ena
        FILTERBYLOC = filterLocEna

    print('Using ' + ipe.name)
    return ipe

def filterLocWna(loc):
    lat = loc['geometry']['coordinates'][1]
    lon = loc['geometry']['coordinates'][0]
    
    if lat > 42 or lat < 30: return
    if lon < -124.5 or lon > -112.5: return

    return True
    
def filterLocEna(loc):
    lat = loc['geometry']['coordinates'][1]
    lon = loc['geometry']['coordinates'][0]
    
    if lat > 38 or lat < 32: return
    if lon < -102 or lon > -93: return

    return True
    
def filterObs(obs):
    newobs = []
    for ob in obs:        
        if FILTERBYLOC(ob):
            newobs.append(ob)
        else:
            pass

    return newobs
    