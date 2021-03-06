from configparser import ConfigParser
from PIL import Image, ImageDraw, ImageFont
import re
import requests
import subprocess
import git
import spidev as SPI
import ST7789

RST = 27
DC = 25
BL = 24
bus = 0
device = 0

disp = ST7789.ST7789(SPI.SpiDev(bus, device),RST, DC, BL)

disp.Init()
disp.clear()

CONFIG_FILE = './cutepihole.ini'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=%s'
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
LARGEFONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 60)
YPADDING = -2
XPADDING = 0
WIDTH = 240
HEIGHT = 240
PANEL_SCREENID_MAP = {
    'pihole': 1,
    'weather': 2,
    'stat': 3,
    'update': 4
}
WEATHER_ICON_MAP = {
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

PANEL_COLOR_MAP = {
    "pink":  "#FFC4C4",
    "blue":  "#A9D8FF",
    "white": "#FFFFFF"
}

class Panel():

    def __init__(self, width=WIDTH, height=HEIGHT, config_file=CONFIG_FILE):
        '''
        Can be used in an endless loop e.g.
            panel = Panel()
            while True:
                if GPIO.button.pushed == 1:
                    p.get_pihole() # fetch new data
                    p.draw_pihole() # draw new data
                elif GPIO.button.pushed == 2:
                    p.get_weather()
                    p.draw_weather()
                ...
        '''

        # initialize the canvas
        self._image = Image.new('RGB', (width, height))
        self._draw = ImageDraw.Draw(self._image)
        #self._draw.rectangle((0, 0, width, height), outline=0, fill=(255, 255, 255))
        self._draw.rectangle((0, 0, width, height), outline=0, fill=(255, 196, 196))
        # get some padding going
        self._top = YPADDING
        self._bottom = height - YPADDING
        self._left = XPADDING
        self._right = width - XPADDING
        # read the config stuff
        self.__parse_config(config_file)
        # initialize some class attributes
        # may be able to skip this if it is slow on pizero
        self.get_sysinfo()
        self.get_pihole()
        self.get_weather()
    
    def __parse_config(self, cfg_file):
        '''
        Does what it says, dunderscored because it is basically useless after being run once so we
        don't want to visually expose it to the user in an iPython session
        '''
        cfg = ConfigParser()
        cfg.read(cfg_file)
        # weather
        self._weather_api_key = cfg['weather']['owm_api_key']
        is_fixed_loc = cfg['weather'].getboolean('fixed_location')
        # go get the location if it's not provided, and save back into config.ini
        if is_fixed_loc:
            self._location = cfg['weather']['location']
        else:
            self._location = get_ip_location()
            cfg.set('weather', 'location', self._location)
            cfg.set('weather', 'fixed_location', 'true')
            with open(cfg_file, 'w') as f:
                cfg.write(f)
        # pihole
        self._pihole_url = cfg['pihole']['pihole_api_url']
        self._pihole_disable_time = cfg['pihole'].getint('pihole_disable_time')
        # default panel if not indicated is pihole
        self._default_panel = PANEL_SCREENID_MAP.get(cfg['panels']['default_panel'], 1)
        self._color_panel = PANEL_COLOR_MAP.get(cfg['panels']['color_panel'], "#FFC4C4")
    
    def get_sysinfo(self):
        '''
        Get some information about the raspberry pi system
        '''
        ip_cmd = "hostname -I | cut -d\' \' -f1"
        self.IP = "IP: %s" % subprocess.check_output(ip_cmd, shell=True).decode('utf-8').strip()
        host_cmd = "hostname | tr -d \'\\n\'"
        self.HOST = subprocess.check_output(host_cmd, shell=True).decode('utf-8')
        cpu_cmd = "top -bn1 | awk '/^%Cpu/{printf \"CPU%%: \" $2}'"
        self.CPU = subprocess.check_output(cpu_cmd, shell=True).decode('utf-8')
        mem_cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        self.MEM = subprocess.check_output(mem_cmd, shell=True).decode('utf-8')
        disk_cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
        self.DISK = subprocess.check_output(disk_cmd, shell=True).decode('utf-8')
        temp_cmd =  "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'"
        self.CPU_TEMP = subprocess.check_output(temp_cmd, shell=True).decode('utf-8')
        self.TAG_VERSION = git.cmd.Git().describe('--tags')
        uptime_cmd = "uptime -p | awk -F'( )+' '{printf \"Uptime: \" $2\" \" $3}'"
        self.UPTIME = subprocess.check_output(uptime_cmd, shell=True).decode('utf-8')
        
    
    def get_pihole(self):
        '''
        Get some useful numbers from the pihole - doesn't seem to require an API key
        '''
        data = requests.get(self._pihole_url).json()
        # integers!
        self.DNSQUERIES = data.get('dns_queries_today', -1)
        self.ADSBLOCKED = data.get('ads_blocked_today', -1)
        self.CLIENTS = data.get('unique_clients', -1)
        # string!
        self.STATUS = data.get('status', 'Unknown')
        
               
    def get_weather(self, units='metric'):
        '''
        Get weather information from openweathermap.org
        '''
        lat, lon = self._location.split(',')
        url = WEATHER_URL % (lat, lon, self._weather_api_key, units)
        data = requests.get(url).json()
        self.WEATHER_ICON = data['current']['weather'][0]['icon']
        icon_strip = re.sub('[dn]', '', self.WEATHER_ICON)
        self.CURRENT_TEMP = data['current']['temp']
        # if we can't get a match on the icon key, return it for debugging
        self.CURRENT_COND = WEATHER_ICON_MAP.get(icon_strip, icon_strip)
        

    def draw_stats(self):
        '''
        Draw the RPi system info (all textual)
        '''
        text = f'{self.HOST}\n{self.IP}\n{self.CPU}\n{self.MEM}\n{self.DISK}\n{self.UPTIME}\n{self.CPU_TEMP}\nDNS Queries: {self.DNSQUERIES}\nVersion: {self.TAG_VERSION}'
        # clear the current canvas
        self._draw.rectangle(
            (0, 0, self._image.width, self._image.height),
            outline=0,
            fill=self._color_panel
        )
        # draw the text TODO: may need to adjust the spacing value
        self._draw.multiline_text(
            (self._left, self._top), 
            text, 
            spacing=1, 
            font=FONT, 
            fill='#000000'
        )
        
    
    def draw_pihole(self):
        '''
        Draw the adblocking info with a nice image indicating if blocking is enabled or not
        '''
        # draw our background
        self._draw.rectangle(
            (0, 0, self._image.width, self._image.height),
            outline=0,
            fill=self._color_panel
        )
        
        # get the image to use
        img = Image.open('./images/%s.png' % self.STATUS)

        # paste the image, using the image as a transparency mask
        self._image.paste(img, (0, 0), mask=img)

        # what's our status?
        if self.STATUS == 'enabled':
            text = 'Blocked Ads: %d' % self.ADSBLOCKED
        else:
            text = 'Blocking Disabled!'
        wtext, htext = self._draw.textsize(text)
        
        # draw text
        text_xy = ((self._image.width - wtext) / 4, self._top + 209)
        shadow_xy = ((self._image.width - wtext) / 4 + 1, self._top + 210)
        self._draw.text(text_xy, text, font=FONT, fill='#FFFFFF')
        self._draw.text(shadow_xy, text, font=FONT, fill='#000000')
        

    def draw_weather(self):
        '''
        Draw the weather information
        '''
        # draw our background
        self._draw.rectangle(
            (0, 0, self._image.width, self._image.height),
            outline=0,
            fill=self._color_panel
        )
        
        # get the image to use
        img = Image.open('./images/%s.png' % self.WEATHER_ICON)

        # paste the image over the background, using the image as a transparency mask
        self._image.paste(img, (0, 0), mask=img)
        
        # draw text
        wtext, htext = self._draw.textsize(self.CURRENT_COND)
        cond_xy = ((self._image.width - wtext) / 4, htext - 12)
        self._draw.text(cond_xy, self.CURRENT_COND, font=FONT, fill="#000000")
        temp_text = f'{self.CURRENT_TEMP:.0f}??'
        temp_text_xy = (self._left + 4, self._top + 179)
        temp_shadow_xy = (self._left + 5, self._top + 180)
        self._draw.text(temp_shadow_xy, temp_text, font=LARGEFONT, fill="#000000")
        self._draw.text(temp_text_xy, temp_text, font=LARGEFONT, fill="#FFFFFF")  
       
    def draw_updatenotice(self):
        '''
        Draw the Update Warning
        '''
        text = f'Update Warning\nTo check for\nor apply an update\nhold Left\non Joystick\nfor a few seconds'
        # clear the current canvas
        self._draw.rectangle(
            (0, 0, self._image.width, self._image.height),
            outline=0,
            fill='#000000'
        )
        # draw the text TODO: may need to adjust the spacing value
        self._draw.multiline_text(
            (self._left, self._top), 
            text, 
            spacing=1, 
            font=FONT, 
            fill='#FF00FF'
        )
    def draw_updating(self):
        '''
        Draw the Updating dialog
        '''
        text = f'Updating!'
        # clear the current canvas
        self._draw.rectangle(
            (0, 0, self._image.width, self._image.height),
            outline=0,
            fill='#000000'
        )
        # draw the text TODO: may need to adjust the spacing value
        self._draw.multiline_text(
            (self._left, self._top), 
            text, 
            spacing=1, 
            font=FONT, 
            fill='#FF00FF'
        )    

    def display_paint(self):
        angle = 180
        imr = self._image.rotate(angle)
        disp.ShowImage(imr,0,0)
    

def get_ip_location(ip=''):
    '''
    Doesn't need to be inside the class, keeping it outside 
    '''
    url = 'https://ipinfo.io/json' if ip == '' else f'https://ipinfo.io/{ip}/json'
    data = requests.get(url).json()
    return data['loc']
       