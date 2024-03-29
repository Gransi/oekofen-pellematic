#!/usr/bin/python3
#! python3
# -*- coding: utf-8 -*-

__author__ = "Peter Gransdorfer"
__copyright__ = "Copyright 2022"

__license__ = "GPL"
__maintainer__ = "Peter Gransdorfer"
__email__ = "peter.gransdorfer[AT]cattronix[com]"

import requests
import http.client
import urllib.parse
import json
import os
import re
import sys
import datetime
import _thread
import threading
import time
import paho.mqtt.client as mqtt

#Oekofen login settings
username = 'oekofen'
password = 'oekofen'
debug = 1
url = 'http://192.168.1.113'
cookies = None
req = None

#Oekofen hardware configuration
peCount=1   #Pellematic count
puCount=1   #Buffer count
hkCount=2   #Heating circuit count
wwCount=1   #Warm water circuit count
soCount=1   #Solar count

#Mqtt settings
Topic_Prefix = "oekofen/0"
BROKER_ADDRESS = "192.168.1.112"
PORT = 1883
QOS = 1


#Outside temperature
def common_Request():
    return {
        "CAPPL:LOCAL.L_aussentemperatur_ist":"Aussentemperatur"
    }

#Pellematic
def pe_Request(number):
    return {
        "CAPPL:FA[" + str(number) + "].L_kesselstatus":"PE" + str(number + 1) + " Kessel Status",
        "CAPPL:FA[" + str(number) + "].L_kesseltemperatur":"PE" + str(number + 1) + " Kesseltemperatur Ist",
        "CAPPL:FA[" + str(number) + "].L_kesseltemperatur_soll_anzeige":"PE" + str(number + 1) + " Kesseltemperatur Soll",
        "CAPPL:FA[" + str(number) + "].L_feuerraumtemperatur":"PE" + str(number + 1) + " Feuerraumtemperatur Ist",
        "CAPPL:FA[" + str(number) + "].L_feuerraumtemperatur_soll":"PE" + str(number + 1) + " Feuerraumtemperatur Soll",
        "CAPPL:FA[" + str(number) + "].L_einschublaufzeit":"PE" + str(number + 1) + " Brenner Einschub Zeit",
        "CAPPL:FA[" + str(number) + "].L_pausenzeit":"PE" + str(number + 1) + " Brenner Pausen Zeit",
        "CAPPL:FA[" + str(number) + "].L_luefterdrehzahl":"PE" + str(number + 1) + " Luefterdrehzahl",
        "CAPPL:FA[" + str(number) + "].L_saugzugdrehzahl":"PE" + str(number + 1) + " Saugzugdrehzahl",
        "CAPPL:FA[" + str(number) + "].L_unterdruck":"PE" + str(number + 1) + " Unterdruck",
        "CAPPL:FA[" + str(number) + "].L_drehzahl_uw_ist":"PE" + str(number + 1) + " Drehzahl UW",
        "CAPPL:FA[" + str(number) + "].L_br1":"PE" + str(number + 1) + " Brennerkontakt",
        "CAPPL:FA[" + str(number) + "].L_kap_sensor_raumentnahme":"PE" + str(number + 1) + " Sensor Raumentnahme",
        "CAPPL:FA[" + str(number) + "].L_kap_sensor_zwischenbehaelter":"PE" + str(number + 1) + " Sensor Zwischenbehaelter",
        "CAPPL:FA[" + str(number) + "].L_bsk_status":"PE" + str(number + 1) + " Brandschutzklappe",
		"CAPPL:FA[" + str(number) + "].L_es_bsk_zu":"PE" + str(number + 1) + " BSK Endschalter zu",
		"CAPPL:FA[" + str(number) + "].L_es_bsk_auf":"PE" + str(number + 1) + " BSK Endschalter auf",		
        "CAPPL:FA[" + str(number) + "].L_alterkessel":"PE" + str(number + 1) + " Best Kessel",
        "CAPPL:FA[" + str(number) + "].L_agt_zuend_flammueb":"PE" + str(number + 1) + " Zuendtemperatur",
        "CAPPL:FA[" + str(number) + "].L_drehzahl_ascheschnecke_ist":"PE" + str(number + 1) + " Drehzahl Aschemotor",
        "CAPPL:FA[" + str(number) + "].L_brennerstarts":"PE" + str(number + 1) + " Brennerstarts",
        "CAPPL:FA[" + str(number) + "].L_brennerlaufzeit_anzeige":"PE" + str(number + 1) + " Brennerlaufzeit",
        "CAPPL:FA[" + str(number) + "].L_mittlere_laufzeit":"PE" + str(number + 1) + " Mitterle Brennerlaufzeit",
        "CAPPL:FA[" + str(number) + "].L_sillstandszeit":"PE" + str(number + 1) + " Stillstandszeit",
        "CAPPL:FA[" + str(number) + "].L_anzahl_zuendung":"PE" + str(number + 1) + " Anzahl Zuendungen",
        "CAPPL:FA[" + str(number) + "].L_saugintervall":"PE" + str(number + 1) + " Saugintervall",
        "CAPPL:FA[" + str(number) + "].ausgang_stoermelderelais":"PE" + str(number + 1) + " Stoermeldung",
    }

