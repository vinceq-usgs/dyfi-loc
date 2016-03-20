# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 21:08:39 2016

@author: vinceq

aggreagate_utm.py :  Module to take GeoJSON feature collection and return
                    geocoded GeoJSON

"""

import math
import geojson
from modules.utm import from_latlon,to_latlon
from modules import cdi

def aggregate(pts,resolution):
    """
    Iterate through GeoJSON feature collection
    Returns GeoJSON feature collection of UTM boxes (polygons)
    with properties:
        utm     UTM code with correct precision
        lat     center coordinate
        lon     center coordinate
        nresp   number of responses contributing
        cdi     aggregated intensity
        
    Arguments:
    pts             GeoJSON feature collection
    resolution      size of geocoding box in km (optional, default 1km)
    """
    resolutionMeters = resolution * 1000
    npts = len(pts)
    print('Got ' + str(npts) + ' points this iteration.')
    print('Calculating UTM coordinates:')
    for pt in pts:
        loc = getAggregation(pt,resolutionMeters)
        if not loc: continue
        pt['properties']['loc'] = loc
                
    rawresults = {}
    print('Aggregating points:')
    for pt in pts:
        if not pt['properties']['loc']: continue
        loc = pt['properties']['loc']
        if loc in rawresults:
            rawresults[loc].append(pt)
        else:
            rawresults[loc] = [pt]
            
    results = []
    for loc,pts in rawresults.items():
        # print('Loc ' + loc + ' has ' + str(len(pts)) + ' results.')

        user_cdi = cdi.calculate(pts)
        # geom = getBoundingPolygon(loc,resolutionMeters)        
        coords = getCoords(loc,resolutionMeters)
        props = {
            'user_cdi' : user_cdi,
            'nresp' : len(pts)
        }
        pt = geojson.Feature(
            geometry=geojson.Point(coords),
            properties=props,
            id=loc
        )
        results.append(pt)

    print('Aggregated %i pts into %i pts' % (npts,len(results)))
    return results

def myFloor(x,multiple):
    """ 
    Emulates the math.floor function but
    rounding down to different digits (i.e. 1000 or 10000 meters)

    Returns integer
    Arguments: 
        x       original value
        multiple   which digit to round to (1000 or 10000)

    """
    
    y = x/multiple
    return int(math.floor(y) * multiple)

def myCeil(x,multiple):
    return int(math.ceil(x/multiple) * multiple)

def getAggregation(pt,digit):
    geom = pt['geometry']['coordinates']
    lat = geom[1]
    lon = geom[0]
    loc = from_latlon(lat,lon)
    if not loc: return

    x,y,zonenum,zoneletter = loc
    x0 = myFloor(x,digit)
    y0 = myFloor(y,digit)
    loc = '{} {} {} {}'.format(x0,y0,zonenum,zoneletter)
    return loc
    
def getCoords(loc,resolutionMeters):
    """
    Returns a Point object of the center of the UTM location
    
    """
    x,y,zone,zoneletter = loc.split()
    x = int(x) + resolutionMeters/2
    y = int(y) + resolutionMeters/2
    zone = int(zone)
    lat,lon = to_latlon(x,y,zone,zoneletter)
    return (lon,lat)

    