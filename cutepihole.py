# -*- coding: utf-8 -*-
import requests
import json
import re
import subprocess
import configparser
import time
import signal
import sys

import RPi.GPIO as GPIO

# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont

# Import LCD functions
from LCD import LCD_1in44
from LCD import LCD_Config

# Get some GPIO pins sorted
KEY_UP_PIN     = 6 
KEY_DOWN_PIN   = 19
KEY_LEFT_PIN   = 5
KEY_RIGHT_PIN  = 26
KEY_PRESS_PIN  = 13
KEY1_PIN       = 21
KEY2_PIN       = 20
KEY3_PIN       = 16

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

#weather config
api_key            = config['weather']['owm_api_key']
fixed_location     = config['weather']['fixed_location']
location           = config['weather']['location']
interval           = 0

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
    GPIO.output(LCD_Config.LCD_BL_PIN,GPIO.LOW)
    GPIO.cleanup()
    print('Caught SIGINT')
    sys.exit(0)

#get location based on IP
def ip_info(addr=''):
    from urllib.request import urlopen
    from json import load
    if addr == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + addr + '/json'
    res = urlopen(url)
    #response from url(if res==None then check connection)
    data = load(res)
    config['weather']['location'] = data['loc']
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    return data['loc']

# are we updating from IP address? Or using fixed address?
if fixed_location == "false":
    latlon = ip_info()
else:
    latlon = config['weather']['location']
lat,lon = latlon.split(",")


# get weather data
def get_weather():
    iconmap = {
        "01": "Clear Sky",
        "02": "Few Clouds",
        "03": "Scattered Clouds",
        "04": "Broken Clouds",
        "09": "Rain Showers",
        "10": "Rain",
        "11": "Thunderstorms",
        "13": "Snow",
        "50": "Mist"
    }
    url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
    weatherresponse = requests.get(url)
    weatherdata = json.loads(weatherresponse.text)
    icon_arch = (weatherdata["current"]["weather"][0]["icon"])
    icon_strip = re.sub('[dn]', '', icon_arch)
    current_temp = weatherdata["current"]["temp"]
    current_cond = iconmap.get(icon_strip, icon_strip)
    if debug == "true":
        print ("Api key: ", api_key)
        print("Current Temperature: ", weatherdata["current"]["temp"])
        print("Current Icon: ", weatherdata["current"]["weather"][0]["icon"])
        print ("The icon text is: ", iconmap.get(icon_strip, icon_strip))
        print ("Seconds until next refresh: ", interval)
    return current_temp, current_cond, icon_arch;

def panel_pihole():
    y = top
    img = Image.open("images/{}.png".format(STATUS))
    width = 128
    height = 128
    newsize = (width, height)
    imgr = img.resize(newsize)
    image.paste(imgr)
    if STATUS == "enabled":
        blockedadsstring = ("Blocked Ads: {}".format(str(ADSBLOCKED)))
        wtext, htext = draw.textsize(blockedadsstring)
        draw.text(((width-wtext)/2+1, y+116), blockedadsstring, font=font, fill="#FFFFFF")
        draw.text(((width-wtext)/2, y+116), blockedadsstring, font=font, fill="#000000")
    else:

        wtext, htext = draw.textsize("Blocking Disabled!")
        draw.text(((width-wtext)/2+1, y+116), "Blocking Disabled!", font=font, fill="#FFFFFF")
        draw.text(((width-wtext)/2, y+116), "Blocking Disabled!", font=font, fill="#000000")

def panel_stats():
    y = top
    draw.text((x, y), IP, font=font, fill="#FFFF00")
    y += font.getsize(IP)[1]
    draw.text((x, y), CPU, font=font, fill="#FFFF00")
    y += font.getsize(CPU)[1]
    draw.text((x, y), MemUsage, font=font, fill="#00FF00")
    y += font.getsize(MemUsage)[1]
    draw.text((x, y), Disk, font=font, fill="#0000FF")
    y += font.getsize(Disk)[1]
    draw.text((x, y), "DNS Queries: {}".format(DNSQUERIES), font=font, fill="#FF00FF")

