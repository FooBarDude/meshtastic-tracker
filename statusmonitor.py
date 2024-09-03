#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""a programm to display the current curren mestastic nodes"""

import radio


import time
import datetime


from typing import Any, List

from rich.style import Style

from textual import on
from textual.app import ComposeResult, App
from textual.command import Provider
from textual.screen import ModalScreen, Screen
from textual.widgets import DataTable, Footer, Header

MY_DATA = [
    ("level", "name", "gender", "country", "age"),
    ("Green", "Wai", "M", "MYS", 22),
    ("Red", "Ryoji", "M", "JPN", 30),
    ("Purple", "Fabio", "M", "ITA", 99),
    ("Blue", "Manuela", "F", "VEN", 25)
]


class UI(App):
    BINDINGS = [
        ("q", "quit_app", "Quit"),
    ]
    CSS_PATH = "textual_ui.tcss"
    # Enable the command palette, to add our custom filter commands
    ENABLE_COMMAND_PALETTE = True

    def action_quit_app(self):
        self.exit(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        table = DataTable(id=f'competitors_table')
        table.cursor_type = 'row'
        table.zebra_stripes = True
        table.loading = True
        yield table
        yield Footer()

    def on_mount(self) -> None:
        self.r=radio.radio(debugging=False,statusmonitor=self)
        self.gernerate_columns()
        self.assemble_data()

    def gernerate_columns(self):
        self.data=[["ID","Letzter Kontakt","Verbindung (SNR)","Akkustand"]]
        columns = [x.title() for x in self.data[0]]
        table = self.get_widget_by_id(f'competitors_table', expect_type=DataTable)
        table.add_columns(*columns)
        
    def assemble_data(self):
        self.data=[["ID","Letzter Kontakt","Verbindung","Akkustand"]]
        input_data=self.r.get_nodes_infos()
        print(input_data)
        for key,value in input_data.items():
            #print("key",key)
            print("value",value)
            name=value["user"]["shortName"]
            if name.find("T")!=0: #fall es sich nicht um einen Tracker handelt überspringen
                continue
            try:
                bat=min(value["deviceMetrics"]["batteryLevel"],100)#gibt manchmal über 100% akkustand an
            except:
                bat="-"
            try:
                #last_heard=value["lastHeard"] #lastHeard updates only with huge delay
                last_heard=value["position"]["time"] 
                print("last_heard",last_heard)
                last_heard2=datetime.datetime.fromtimestamp(last_heard)
                last_heard3=last_heard2.time()
                print("last_heard2",last_heard2)
            except:
                last_heard="-"
                last_heard2="-"
                last_heard3="-"
            try:
                snr=value["snr"]
            except:
                snr="-"
            print("name",name,"last_heard",last_heard3,"bat",bat,"snr",snr)
            self.data.append([name,last_heard3,snr,str(bat)+"%"])
            
        print("assembeld data",self.data)
        table = self.get_widget_by_id(f'competitors_table', expect_type=DataTable)
        #columns = [x.title() for x in self.data[0]]
        #table.add_columns(*columns)
        table.add_rows(self.data[1:])
        table.loading = False

    
    def on_recieve_text(self,text):
        table = self.query_one(DataTable)
        table.clear()
        self.assemble_data()
        
    def on_recieve_pos(self,pos_dict):
        table = self.query_one(DataTable)
        table.clear()
        self.assemble_data()

if __name__ == "__main__":
    print("started")

    app = UI()
    app.title = f"Heimdall".title()
    app.run()
    
    print("ended")
