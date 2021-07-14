# -*- coding: utf-8 -*-
import requests
import re
import subprocess
import configparser
import time
import signal
import sys
import git
from systemd.daemon import notify, Notification
import RPi.GPIO as GPIO

import panels
p = panels.Panel()

#note the LCD will be mounted "upside down", left is right, up is down, etc.

# Get some GPIO pins sorted
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16
RST_PIN        = 27
CS_PIN         = 8
DC_PIN         = 25
BL_PIN         = 24

#init GPIO

GPIO.setmode(GPIO.BCM) 
GPIO.setup(KEY_UP_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN,   GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY2_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up
GPIO.setup(KEY3_PIN,        GPIO.IN, pull_up_down=GPIO.PUD_UP)      # Input with pull-up

CONFIG_FILE = "cutepihole.ini"
#parse our config
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

#pihole config
pihole_api_url      = config['pihole']['pihole_api_url']
pihole_api_pass     = config['pihole']['pihole_api_pass']
pihole_disable_time = config['pihole']['pihole_disable_time']
pihole_config_file  = config['pihole']['pihole_config_file']
#panels config
default_panel      = config['panels']['default_panel']
if default_panel == "pihole":
    screenid = 1
elif default_panel == "weather":
    screenid = 2
elif default_panel == "stat":
    screenid = 3


#app config
update_panel       = config['app']['update_panel']
debug             = config['app']['debug']

# url to disable pihole
disable_url = pihole_api_url + "?disable=" + pihole_disable_time + "&auth=" + pihole_api_pass

# catch those SIGINTs
def signal_handler(sig, frame):
    GPIO.output(BL_PIN,GPIO.LOW)
    #GPIO.cleanup()
    print('Caught SIGINT')
    sys.exit(0)

backlight = 1
update_counter = 0
interval = config['weather'].getint('interval')
pihole_interval = config['pihole'].getint('pihole_interval')

print('Startup complete')
notify(Notification.READY)

# main event
while True:
    # Weather data!
    

    if GPIO.input(KEY_UP_PIN) == 0:
        screenid += 1
        if screenid >= 4:
            screenid = 1

    if GPIO.input(KEY_DOWN_PIN) == 0:
        screenid -= 1
        if screenid <= 0:
            screenid = 3

    if GPIO.input(KEY_LEFT_PIN) == 0 and update_panel == "true":
        if debug == "true":
                print ("Key Left Pushed")
        screenid = 4

    if GPIO.input(KEY_RIGHT_PIN) == 0 and update_panel == "true":
        if debug == "true":
                print ("Key Right Pushed")
        if update_counter == 5:
            p.draw_updating()
            p.display_paint()
            git.cmd.Git().fetch('--all')
            git.cmd.Git().reset('--hard', 'origin/releases')
            sys.exit(0)
        else:
            update_counter += 1

    if GPIO.input(KEY_PRESS_PIN) == 0:
        if screenid == 1:
            default_panel = "pihole"
        elif screenid == 2:
            default_panel = "weather"
        elif screenid == 3:
            default_panel = "stat"
        config['panels']['default_panel'] = default_panel    
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        

    if GPIO.input(KEY1_PIN) == 0: 
        p.get_sysinfo()
        p.draw_stats()
    else:
        if screenid == 1:
            if pihole_interval == 0:
                try:
                    pihole_interval = config['pihole'].getint('pihole_interval')
                    p.get_pihole()
                except KeyError:
                    time.sleep(1)
                    continue
            else:
                pihole_interval -= 1
                p.draw_pihole()
        elif screenid == 2:
            if interval == 0:
                try:
                    interval = config['weather'].getint('interval')
                    p.get_weather()
                except KeyError:
                    time.sleep(1)
                    continue
            else:
                time.sleep(1)
                interval -= 1
                if debug == "true":
                    print ("Seconds until next refresh: ", interval)
            p.draw_weather()
        elif screenid == 3:
            p.get_sysinfo()
            p.draw_stats()
        elif screenid == 4:
            p.draw_updatenotice()
        else:
            panel_pihole()

    
    if GPIO.input(KEY2_PIN) == 0: 
        try:
            r = requests.get(disable_url)
            p.get_pihole()
            if debug == "true":
                print ("Key 2 Pushed - Disabling PiHole for 5m")
        except:
            time.sleep(1)

    if GPIO.input(KEY3_PIN) == 0: 
        if backlight == 1:
            GPIO.output(BL_PIN,GPIO.LOW)
            backlight = 0
            if debug == "true":
                print ("Key 3 Pushed - Disabling LCD")
        else:
            GPIO.output(BL_PIN,GPIO.HIGH)
            backlight = 1
            if debug == "true":
                print ("Key 3 Pushed - Enabling LCD")
    
    
    signal.signal(signal.SIGINT, signal_handler)
    #signal.pause()

    # Display image.
    p.display_paint()
    time.sleep(.5)
