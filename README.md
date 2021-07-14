# CutePiHole

This is still very much a Work In Progress. 

## 3D Printing
I'm terrible at 3D Modeling stuff, so if you really want to help, fix (or create an alternate) case design!

The selectable colors for the CutePiHole were designed to work well with the [Overture Matte PLA](https://amzn.to/3i5SWjl)

I printed using the Overture Matte PLA on a Prusa Mk3s using Prusa Slicer PLA defaults. No supports or tweaking needed. 

## Assumptions:

1. You have a Raspberry Pi of some flavor, using a [WaveShare 1.3inch LCD HAT](https://amzn.to/3wD4akS)
***
Note: Skip the version of fbcp they are pushing. Use [fbcp-ili9341](https://github.com/juj/fbcp-ili9341) instead. 

Use
`cmake -DSPI_BUS_CLOCK_DIVISOR=20 -DWAVESHARE_ST7789VW_HAT=ON -DBACKLIGHT_CONTROL=ON -DSTATISTICS=0 ..`

Don't add it to `/etc/rc.local` as they suggest, since it's not necessary for this app and can cause problems. Handy to have for boot diagnostics (kind of).
***
2. You have installed Raspbian, and [Installed PiHole](https://github.com/pi-hole/pi-hole/#one-step-automated-install)

## Install
1. Follow the guide found here: https://www.waveshare.com/wiki/1.3inch_LCD_HAT
2. Setup Python:

    >sudo apt-get update

    >sudo apt-get install python3-pip 
    
    >sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
    
    >sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2
    
    >sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
    
    >sudo pip install pillow

    >sudo pip install GitPython
    
    >sudo apt-get install libopenjp2-7 libtiff5 python3-numpy ttf-dejavu python3-requests git

    Note: Apt is preferred as the wheels take forever to install on a pi zero
3. Clone the latest release of this to your home directory - `git clone -b releases https://github.com/hanzov69/CutePiHole.git`
4. Rename `cutepihole.ini.sample` to `cutepihole.ini`
5. `cat /etc/pihole/setupVars.conf`, copy the value of `WEBPASSWORD` to `pihole_api_pass` in the config file
6. Register for an OpenWeatherMap account, get an API Key. Save this to `owm_api_key` in the config file
7. (optional) If you want to install this as a service that runs at boot, `sudo ./install.sh`

## Usage
`python cutepihole.py`

- Scroll through screens by pressing UP/DOWN on left joystick
- Temporarily display system stats with Button 1
- Disable PiHole blocking for 5 minutes (default) with Button 2
- Turn Off/On the display with Button 3
- Save Current screen as "default" by clicking joystick

## Configuration Options
- `owm_api_key` - see above
- `fixed_location` - if you don't want CutePiHole to detect your location automatically
- `location` - written automatically if above is `false`. Otherwise, set to Lat,Lon
- `interval` - the frequency OpenWeatherMap is hit. Default is 60s, increase if you hit API rate limits, this doesn't need a livestream

- `default_panel` - choose between `weather`,`stats`,`pihole`
- `color_panel` - choose the panel background color, options are "pink", "blue", "white" (not recommended). Pink is default, more added later

- `pihole_api_url` - don't change this, unless you know what you're doing
- `pihole_api_pass` - see above
- `pihole_disable_time` - duration to temporarily suspend pihole blocking, time is in seconds
- `pihole_config_file` - no function currently

- `update_panel` - no function currently
- `debug` - displays debug information on console

## Credits
Please see [LICENSE_SUPPLEMENT](LICENSE_SUPPLEMENT) for supplementary license details.

Credits/Attributions for the Icons used are available in [images/CREDITS](images/CREDITS)

Project inspired by [this excellent guide](https://learn.adafruit.com/pi-hole-ad-blocker-with-pi-zero-w/install-pi-hole) by AdaFruit

Case is a (bad) remix of a few designs found on Thingiverse
- [4798714](https://www.thingiverse.com/thing:4798714)
- [3334127](https://www.thingiverse.com/thing:3334127)
