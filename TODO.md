# ToDo
## Features

- [ ] Clock Panel
- [ ] Configure Unit type (for imperial savages)
- [ ] install scripts?
- [ ] get WEBPASSWORD automagically
- [ ] configurable drop-shadow (black over white, white over black)
- [ ] 3D model is not great, make a new moar better one
- [ ] text only mode
- [ ] add system/process uptime to stats
- [x] Images!
- [x] Rotate output
- [x] Click to save current screen as default
- [x] Field upgrade routine
- [x] system for changing background color
- [x] rework images for better support of background color
- [x] systemd units


## Process / Other
- [ ] BOM
- [ ] Tagging/Releases in Github
- [x] Linting/SCA?
- [x] 3D Models for case

## Defect / Code Quality
- [x] hammering php-cgi with API calls, lets add a little delay to that
- [ ] sort out configparser for booleans
- [ ] Remove prints - use logging facility for debug
- [ ] text alignment issues abound, fix formatting
- [x] rework all images to correct resolution to avoid resize
- [x] `requirements.txt` freeze package versions
- [x] `Panel()` class
- [x] allcaps constants/global vars
- [x] general variable naming/capitalization cleanup/standardization
- [x] function scopes impacting global vars
- [x] Inconsistent string formatting
- [x] "don't have to cast types when using .format() syntax"
- [x] remove import json, us r.json
- [x] schwack urllib, requests present
- [x] move iconmap/url out of getweather()