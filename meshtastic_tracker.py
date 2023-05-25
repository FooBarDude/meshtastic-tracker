#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""a programm to track mestastic nodes"""

import radio
import mapping


import time



if __name__ == "__main__":
    print("started")
    m=mapping.mapping()
    r=radio.radio(map=m,debugging=False)
    
    
    #--show the map--
    m.open_map()
    
    #prevent the programm from finishing, so that printouts are visible
    for nr in range(60*24):
        
        #r.ping_device(device_id=1234) #ping a device regularly
        
        if nr%5==0:
            print("running for",nr,"minutes")
        
        time.sleep(60)


#TODO: implement reconnect procedures in case the connection is lost
