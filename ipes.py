#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:51:20 2016

@author: vinceq
"""

import math

c = (0,0.309,1.864,-1.672,-0.00219,1.77,-0.383);

def aww2014(mag,r):
    """
    Implementation of Atkinson, Worden, Wald (2014)
    Returns intensity
    """
    
    b = math.log(r/30,10) if r > 30 else 0
    logr = math.log(r,10) if r > 1 else 0
    mlogr = mag * logr
    
    ii = c[1] + c[2]*mag + c[3]*logr + c[4]*r + c[5]*b + c[6]*mlogr
    return ii
    

 