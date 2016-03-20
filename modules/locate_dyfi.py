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

# TODO: Make these parameters configurable

PRECISION = 4
xgridrange = range(-200,210,10)          # search grid in km
ygridrange = range(-200,210,10)          # search grid in km
magrange = [ x*0.1 for x in range(18,71) ]   # search parameters for magnitude

def locate(pts):
    """
    Iterate over observations to determine best location
    Returns GeoJSON Feature: epicenter with mag, resid
    
    Arguments:    
    pts: geojson feature collection (list of GeoJSON points)
    """

    counter = 0
    initloc = getStartingPt(pts)
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
            if counter % 100 == 0:
                print('%i: Best loc: (%i,%i)' % 
                    (counter,bestloc['properties']['ix'],
                     bestloc['properties']['iy'])
                 )

            tryloc = getOffsetPt(initloc,ix,iy)
            result = trylocation(tryloc,pts)
            
            mag = result['mag']
            resid = result['resid']
            props = {'mag' : mag,'resid' : resid, 'ix': ix, 'iy' : iy }
            loc = Feature(geometry=tryloc,properties=props)
            saveresults.append(loc)
            if (resid < bestresid):
                bestresid = resid
                bestloc = loc

    tmpfilename = 'tmp/solutiongrid.geojson'
    allgeojson = { 'type' : 'FeatureCollection', 'features' : saveresults }
    with open(tmpfilename,'w') as outfile:
        json.dump(allgeojson,outfile)
    return bestloc
                
def getStartingPt(pts):
    """
    Find best location from observations (i.e. highest intensity)
    Returns GeoJSON point

    Arguments:
    pts: geojson feature collection (list of GeoJSON points)
    """
    
    maxcdi = 0.0
    bestpt = 0
    for pt in pts:
        cdi = pt['properties']['user_cdi']
        if cdi > maxcdi:
            cdi = maxcdi
            bestpt = pt
            
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
    firstrun = True
    for trymag in magrange:    
        # If this is the first run, recalculate distances and weights
        if firstrun:
            getDistancesWts(pts,loc)
            firstrun = False
            
        # Now iterate through each point and add up the resids
        totalresid2 = 0     # Cumulative total of squared resids
        totalwt2 = 0        # Cumulative total of squared weights
        for pt in pts:
            # Todo: Implement this as Point object property            
            ii = pt['properties']['user_cdi']
            dist = pt['properties']['_dist']
            tryii = ipe(trymag,dist,False)
            
            wt = pt['properties']['_wt']
            totalresid2 += (wt*(ii - tryii))**2
            totalwt2 += wt**2

        totalresid2 /= totalwt2
        if totalresid2 < bestresid2:
            bestmag = trymag
            bestresid2 = totalresid2
            
    resid = round(math.sqrt(bestresid2),PRECISION)
    results = { 'mag': bestmag, 'resid' : resid }
    return results
 
def trylocation_B(loc,pts):
    """
    This implements BW1997 calculating residuals of magnitude
    Given a trial epicenter, calculate best magnitude and residual
    Result is the best value for this trial location
    returns [ 'mag' : best magnitude, 'resid' : lowest residual ]
        
    Arguments:
    pts    GeoJSON feature collection (list of GeoJSON points)
    loc    GeoJSON point (dict)
    """
    
    getDistancesWts(pts,loc)

    totalmag = 0
    totalresid2 = 0     # Cumulative total of squared resids
    totalwt = 0
    totalwt2 = 0        # Cumulative total of squared weights

    # First iterate through each point and calculate the estimated mag
    # for each observation
    for pt in pts:
        # Todo: Implement this as Point object property            
        ii = pt['properties']['user_cdi']
        dist = pt['properties']['_dist']
        trymag = ipe(ii,dist,True)

        wt = pt['properties']['_wt']
        pt['properties']['_mag'] = trymag        
        totalmag += wt*trymag
        totalwt += wt
        totalwt2 += wt**2

    meanmag = totalmag/totalwt
    # Now calculate the magnitude residual
    for pt in pts:
        wt = pt['properties']['_wt']
        mag = pt['properties']['_mag']
        resid2 = wt * (meanmag - mag)**2
        totalresid2 += resid2
    
    resid = math.sqrt(totalresid2 / totalwt2)
    results = { 'mag': round(meanmag,1), 'resid' : round(resid,PRECISION) }
    return results
       
def getDistancesWts(pts,loc):
    """
    Iterate through all observations and calculate distance to loc
    Also calculates distance-based weight (see BW1997)
    Returns number of points calculated
    Weight is modified by nresp (when event entries are geocoded)
    
    Arguments:
    pts    geojson feature collection (list of GeoJSON points)
    loc    geojson point (dict)
    """
    
    counter = 0    
    lat0 = loc['coordinates'][1]
    lon0 = loc['coordinates'][0]
    
    for pt in pts:
        lat1 = pt['geometry']['coordinates'][1]
        lon1 = pt['geometry']['coordinates'][0]
        dist = great_circle((lat0,lon0),(lat1,lon1)).kilometers
        if dist >= 150:
            wt = 0.1
        else:
            wt = 0.1 + math.cos(math.pi/2*dist/150)

        try:
            nresp = pt['properties']['nresp']
            if nresp > 0: wt *= nresp
        except KeyError: pass

        dist = round(dist,PRECISION)
        wt = round(wt,PRECISION)
        pt['properties']['_dist'] = dist
        pt['properties']['_wt'] = wt        
        counter += 1

    return(counter)

