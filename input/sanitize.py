#!/anaconda/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 19 13:16:52 2016

@author: vinceq

Sanitize GeoJSON with inadvertent strings instead of float numbers
"""

import argparse
import json
import geojson

number_props = [ 'confidence','damage','felt','furniture','motion','picture',
                'reaction','shelf','stand','subid','t','user_cdi',
                'mag' ]

parser = argparse.ArgumentParser()
parser.add_argument('file')

args = parser.parse_args()
data = json.load(open(args.file))

features = []
f = data['features']
for pt in f:
    coords = pt['geometry']['coordinates']
    p = pt['properties']
    lat = float(coords[0])
    lon = float(coords[1])
    if 'subid' in p : id = p['subid']
    else : id = 0
    
    props = []
    for key in p:
        if key in number_props:
            val = p[key]
            # print(key + ':' + val)
            if val is None : continue
            if isinstance(val,(int,float)) : continue
            if '.' in val:
                nval = float(val)
            elif val == '':
                nval = None
            else:
                nval = int(val)
            p[key] = nval

    feature = geojson.Feature(
        geometry = geojson.Point((lon,lat)),
        properties = p,
        id = id
    )
    features.append(feature)
    
allgeojson = geojson.FeatureCollection(features)    

with open('out.geojson', 'w') as outfile:
    geojson.dump(allgeojson, outfile)


