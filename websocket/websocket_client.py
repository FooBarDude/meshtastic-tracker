import tornado.ioloop
import tornado.websocket
import time

from tornado import gen
from threading import Thread

import json

#asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # for windows only 

class WsClient(Thread):

    def __init__(self, url, on_message=None, on_open=None, on_close=None) -> None:
        super().__init__(daemon=True)

        self.ws: tornado.websocket.WebSocketClientConnection = None
        self.connected = False
        self.message_buffer = []
        self.on_message = on_message
        self.on_open = on_open
        self.on_close = on_close
        self.url = url

    def run(self):

        self.ioloop = tornado.ioloop.IOLoop()
        self._connect_ws()
        self.ioloop.start()

    def emit(self, event: str, message):
        if (self.connected):
            self.ws.write_message(json.dumps({"event":event, "data":message}))
        else:
            print("Websocket not connected")

    def close(self):
        if self.ws is not None:
            self.ws.close()

    @gen.coroutine
    def _connect_ws(self):
        try:
            self.ws = yield tornado.websocket.websocket_connect(self.url, callback=self._on_connection, on_message_callback=self._on_message)
        except:
            pass

    def _cleanup(self):
        self.ioloop.remove

    def _on_connection(self, *args):
        if args[0].exception():
            time.sleep(2)
            self._connect_ws()
        else:
            self.connected = True
            self.ioloop.add_callback(self._on_open)

    def _on_open(self):
        if self.on_open:
            self.ioloop.add_callback(self.on_open)

    def _on_message(self, buffer):
        if not buffer:
            self._on_close()
        elif self.on_message:
            try:
                message = json.loads(buffer)
                self.on_message(message['data'])
            except Exception as e:
                return

    def _on_close(self):
        self.connected = False
        
        if self.on_close:
            self.on_close()

        self._connect_ws()