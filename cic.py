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
        
        #self.ws_client = WsClient("ws://echo.websocket.events")
        self.ws_client = WsClient("ws://yavin-iv.ddnss.de:3100")
    
    def connect(self):
        self.ws_client.start()
        
    def close_connection(self):
        self.ws_client.close()
    
    def coordinate_translation(self, lat, lon):
        """translates coordinates from GPS-format to the special CIC format"""
        y = (self.origin["lat"] - lat) * 111300
        x = (lon - self.origin["lon"]) * self.scaler
        return x, y
    
    def send_coordinate(self, lat, lon, tracker_id):
        x, y = self.coordinate_translation(lat, lon)
        msg = RldNodeMessage()
        msg.id = str(uuid4())
        msg.request = SetTrackerRequest()
        #msg.request.tracker = Tracker()
        
        msg = msg.to_dict()
        #print("msg",msg)
        #msg["request"]["setTracker"] = {"tracker": {"id": tracker_id, "postion": {"x": int(x), "y": int(y)}}}
        msg = {"request": {"setTracker":  {"tracker": {"id": tracker_id, "postion": {"x": int(x), "y": int(y)}}}}}
        
        _msg = RldNodeMessage()
        msg = _msg.from_dict(msg)
        self.ws_client.emit("msg", msg.to_json())
        print("sent position of",tracker_id,"to CIC")
    
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
    cic.send_coordinate(lat=52.376857336038256, lon=11.819297095719259, tracker_id=99)#gebäude 00
    #cic.send_coordinate(lat=52.38149504794789, lon=11.827885017939058, tracker_id=99)#gebäude 43 (tower)
    #cic.send_coordinate(lat=52.38006656850958, lon=11.837442278648139, tracker_id=99)#gebäude X41 Y17 im long range gebiet
    cic.send_ping(tracker_id=99)
    cic.close_connection()
    print("finished")