#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""die schnitstelle zum CIC testen"""

import cic
import mapping

import time




if __name__ == "__main__":
    print("testing connection")
    cic=cic.Cic()
    #cic.connect()




    print("!!! generating  path for testing !!!")

    m=mapping.mapping()
    
    #start-position--
    nr_of_trackers=1
    scaling=0.0005
    pos_list=[]
    for nr in range(nr_of_trackers):
        pos_list.append({"latitude1":52.37604,"longitudel":11.81999}) #koordinaten um den Prim koordinaten nullpunkt rum
    
    #--make faster update-- (folium seems to crash, when the file is reloaded and witen at the same time, so reloding more often makes crashes more likely)
    m.update_every=10
    
    m.create_map()
    m.open_map()
    
    for tick in range(100):
        print("Step nr",tick)
        for nr in range(nr_of_trackers):
            if tick%4==0:
                print("1")
                pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+scaling
                pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+0
            elif tick%4==1:
                print("2")
                pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+0
                pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+scaling
            elif tick%4==2:
                print("3")
                pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]-scaling
                pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+0
            elif tick%4==3:
                print("3")
                pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+0
                pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]-scaling
            else:
                print("thats not supposed to happen")
            position_dict1={"device_id":nr,"latitude":pos_list[nr]["latitude1"],"longitude":pos_list[nr]["longitudel"],"gps_time":tick,"gps_date":1}
            m.update_position(position_dict1)
            m.draw_path(position_dict1)
        m.draw_map()
        if tick%3==0:
            m.recreate_map()
        time.sleep(5)
