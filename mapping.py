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
		self.update_every=60*1000#update time for the map in miliseconds
		self.saved_positions={}#stores positioninformation
		self.positions_folder="positions"
		self.position_counter=0
		self.create_map()
		
	def create_map(self):
		self.m = folium.Map()
		self.m.add_child(folium.LatLngPopup())
		
		path="file://"+os.getcwd()+"/"+self.map_filename
		
		#Folium doesn't know when something changed, so it needs to periodicaly reload
		autoreload = '''
			<script>
			setInterval(function(){
			window.open('%s', "_self")
			}, %s);
			</script>
	             '''%(path,self.update_every)
		self.m.get_root().html.add_child(folium.Element(autoreload))
		
		self.m.save(self.map_filename)

	def show_map(self):
		webbrowser.open(self.map_filename, new=2)#opens new tab
		
	def update_position(self,position_dict):
		"""thsis function handels new position data"""
		self.save_position(position_dict)
		self.add_marker(position_dict)
		self.draw_path(position_dict)
		self.set_bounds()
		self.m.save(self.map_filename)
		
	def add_marker(self,position_dict):
		"""adds a new marker to the map"""
		
		device_id=position_dict["device_id"]
		gps_time=position_dict["gps_time"]
		latitude=position_dict["latitude"]
		longitude=position_dict["longitude"]
		
		tooltip = 'device_id: %s'%device_id
		popup='<i>Details: \n Device %s \ngps timestamp %s</i>'%(device_id,gps_time)
		folium.Marker([latitude, longitude], popup=popup, tooltip=tooltip,icon=folium.Icon(color='lightgreen',icon_color='#0000ff', icon='bug',prefix='fa',angle=0)).add_to(self.m)
	
	def save_position(self, position_dict):
		try:
			self.saved_positions[str(position_dict["device_id"])].append(position_dict)
		except KeyError as e:
			self.saved_positions[str(position_dict["device_id"])]=[position_dict]
			
		filename=self.positions_folder+"/"+str(int(time.time()))+"."+str(self.position_counter)+".p"
		try:
			pickle.dump(self.saved_positions, open(filename, "wb" ) )
		except FileNotFoundError:
			print("couldn't store File.")
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
		
		folium.PolyLine([current_pos,old_pos], color="red", weight=2.5, opacity=1).add_to(self.m)
	
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
	latitude1=0
	longitude1=15
	latitude2=0
	longitude2=15
	#--make faster update-- (folium seems to crash, when the file is reloaded and witen at the same time, so reloding more often makes crashes more likely)
	m.update_every=10*1000#miliseconds
	
	m.create_map()
	
	m.show_map()
	
	for nr in range(100):
		print("Step nr",nr)
		latitude1+=(0.5-random.random())/10
		longitude1+=(0.5-random.random())/10
		latitude2+=(0.5-random.random())/10
		longitude2+=(0.5-random.random())/10
		position_dict1={"device_id":1,"latitude":latitude1,"longitude":longitude1,"gps_time":nr}
		position_dict2={"device_id":2,"latitude":latitude2,"longitude":longitude2,"gps_time":nr}
		m.update_position(position_dict1)
		m.update_position(position_dict2)
		time.sleep(4)

