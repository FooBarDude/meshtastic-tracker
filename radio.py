#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""all radio related functions"""

import sys
import os

sys.path.append('../../Libraries/Meshtastic-python')#use the local Meshtastic-python library for develeopement
import meshtastic #pip3 install meshtastic --user
import meshtastic.serial_interface


from pubsub import pub #pip3 install pubsub --user

import time
import datetime
import pickle


class radio():
    def __init__(self,map=None,debugging=False):
        """the radio class handles all comunication with the meshtastic hard&software
        param: map: an object of the mapping class. this is used to update the map
        param: debugging: bool: if true more messeages are printed and all packets are stored"""
        
        self.map=map
        self.debugging=debugging
        self.packet_counter=0#stores the number of recieved packets to avoid collisions when pickling
        self.outstanding_pings={}#dict to keep track or pings
        pub.subscribe(self.onConnection, "meshtastic.connection.established")
        pub.subscribe(self.onReceive, "meshtastic.receive")
        pub.subscribe(self.onReceive_text, "meshtastic.receive.text")
        pub.subscribe(self.onReceive_position, "meshtastic.receive.position")
        #self.interface = meshtastic.StreamInterface()
        self.serial_interface = meshtastic.serial_interface.SerialInterface()
        self.packet_folder="packets"

    def get_device_config(self):
        """get the configuration of the connected board"""
        URL=self.serial_interface.channelURL
        wait_bluetooth_secs=self.serial_interface.radioConfig.preferences.wait_bluetooth_secs
        position_broadcast_secs=self.serial_interface.radioConfig.preferences.position_broadcast_secs
        gps_attempt_time=self.serial_interface.radioConfig.preferences.gps_attempt_time
        gps_update_interval=self.serial_interface.radioConfig.preferences.gps_update_interval
        
        #TODO: add other relevant configuratiosn
        return {"URL":URL,"wait_bluetooth_secs":wait_bluetooth_secs,"position_broadcast_secs":position_broadcast_secs,"gps_attempt_time":gps_attempt_time,"gps_update_interval":gps_update_interval}
    
    def set_device_config(self,general_config):
        """set the configuration of the connected board with previously stored settings"""
        self.serial_interface.setURL(general_config["URL"])
        self.serial_interface.radioConfig.preferences.wait_bluetooth_secs=general_config["wait_bluetooth_secs"]
        self.serial_interface.radioConfig.preferences.position_broadcast_secs=general_config["position_broadcast_secs"]
        self.serial_interface.radioConfig.preferences.gps_attempt_time=general_config["gps_attempt_time"]
        self.serial_interface.radioConfig.preferences.gps_update_interval=general_config["gps_update_interval"]
        
        #TODO: add other relevant configuratiosn
        self.serial_interface.writeConfig()
    
    def onReceive(self,packet,interface): # called when a packet arrives
        if self.debugging==True:
            print(f"Received: {packet}")
            filename=self.packet_folder+"/"+str(int(time.time()))+"."+str(self.packet_counter)+".p"
            pickle.dump( packet, open(filename, "wb" ) )
            self.packet_counter+=1
        
        #--process ping returns--
        try:
            pingID=packet['decoded']['successId']
            self.onReceive_ping_response(packet, interface)
        except KeyError:
            pass
        try:
            pingId=packet['decoded']['failId']
            self.onReceive_ping_response(packet, interface)
        except KeyError:
            pass
            
        #--update battery level--
        try:
            sender_id=packet['from']
            batteryLevel=packet['decoded']['deviceMetrics']['batteryLevel']
            print("updated battery level:",sender_id,batteryLevel,"%")
        except KeyError:
            pass

    def onReceive_text(self,packet,interface): # called when a packet arrives
        #print(f"Received: {packet}")
        
        if ("data" in packet['decoded']) and ('text' in packet['decoded']['data']):
            msg = str(packet['decoded']['data']['text'])
            
            
            try:
                rxSnr = packet['rxSnr']
                hopLimit = packet['hopLimit']
            except KeyError:
                print("didnt get snr or hopLimit")
                rxSnr="-"
                hopLimit="-"
            print(f"message: {msg}")
            if msg.find("test")>=0: #auto reply to messages containing 'test'
                if msg.find("rxSnr")>0:#bot dont reply to messegas I just sent out myself
                    return
                reply="got msg %s with rxSnr: %s and hopLimit: %s"%(msg,rxSnr,hopLimit)
                print("Sending reply: ",reply)
                interface.sendText(reply)
        else:
            print(f"Received packet, but couldn't decode it: {packet}")
    
    def onReceive_position(self,packet,interface): # called when a packet arrives
        print(f"Received position packet: {packet}")
        
        sender_id=packet['from']
        try:
            print("----got a position packet----")
            if self.debugging==True:
                print("++debug:",packet['decoded']['position'])
            latitude=packet['decoded']['position']['latitude']
            longitude=packet['decoded']['position']['longitude']
            gps_time=packet['decoded']['position']['time']
            sys_time=int(time.time())
            print("%s gps_time"%(gps_time,))
            
            print("%s sys_time"%(sys_time))
        except KeyError as e:
            print("but faild decoding basic info it. exception:",e)
            print("packet:",packet)
            return
        
        gps_date = datetime.datetime.fromtimestamp(gps_time / 1e3)
        
        sys_date= datetime.datetime.fromtimestamp(sys_time / 1e3)
        print("gps_time %s  ; sys_time: %s"%(gps_date,sys_date))
        #TODO: add dates to dict
        #TODO:, add battery level & SNR
        #TODO: add precicion (if avaliable)
        position_dict={"device_id":sender_id,"latitude":latitude,"longitude":longitude,"gps_time":gps_time,"gps_date":gps_date,"sys_time":sys_time,"sys_date":sys_date}
        
        #--add aditional infos if available--
        try:
            rx_time= packet['decoded']['rx_time']#not shure what time this is exactly
            print("%s rx_time"%(rx_time))
            rx_date= datetime.datetime.fromtimestamp(rx_time / 1e3)
            position_dict["rx_time"]=rx_time
            position_dict["rx_date"]=rx_date
        except KeyError as e:
            print("no rx_time")
        try:
            timestamp= packet['decoded']['position']['timestamp']#not shure what time this is exactly
            print("%s timestamp"%(timestamp))
            timestamp_date= datetime.datetime.fromtimestamp(timestamp / 1e3)
            position_dict["timestamp"]=timestamp
            position_dict["timestamp_date"]=timestamp_date
        except KeyError as e:
            print("no timestamp")
        try:
            HDOP= packet['decoded']['position']['HDOP']#horizontal dilution of precicion
            print("%s HDOP"%(HDOP))
            position_dict["HDOP"]=HDOP
        except KeyError as e:
            print("no HDOP")
        try:
            satsInView= packet['decoded']['position']['satsInView']#satelites in view
            print("%s satsInView"%(satsInView))
            position_dict["satsInView"]=satsInView
        except KeyError as e:
            print("no satsInView")
        try:
            rxSnr= packet['decoded']['rxSnr']#satelites in view
            print("%s rxSnr"%(rxSnr))
            position_dict["rxSnr"]=rxSnr
        except KeyError as e:
            print("no rxSnr")
        try:
            hopLimit= packet['decoded']['hopLimit']#satelites in view
            print("%s hopLimit"%(hopLimit))
            position_dict["hopLimit"]=hopLimit
        except KeyError as e:
            print("no hopLimit")
        try:
            rxRssi= packet['decoded']['position']['rxRssi']#satelites in view
            print("%s rxRssi"%(rxRssi))
            position_dict["rxRssi"]=rxRssi
        except KeyError as e:
            print("no rxRssi")
        
        print("position_dict",position_dict)
        
        self.map.update_position(position_dict)
        self.map.draw_map()#TODO: dont update to often to not slow things down
        #interface.sendText("position updated")#send a controlmessage to see remotly if GPS is logged
    
    
    def onReceive_ping_response(self,packet,interface):
        """capture ping responses, currentli onRecieve makes the triage"""
        #print("ping response triggerd")
        #print("packet",packet)
        target_id=packet["from"]
        try:
            snr=packet['rxSnr']
        except:
            snr="-"
        ping_id=packet['decoded']['successId']
        
        send_time=self.outstanding_pings[ping_id]['send_time']
        roundtrip_time=time.time()-send_time
        print("ping %s took %ss SNR:%s"%(target_id,round(roundtrip_time,1),snr))
        #TODO: drop data from outstanding_pings after a while
    
    def onConnection(self,interface, topic=pub.AUTO_TOPIC): # called when we (re)connect to the radio
        interface.sendText("meshtastic_trac has connected") #TODO: define a monitoring node and send message only there
    
    def print_node_settings(self):
        node=self.serial_interface.getMyNode()
        url=self.serial_interface.channelURL
        s_name=self.serial_interface.getShortName()
        l_name=self.serial_interface.getLongName()
        print("local node: %s \nURL: %s \nShortname: %s, Longname: %s"%(node,url,s_name,l_name))
    
        nodes=self.serial_interface.nodes
        print("all nodes:",nodes)
    
    def ping_device(self,device_id='^all'):
        """check if a device is reachable
        if no device is specified, all devices are pinged"""
        data=b"p"#ping
        sent_packet=self.serial_interface.sendData(data, destinationId=device_id, portNum=256, wantAck=True, wantResponse=True)
        print("sent ping to",sent_packet.to)
        self.outstanding_pings[sent_packet.id]={"send_time":time.time(),"packet":sent_packet}
        #TODO: test if theis is acutlly working as intended
    
    def print_pickled_packets(self):
        """ prints pickled packets, useful for debugging"""
        folder=os.listdir(self.packet_folder)
        print(folder)
        for filename in folder:
#             print(filename)
            unpickled=pickle.load(open(self.packet_folder+"/"+filename, 'rb'))
            print(unpickled)

if __name__ == "__main__":
    print("replaying stored packets")
    r=radio(map="")
    r.print_pickled_packets()
    print("finished")
    