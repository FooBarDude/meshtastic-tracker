#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""all map related functions"""

import sys
import time
import os
import pickle

import folium
import webbrowser



class mapping():
    def __init__(self):
        self.map_filename='meshtastic_tracker.html'
        self.update_every=60#autoreload the html every x seconds (cant do that when the file is been written at that moment and nees to bee reloaded manualy in that case)
        self.saved_positions={}#stores positioninformation
        self.positions_folder="positions"
        self.position_counter=0
        self.icon_color_dict={} #is used to assign colors to an device id
        self.create_map()
        
    def create_map(self):
        self.m = folium.Map()
        self.m.add_child(folium.LatLngPopup())
        
        path="file://"+os.getcwd()+"/"+self.map_filename
        
        #Folium doesn't know when something changed, so it needs to periodicaly reload
        autorefresh='<meta http-equiv="refresh" content="%s">'%(self.update_every)
        self.m.get_root().html.add_child(folium.Element(autorefresh))
        
        self.m.save(self.map_filename)
    
    def recreate_map(self):
        """create a map with only the last few positions of a tracker"""
        self.create_map()
        for item in self.saved_positions.items():
            print(item[1][-1])
            self.update_position(item[1][-1])
            self.draw_historic_path(device_id=item[1][-1]['device_id'],last=20)
        self.draw_map()
        
    def open_map(self):
        webbrowser.open(self.map_filename, new=2)#opens new tab
        
    def draw_map(self):
        """draw a updated map"""
        self.set_bounds()
        self.m.save(self.map_filename)
        
    def update_position(self,position_dict):
        """add new positions to the map"""
        print("updated position")
        self.save_position(position_dict)
        self.add_marker(position_dict)
        #self.draw_path(position_dict)
    
    def add_marker(self,position_dict):
        """adds a new marker to the map"""
        
        device_id=position_dict["device_id"]
        name=position_dict["name"]
        try:
            tooltip_time=position_dict["timestamp_date"]
        except:
            tooltip_time=position_dict["gps_date"]
        latitude=position_dict["latitude"]
        longitude=position_dict["longitude"]
        
        tooltip = 'device_id: %s'%name
        popup='<i>Details: \n Device %s \ngps timestamp %s</i>'%(device_id,tooltip_time)
        icon_color=self.icon_color_by_id(device_id)
        icon_symbol=self.icon_symbol_by_id(device_id)
        folium.Marker([latitude, longitude], popup=popup, tooltip=tooltip,icon=folium.Icon(color='lightgreen',icon_color=icon_color, icon=icon_symbol,prefix='fa',angle=0)).add_to(self.m)
        try:
            radius=position_dict["HDOP"]/100*4 # positionen die komplett daneben liegen haben trotzdem einen kleinen wert
            #radius=position_dict["PDOP"]/10
            #radius=1000/pow(position_dict["satsInView"],2)
            if position_dict["HDOP"]<500:
                fill_opacity=0.01
            else:
                fill_opacity=0.1
            folium.Circle([latitude, longitude],radius=radius, fill_color=icon_color, fill_opacity=fill_opacity, color=icon_color, weight=1).add_to(self.m)
        except:
            print("no precicion")
        #UserWarning: color argument of Icon should be one of: {'purple', 'pink', 'green', 'darkred', 'darkgreen', 'lightred', 'lightgray', 'lightgreen', 'darkblue', 'black', 'orange', 'blue', 'darkpurple', 'red', 'cadetblue', 'beige', 'white', 'lightblue', 'gray'}.
    
    def icon_color_by_id(self,device_id):
            palet=['#ff0000','#005f00','#0000ff','#00ffff','#ff00ff','#ffff00','#000000','#770000','#007700','#000077','#bbbbbb','#ffffff','#00ff00']#color palet to pick from
            try:
                color=self.icon_color_dict[device_id]
            except KeyError as e:
                pos=len(self.icon_color_dict)
                self.icon_color_dict[device_id]=palet[pos]
                color=self.icon_color_dict[device_id]
            return color
            
    def icon_symbol_by_id(self,device_id):
            icon="bug"
            #TODO: add matching simbols for different devices
            palet=['fa-user','fa-users','fa-circle-user','fa-person','fa-ghost','fa-diamond', 'fa-tower-broadcast']#color palet to pick from
            return palet[0]
            if device_id<9:
                icon=str(device_id)
                return icon
            try:
                pass
            except KeyError as e:
                pass
            except:
                pass
            return icon
            
            
    def save_position(self, position_dict):
        """backup der daten als pickel dump erstellen"""
        try:
            self.saved_positions[str(position_dict["device_id"])].append(position_dict)
        except KeyError as e:
            self.saved_positions[str(position_dict["device_id"])]=[position_dict]
            
        filename=self.positions_folder+"/"+str(int(time.time()))+"."+str(self.position_counter)+".p"
        try:
            pickle.dump(self.saved_positions, open(filename, "wb" ) )
        except FileNotFoundError:
            print("couldn't store File. Maybe the folder to store in does't exist")
        self.position_counter+=1
        #TODO: delete old files
        #TODO: save only once in a while
    
    def draw_path(self,position_dict):
        """draws a path from the last location to the current one"""
        current_pos=[position_dict["latitude"],position_dict["longitude"]]
        try:
            positions=self.saved_positions[str(position_dict["device_id"])]
            try:
                old_pos=[positions[-2]["latitude"],positions[-2]["longitude"]] #the last position in the list (-1) shold be the same as the current position supplied with the function call
            except IndexError:
                #print("got only one position, need at least two to draw a path")
                return
        except KeyError as e:
            #print("got no position, need at least two to draw a path")
            return
        color=self.icon_color_by_id(position_dict["device_id"])
        folium.PolyLine([current_pos,old_pos], color=color, weight=2.5, opacity=0.8).add_to(self.m)
        #folium.ColorLine([current_pos,old_pos], colors=[0,1],colormap=['b', 'g'], weight=2.5, opacity=1).add_to(self.m)
        
    def draw_historic_path(self,device_id,last=3):
        """draws a path of the last x locations of a device"""
        positions=self.saved_positions[str(device_id)]
        color=self.icon_color_by_id(device_id)
        for step in range(last):
            nr1=-1-step
            nr2=-2-step
            try:
                try:
                    pos1=[positions[nr1]["latitude"],positions[nr1]["longitude"]]
                    pos2=[positions[nr2]["latitude"],positions[nr2]["longitude"]]
                except IndexError:
                    #print("got only one position, need at least two to draw a path")
                    return
            except KeyError as e:
                #print("got no position, need at least two to draw a path")
                return
            folium.PolyLine([pos1,pos2], color=color, weight=2.5, opacity=0.8).add_to(self.m)
        
        
    def set_bounds(self):
        """goes throug all saved positions and sets the bound so that everithing is visible"""
        latitude_min=sys.float_info.max #set smalest/largest possible value to compare against
        latitude_max=sys.float_info.min #set smalest/largest possible value to compare against
        longitude_min=sys.float_info.max #set smalest/largest possible value to compare against
        longitude_max=sys.float_info.min #set smalest/largest possible value to compare against
        for key, value in self.saved_positions.items():
            #print("device",key,"positions",value)
            for pos in value:
                latitude_min=min(latitude_min,pos["latitude"])
                latitude_max=max(latitude_max,pos["latitude"])
                longitude_min=min(longitude_min,pos["longitude"])
                longitude_max=max(longitude_max,pos["longitude"])
        folium.FitBounds([(latitude_min,longitude_min), (latitude_max,longitude_max)]).add_to(self.m)


if __name__ == "__main__":
    print("!!! generating random path for testing !!!")
    import random
    m=mapping()
    
    #start-position--
    nr_of_trackers=5
    pos_list=[]
    for nr in range(nr_of_trackers):
        pos_list.append({"latitude1":0,"longitudel":15})
    
    #--make faster update-- (folium seems to crash, when the file is reloaded and witen at the same time, so reloding more often makes crashes more likely)
    m.update_every=10
    
    m.create_map()
    m.open_map()
    
    for tick in range(100):
        print("Step nr",tick)
        for nr in range(nr_of_trackers):
            pos_list[nr]["latitude1"]=pos_list[nr]["latitude1"]+(0.5-random.random())/10
            pos_list[nr]["longitudel"]=pos_list[nr]["longitudel"]+(0.5-random.random())/10
            position_dict1={"device_id":nr,"latitude":pos_list[nr]["latitude1"],"longitude":pos_list[nr]["longitudel"],"gps_time":tick,"gps_date":1}
            m.update_position(position_dict1)
            m.draw_path(position_dict1)
        m.draw_map()
        if tick%3==0:
            m.recreate_map()
        time.sleep(5)