#Buffer
def pu_Request(number):
    return {
        "CAPPL:LOCAL.L_pu[" + str(number) + "].einschaltfuehler_ist":"PU" + str(number + 1) + " TPO Ist",
        "CAPPL:LOCAL.L_pu[" + str(number) + "].einschaltfuehler_soll":"PU" + str(number + 1) + " TPO Soll",
        "CAPPL:LOCAL.L_pu[" + str(number) + "].ausschaltfuehler_ist":"PU" + str(number + 1) + " TPM Ist",
        "CAPPL:LOCAL.L_pu[" + str(number) + "].ausschaltfuehler_soll":"PU" + str(number + 1) + " TPM Soll",
        "CAPPL:LOCAL.L_pu[" + str(number) + "].pumpe":"PU" + str(number + 1) + " Pufferpumpe",
    }

#Heating circuit
def hk_Request(number):
    return {
        "CAPPL:LOCAL.L_hk[" + str(number) + "].vorlauftemp_ist":"HK" + str(number + 1) + " Vorlauftemperatur Ist",
        "CAPPL:LOCAL.L_hk[" + str(number) + "].vorlauftemp_soll":"HK" + str(number + 1) + " Vorlauftemperatur Soll",
        "CAPPL:LOCAL.L_hk[" + str(number) + "].raumtemp_ist":"HK" + str(number + 1) + " Raumtemperatur Ist",
        "CAPPL:LOCAL.L_hk[" + str(number) + "].pumpe":"HK" + str(number + 1) + " Pumpe"
    }

#Warm water circuit
def ww_Request(number):
    return {
        "CAPPL:LOCAL.L_ww[" + str(number) + "].einschaltfuehler_ist":"WW" + str(number + 1) + " Ein Temperatur",
        "CAPPL:LOCAL.L_ww[" + str(number) + "].temp_soll": "WW" + str(number + 1) + " Solltemperatur",
        "CAPPL:LOCAL.L_ww[" + str(number) + "].ausschaltfuehler_ist":"WW" + str(number + 1) + " Aus Temperatur",
        "CAPPL:LOCAL.L_ww[" + str(number) + "].pumpe":"WW" + str(number + 1) + " Pumpe",
		"CAPPL:LOCAL.ww[" + str(number) + "].einmal_aufbereiten": "WW" + str(number + 1) + " Einmal aufbereiten"
    }    

#solar circuit
def so_Request(number):
    return {
        "CAPPL:LOCAL.L_sk[" + str(number) + "].kollektortemp_ist":"SO" + str(number + 1) + " Kollektortemperatur",
        "CAPPL:LOCAL.L_sk[" + str(number) + "].speichertemp_ist":"SO" + str(number + 1) + " Speichertemperatur",
        "CAPPL:LOCAL.L_sk[" + str(number) + "].pumpe":"SO" + str(number + 1) + " Solarpumpe",
        "CAPPL:LOCAL.L_ertrag[" + str(number) + "].vorlauftemp_ist":"SO" + str(number + 1) + " Vorlauftemperatur",
        "CAPPL:LOCAL.L_ertrag[" + str(number) + "].ruecklauftemp_ist":"SO" + str(number + 1) + " Ruecklauftemperatur",
        "CAPPL:LOCAL.L_ertrag[" + str(number) + "].durchflussmenge":"SO" + str(number + 1) + " Durchfluss",
        "CAPPL:LOCAL.L_ertrag[" + str(number) + "].leistung_aktuell":"SO" + str(number + 1) + " Leistung aktuell",
        "CAPPL:LOCAL.ertrag[" + str(number) + "].leistung_tag":"SO" + str(number + 1) + " Tagesertrag",
        "CAPPL:LOCAL.ertrag[" + str(number) + "].leistung_gesamt":"SO" + str(number + 1) + " Gesamtertrag"
    }

