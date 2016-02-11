#! /usr/local/bin/python3

"""
Given a list of geojson points, iterate over them and determine
the best location

"""

import sys
import math
from geojson import Point,Feature
from geopy.distance import great_circle
import copy

import ipes

ipe = ipes.aww2014

# TODO: Make these parameters configurable

xgridrange = range(-100,100,10)          # search grid in km
ygridrange = range(-100,100,10)          # search grid in km
magrange = [ x*0.1 for x in range(18,70) ]   # search parameters for magnitude

def locate(observations):
    """
    Iterate over observations to determine best location
    Returns GeoJSON Feature: epicenter with mag, resid
    
    Arguments:    
    observations: geojson feature collection (list of GeoJSON points)
    """
    
    initloc = find_starting_loc(observations)
    bestresid = 9999
    bestloc = initloc
    for ix in xgridrange:
        for iy in ygridrange:
            tryloc = getPoint(initloc,ix,iy)
            result = trylocation(tryloc,observations)
            mag = result['mag']
            resid = result['resid']
            if (resid < bestresid):
                bestresid = resid
                props = {'mag' : mag,'resid' : resid}
                bestloc = Feature(geometry=tryloc,properties=props)
                
    return bestloc
                
def find_starting_loc(observations):
    """
    Find best location from observations (i.e. highest intensity)
    Returns GeoJSON point

    Arguments:
    observations: geojson feature collection (list of GeoJSON points)
    """
    
    maxcdi = 0.0
    bestpt = 0
    for pt in observations:
        cdi = float(pt['properties']['user_cdi'])
        if cdi > maxcdi:
            cdi = maxcdi
            bestpt = pt
            
    return bestpt

def getPoint(initloc,ix,iy):
    """
    Get longitude/latitude from epicenter and x/y offset (in km)
    Returns GeoJSON point
    
    Arguments:
    initloc     initial point in GeoJSON format (dict)
    ix          x-offset in km (positive is East)
    iy          y-offset in km (positive is North)
    """
    
    # TODO: Implement this as a Point object method
    lat0 = float(initloc['geometry']['coordinates'][1])
    lon0 = float(initloc['geometry']['coordinates'][0])
    lat = lat0 + (iy / 111.12)
    lon = lon0 + (ix / 111.12) * math.cos(lat * 0.0174532925);
    result = Point((lon,lat))
    return result
    
def trylocation(loc,observations):
    """
    Given a trial epicenter, calculate best magnitude and residual
    Returns dict of mag and resid
    
    Arguments:
    observations    geojson feature collection (list of GeoJSON points)
    loc             geojson point (dict)
    """
    
    bestresid = 9999
    bestmag = 0
    firstrun = True
    for trymag in magrange:    
        # If this is the first run, recalculate distances
        if firstrun:
            find_dist(observations,loc)
            firstrun = False
        # Now iterate through each point and add up the resids
        counter = 0
        totalresid = 0            
        for pt in observations:
            # Todo: Implement this as Point object property
            ii = float(pt['properties']['user_cdi'])
            dist = pt['properties']['_dist']
            tryii = ipe(trymag,dist)
            totalresid += (ii - tryii)**2
            counter += 1
            
        if totalresid < bestresid:
            bestmag = trymag
            bestresid = totalresid
            
    bestresid = math.sqrt(bestresid / counter)
    results = { 'mag': bestmag, 'resid' : bestresid }
    return results
        
def find_dist(observations,loc):
    """
    Iterate through all observations and calculate distance to loc
    (Internal function only)
    
    Arguments:
    observations    geojson feature collection (list of GeoJSON points)
    loc             geojson point (dict)
    """
    
    # TODO: Implement this as Point object method
    counter = 0    
    lat0 = loc['coordinates'][1]
    lon0 = loc['coordinates'][0]
    
    for pt in observations:
        lat1 = pt['geometry']['coordinates'][1]
        lon1 = pt['geometry']['coordinates'][0]
        dist = great_circle((lat0,lon0),(lat1,lon1)).kilometers
        pt['properties']['_dist'] = dist
        counter += 1
        
    return(counter)
