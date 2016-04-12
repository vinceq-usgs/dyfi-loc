#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:51:20 2016

@author: vinceq
"""

import math

C = (0,0.309,1.864,-1.672,-0.00219,1.77,-0.383);

def aww2014wna(mag,r,inverse):
    """
    Implementation of Atkinson, Worden, Wald (2014)
    Returns intensity = f(mag,r)
    
    If inverse is true, returns mag = f(intensity,r)
    """

    
    R = math.sqrt(r**2 + 14**2)
    if R > 50:
        B = 0
    elif R<1:
        B = math.log(1/50,10)
    else:
        B = math.log(R/50,10)
                    
    logr = math.log(R,10) if R > 1 else 0
    
    if inverse:
        # For inverse problem, input is intensity, output is mag
        ii = mag
        mag = (ii - C[1] - C[3]*logr - C[4]*R - C[5]*B) / (C[2] + C[6]*logr) 
        return mag
    
    mlogr = mag * logr
    ii = C[1] + C[2]*mag + C[3]*logr + C[4]*R + C[5]*B + C[6]*mlogr
    if ii > 1.0 and ii < 2.0: ii = 2.0
    if ii < 1.0: ii = 1.0
    return ii
    
def aww2014ena(mag,r,inverse):
    """
    Implementation of Atkinson, Worden, Wald (2014)
    Returns intensity = f(mag,r)
    
    If inverse is true, returns mag = f(intensity,r)
    """

    R = math.sqrt(r**2 + 14**2)
    if R > 50:
        B = 0
    elif R<1:
        B = math.log(1/50,10)
    else:
        B = math.log(R/50,10)
                    
    logr = math.log(R,10) if R > 1 else 0

    if r < 1: 
        e1 = 1/50
    else: 
        e1 = min(r,150)/50

    ecorr = 0.7 + 0.001*r + max(0,0.8*math.log(e1))
    
    if inverse:
        # For inverse problem, input is intensity, output is mag
        ii = mag
        mag = (ii - C[1] - ecorr - C[3]*logr - C[4]*R - C[5]*B) / (C[2] + C[6]*logr) 
        return mag
    
    mlogr = mag * logr
    ii = C[1] + C[2]*mag + C[3]*logr + C[4]*R + C[5]*B + C[6]*mlogr
    ii += ecorr

    if ii > 1.0 and ii < 2.0: ii = 2.0
    if ii < 1.0: ii = 1.0
    return ii
    
aww2014wna.name = 'Atkinson, Worden, Wald 2014 (WNA)'
aww2014ena.name = 'Atkinson, Worden, Wald 2014 (ENA)'

 