#get data from system
def getDataFromSystem(url, items):
    global cookies
    global req
    
    try:
    
        #Parse url
        urlparse = urllib.parse.urlparse(url)
        
        #login
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'keep-alive',
            'Cookie': 'language=de'
        }    
        
        data = [            
            ('username', username),
            ('password', password),
            ('language', 'de'),
            ('submit', 'Anmelden')
        ]
        
        #form based login
        if cookies is None:
            req = requests.post(url + '/index.cgi',headers = headers, data = data)
            cookies = req.cookies #Save cookie
        
        print(req)
        print(cookies)
        
        #get data from touch
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept-Language': 'de'
        }    
        
        data = json.dumps(list(items))
            
        req = requests.post(url + '/?action=get&attr=1',headers = headers, cookies=cookies, data = data)
        
        if req.status_code != requests.codes.ok: return 0
        
        return req.json()

    except Exception as e:
        print(str(e))
        return 0
    
def parseData():
    
    global currenttime
    global cookies
    #get configuration
    config = getConfig()
    
    while True:
        currenttime = datetime.datetime.utcnow().isoformat() + 'Z'
        out = getDataFromSystem(url, config)
        
        #return if response is empty
        if out == 0: 
            cookies = None
            time.sleep(5)
            continue

        #save output to file
        with open('data.txt', 'w') as f:
            json.dump(out, f, ensure_ascii=False, sort_keys=True, indent=4)

        
        #get each json item
        for i in range(0,len(out)):
            
            item = out[i]
            
            #get values from response
            valueRaw = item['value']
            valueUnit = item['unitText'] if item['unitText'] != '???' else ''            
            divisor = item['divisor']
            shortName = item['shortText']
            formatTexts = item['formatTexts']
            name = item['name']
            
            #check divisor is given
            if divisor.isdigit():
                valueRaw = float(float(valueRaw) / float(divisor))
            
            #transform integer value to text, when format text is given
            if formatTexts != "":
                formatTextsSplit = formatTexts.split("|")
                value = formatTextsSplit[int(valueRaw)]
            else:
                value = valueRaw
            
            #print(config[name] + '-' + str(value))
            
            writeMqttData(config[name], valueRaw)
            
        time.sleep(60)
        print('-------------------------------------')

#build configuration request
def getConfig():
    config = common_Request()
        
    for i in range(0,peCount):
        config.update(pe_Request(i))

    for i in range(0,puCount):
        config.update(dict(pu_Request(i)))
        
    for i in range(0,hkCount):
        config.update(dict(hk_Request(i)))

    for i in range(0,wwCount):
        config.update(dict(ww_Request(i)))       
    
    for i in range(0,soCount):
        config.update(dict(so_Request(i)))   
    
    return config

def on_log(client, userdata, level, buff):
    print(buff)

#write data to MQTT
def writeMqttData(mesurement, value):
    
    mesurement = mesurement.replace('CAPPL:', '')
    mesurement = mesurement.replace(' ', '_')
    mesurement = mesurement.replace(':', '_')
    mesurement = mesurement.replace('.', '_')
    mesurement = mesurement.replace('[', '')
    mesurement = mesurement.replace(']', '')

    json_body = [{
            "measurement": mesurement,
            "time": currenttime,
            "fields": {
                "value": value
            }
        }]

    print(f"{Topic_Prefix}/{mesurement} - {value}")

    with open('data.txt', 'a') as f:
        json.dump(json_body, f, ensure_ascii=False, sort_keys=True, indent=4)

    client.publish(f"{Topic_Prefix}/{mesurement}", value, qos=QOS)
    client.loop()

# python on connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #set mqtt lwt
    client.publish(f"{Topic_Prefix}/connection",payload="online")

client = mqtt.Client()
client.on_log = on_log
client.on_connect = on_connect
client.will_set(f"{Topic_Prefix}/connection",payload="offline")
client.connect(BROKER_ADDRESS, PORT)
print("Connected to MQTT Broker: " + BROKER_ADDRESS)

try:
   eg = threading.Thread(target=parseData)
   eg.daemon = True
   eg.start()
   eg.join()
except Exception as e:
   print("Error {0}".format(str(e.args[0])).encode("utf-8"))
   print ("Error: unable to start thread")

