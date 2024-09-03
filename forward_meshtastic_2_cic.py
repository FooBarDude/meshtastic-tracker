#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""this is intended to be run on a raspberry Pi and continiously forward the mesh packages to the CIC"""

import radio
import cic

import time



if __name__ == "__main__":
    print("started")
    cic=cic.Cic()
    r=radio.radio(map=None,debugging=False,cic=cic)
    
    #prevent the programm from finishing, so that printouts are visible
    nr=0
    while True:
        
        if nr%5==0:
            print("running for",nr,"minutes")
        
        time.sleep(60)
        nr+=1


