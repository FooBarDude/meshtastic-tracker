#!/usr/bin/env python
# -*- coding: utf-8 -*-
from websocket import WsClient

"""die schnitstelle zum CIC"""

import numpy as np

class cic():
    def __init__(self):
        self.origin = {"lat": 52.382864, "lon": 11.818967}
        self.scaler = np.cos(self.origin["lat"] * np.pi / 180) * 111300

        self.ws_client = WsClient("ws://echo.websocket.events")
    
    def connect(self):
        self.ws_client.start()
        
    # def close_connection(self):
    #     self.ws_client.

    def coordinate_translation(self, lat, lon):
        """translates coordinates from GPS-format to the special CIC format"""
        y = (self.origin["lat"] - lat) * 111300
        x = (lon - self.origin["lon"]) * self.scaler
        return x, y

    def position_distortion(self,x,y):
        #in Ingame logic the position sholdnt be as precice as it is from the GPS. this function adds a random distortion (dependent on the distance) to the position
        pass

    def send_coordinate(self,x,y,tracker_id,freund_feind):
        #potional parameters? precicion, timestamp
        pass
    
    def onRecive_coordinate(self):
        #the cic can also send coordinates from other systems. 
        pass
    
    def send_ping(self,tracker_id):
        #an idea is to fit the trackers with a button to send a "ping" to get the attention of a cic opperator
        pass

if __name__ == "__main__":
    print("testing connection")
    cic=cic()
    cic.connect()
    x,y=cic.send_coordinate(lat=52.37604,long=11.81999)#should be arround 0/0 of the CIC grid system
    cic.send_coordinate(x,y,tracker_id=0)
    cic.send_ping(tracker_id=0)
    cic.close()
    print("finished")