# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 21:08:39 2016

@author: vinceq

cdi.py :  Take a list of points, combine indices, and calculate CDI

"""

import math

cdiIndices = {'felt':5,'motion':1,'reaction':1,'stand':2,
              'shelf':5,'picture':2,'furniture':3,'damage':5}

def calculate(pts):

    byindex = {} 
    
    for index in cdiIndices:
        total  = 0
        num = 0
        for pt in pts:
            p = pt['properties']
            if index not in p: continue
            if p[index] is None: continue
            total += p[index]
            num += 1
        
        if num: byindex[index] = total/num

    # Now byindex has average of each index
    cws = 0
    for index in byindex:
        cws += byindex[index] * cdiIndices[index]

    if cws <= 0 : return 1

    cdi = math.log(cws) * 3.3996 - 4.3781
    if cdi < 2 : return 2
    return round(cdi,1)