def panel_weather(current_temp, current_cond, icon_arch):
    y = top
    width = 128
    height = 128
    img = Image.open("images/{}.bmp".format(icon_arch))
    newsize = (width, height)
    imgr = img.resize(newsize)
    image.paste(imgr)
    wtext, htext = draw.textsize(current_cond)
    draw.text(((width-wtext)/2, htext-12), current_cond, font=font, fill="#000000")  
    current_temp = int(current_temp)
    draw.text((x+1, y+98), "{}°".format(str(current_temp)), font=largefont, fill="#000000")
    draw.text((x, y+98), "{}°".format(str(current_temp)), font=largefont, fill="#FFFFFF")
    
def panel_update():
    y = top
    draw.text((x, y), "UPDATE CutePiHole?", font=font, fill="#FFFF00")
    y += font.getsize("UPDATE CutePiHole?")[1]
    draw.text((x, y), "Press Middle", font=font, fill="#FFFF00")
    y += font.getsize("Press Middle")[1]
    draw.text((x, y), "Click to", font=font, fill="#00FF00")
    y += font.getsize("Click to")[1]
    draw.text((x, y), "Update", font=font, fill="#0000FF")
    y += font.getsize("Update")[1]


# LCD Setup

# 240x240 display with hardware SPI:
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT 
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = 128
height = 128
image = Image.new('RGB', (width, height))


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.LCD_ShowImage(image,0,0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
largefont = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 30)
backlight = 1

# main event
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=(255, 204, 209))

    # Shell scripts for system monitoring from here:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = "IP: "+subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "hostname | tr -d \'\\n\'"
    HOST = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
    cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'" # pylint: disable=line-too-long

    # Pi Hole data!
    try:
        r = requests.get(pihole_api_url)
        data = json.loads(r.text)
        DNSQUERIES = data['dns_queries_today']
        ADSBLOCKED = data['ads_blocked_today']
        CLIENTS = data['unique_clients']
        STATUS = data['status']
    except KeyError:
        time.sleep(1)
        continue

    # Weather data!
    if interval == 0:
        try:
            interval = config['weather'].getint('interval')
            current_temp, current_cond, icon_arch = get_weather()
        except KeyError:
            time.sleep(1)
            continue
    else:
        interval -= 1
        if debug == "true":
            print ("Seconds until next refresh: ", interval)

    y = top
    
    if GPIO.input(KEY_UP_PIN) == 0:
        screenid += 1
        if screenid >= 4:
            screenid = 1

    if GPIO.input(KEY_DOWN_PIN) == 0:
        screenid -= 1
        if screenid <= 0:
            screenid = 3

    if GPIO.input(KEY_LEFT_PIN) == 0 and update_panel == "true":
        screenid = 4

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
        panel_stats()
    else:
        if screenid == 1:
            panel_pihole()
        elif screenid == 2:
            panel_weather(current_temp, current_cond, icon_arch)
        elif screenid == 3:
            panel_stats()
        elif screenid == 4:
            panel_update()
        else:
            panel_pihole()

    
    if GPIO.input(KEY2_PIN) == 0: 
        try:
            r = requests.get(disable_url)
            if debug == "true":
                print ("Key 2 Pushed - Disabling PiHole for 5m")
        except:
            time.sleep(1)

    if GPIO.input(KEY3_PIN) == 0: 
        if backlight == 1:
            GPIO.output(LCD_Config.LCD_BL_PIN,GPIO.LOW)
            backlight = 0
            if debug == "true":
                print ("Key 3 Pushed - Disabling LCD")
        else:
            GPIO.output(LCD_Config.LCD_BL_PIN,GPIO.HIGH)
            backlight = 1
            if debug == "true":
                print ("Key 3 Pushed - Enabling LCD")
    
    
    signal.signal(signal.SIGINT, signal_handler)
    #signal.pause()

    # Display image.
    angle = 180
    imr = image.rotate(angle)
    disp.LCD_ShowImage(imr,0,0)
    time.sleep(.1)