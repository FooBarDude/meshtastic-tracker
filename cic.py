#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np

from protocol import RldNodeMessage, Request
from uuid import uuid4
from protocol.protocol import SetTrackerRequest
from websocket import WsClient

"""die schnitstelle zum CIC"""


class Cic():
    def __init__(self):
        self.origin = {"lat": 52.382864, "lon": 11.818967}
        self.scaler = np.cos(self.origin["lat"] * np.pi / 180) * 111300

        self.ws_client = WsClient("ws://echo.websocket.events")
    
    def connect(self):
        self.ws_client.start()
        
    def close_connection(self):
        self.ws_client.close()

    def coordinate_translation(self, lat, lon):
        """translates coordinates from GPS-format to the special CIC format"""
        y = (self.origin["lat"] - lat) * 111300
        x = (lon - self.origin["lon"]) * self.scaler
        return x, y

    def position_distortion(self,x,y):
        #in Ingame logic the position sholdnt be as precice as it is from the GPS. this function adds a random distortion (dependent on the distance) to the position
        pass

    def send_coordinate(self, lat, lon, tracker_id):
        x, y = self.coordinate_translation(lat, lon)
        msg = RldNodeMessage(id=str(uuid4()))
        msg.request = SetTrackerRequest()
        msg.request.tracker.id = tracker_id
        msg.request.tracker.postion.x = x
        msg.request.tracker.postion.y = y

        self.ws_client.emit("msg", msg.to_json())
    
    def onRecive_coordinate(self):
        #the cic can also send coordinates from other systems. 
        pass
    
    def send_ping(self,tracker_id):
        #an idea is to fit the trackers with a button to send a "ping" to get the attention of a cic opperator
        pass

if __name__ == "__main__":
    print("testing connection")
    cic=Cic()
    cic.connect()
    cic.send_coordinate(lat=52.37604, lon=11.81999, tracker_id=0)
    cic.send_ping(tracker_id=0)
    cic.close_connection()
    print("finished")