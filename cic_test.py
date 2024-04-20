#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""die schnitstelle zum CIC testen"""

import cic
import mapping

import time


class tests():
    def __init__(self):
        self.cic=cic.Cic()
    
    def connection(self):
        """only test connection without generating any tracks"""
        self.cic.connect()
        
    def walk_in_square(self):
        print("!!! generating  path for testing !!!")
        
        self.cic.connect()
        m=mapping.mapping()
        
        #start-position--
        nr_of_trackers=1
        tracker_id=35
        scaling=0.0005
        pos_list=[]
        for nr in range(nr_of_trackers):
            pos_list.append({"latitude1":52.37604,"longitudel":11.81999}) #koordinaten um den Prim koordinaten nullpunkt rum
        
        #--make faster update-- (folium seems to crash, when the file is reloaded and witen at the same time, so reloding more often makes crashes more likely)
        m.update_every=10
        
        m.create_map()
        m.open_map()
        
        for tick in range(100):
            print("Step nr",tick,tick%4)
            for nr in range(nr_of_trackers):
                if tick%4==0:
                    pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+scaling
                    pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+0
                elif tick%4==1:
                    pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+0
                    pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+scaling
                elif tick%4==2:
                    pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]-scaling
                    pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+0
                elif tick%4==3:
                    pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+0
                    pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]-scaling
                else:
                    print("thats not supposed to happen")
                position_dict1={"device_id":nr,"latitude":pos_list[nr]["latitude1"],"longitude":pos_list[nr]["longitudel"],"gps_time":tick,"gps_date":1}
                m.update_position(position_dict1)
                m.draw_path(position_dict1)
                self.cic.send_coordinate(pos_list[nr]["latitude1"],pos_list[nr]["longitudel"],tracker_id)
            m.draw_map()
            if tick%3==0:
                m.recreate_map()
            time.sleep(5)


if __name__ == "__main__":
    print("cic_test.py started")
    t=tests()
    print("1: only connect to cic")
    print("2: generata a tracker that walks in a square")
    reply=input("start witch test?:")
    if int(reply)==1:
        t.connection()
    elif int(reply)==2:
        t.walk_in_square()
    elif int(reply)==3:
        print("not implemented yet")
    else:
        print("unknown test")
        
    print("test ended")



