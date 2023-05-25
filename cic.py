#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""die schnitstelle zum CIC"""

import websocket
import time


class cic():
    def __init__(self):
        self.ws = websocket.WebSocket()
    
    def connect(self):
        self.ws.connect("ws://echo.websocket.events")
        self.ws.send("Hello, Server")
        print(ws.recv())
        self.ws.close()

    def coordinate_translation(self,lat,long):
        """translates coordinates from GPS-format to the special CIC format"""
        pass



if __name__ == "__main__":
    print("testing connection")
    cic=cic()
    cic.connect()
    
    print("finished")