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

ipe = ipes.aww2014
# Resid type A = residuals of intensities at each observation
# Resid type B = residuals of magnitudes at each observation
RESID_TYPE = 'B'

STARTING_PT_TYPE = 'mean'

# TODO: Make these parameters configurable

PRECISION = 4
xgridrange = range(-100,100,5)          # search grid in km
ygridrange = range(-100,100,5)          # search grid in km
magrange = [ x*0.1 for x in range(18,71) ]   # search parameters for magnitude

def locate(obs):
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

    counter = 0
    initloc = getStartingPt(obs)
    bestresid = 9999
    bestloc = initloc
    saveresults = []

    if RESID_TYPE == 'A':
        trylocation = trylocation_A
    else:
        trylocation = trylocation_B
    
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
            result = trylocation(tryloc,obs)
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

    # Now we have min(residuals) == rms0[MI-Mi]
    # Calculate rmsMI = rms[MI] = rms[MI-Mi] - rms0 for each trial epicenter

    for trialloc in saveresults:
        p = trialloc['properties']
        p['rmsMI'] = p['resid'] - bestresid

    # Now we have the best location, recalculate distances in each
    # observation (this will get saved later)

    getDistancesWts(bestloc['geometry'],obs)

    # Save the trial grid for this set of observations

    tmpfilename = 'tmp/solutiongrid.geojson'
    allgeojson = { 'type' : 'FeatureCollection', 'features' : saveresults }
    with open(tmpfilename,'w') as outfile:
        json.dump(allgeojson,outfile)

    # Return the best trial epicenter

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
    
def trylocation_A(loc,pts):
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
 
def trylocation_B(trialloc,obs):
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
            
    # TODO: modify xgridrange, ygridrange by throwing out 10% of
    # outliers
    print('Best starting point:')
    print(bestpt)
    return bestpt

def cdiwt(cdi):
    if cdi >= 9: return 1
    if cdi <= 1: return 0
    return (cdi - 1)/8

def addpts(pt1,pt2,wt):
    lat1 = pt1['geometry']['coordinates'][1]
    lat2 = pt2['geometry']['coordinates'][1]
    
    lon1 = pt1['geometry']['coordinates'][0]
    lon2 = pt2['geometry']['coordinates'][0]

    dist = great_circle((lat1,lon1),(lat2,lon2)).kilometers
 
    newlat = (lat1 * (1-wt/2)) + lat2*wt/2
    newlon = (lon1 * (1-wt/2)) + lon2*wt/2
    
    
    newpt = Feature(geometry=Point((newlon,newlat)))
    return newpt



    