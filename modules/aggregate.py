# -*- coding: utf-8 -*-

"""
Created on Fri Mar 11 21:08:39 2016

@author: vinceq

aggreagate_utm.py :  Module to take GeoJSON feature collection and return
                    geocoded GeoJSON

"""

import math
import geojson
from modules.utm import from_latlon,to_latlon,OutOfRangeError
from modules import cdi

PRECISION = 4

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
    for pt in pts:
        loc = getAggregation(pt,resolutionMeters)
        if not loc: continue
        pt['properties']['loc'] = loc
                
    rawresults = {}
    earliesttimes = {}
    print('Aggregating points:')
    for pt in pts:
        if 'loc' not in pt['properties']: continue
        loc = pt['properties']['loc']
        t = pt['properties']['t']
        if loc in rawresults:
            rawresults[loc].append(pt)
            if t < earliesttimes[loc]: earliesttimes[loc] = t 
        else:
            rawresults[loc] = [ pt ]
            earliesttimes[loc] = t

            
    results = []
    for loc,pts in rawresults.items():

        intensity = cdi.calculate(pts)
        # geom = getBoundingPolygon(loc,resolutionMeters)        
        coords = getCoords(loc,resolutionMeters)
        props = {
            'cdi' : intensity,
            'nresp' : len(pts),
            't' : earliesttimes[loc]
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
    try: 
        loc = from_latlon(lat,lon)
    except OutOfRangeError:
        return
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
    lat = round(lat,PRECISION)
    lon = round(lon,PRECISION)
    return (lon,lat)

    
