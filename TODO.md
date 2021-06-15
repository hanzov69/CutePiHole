# ToDo
## Features
- [x] Images!
- [x] Rotate output
- [x] Click to save current screen as default
- [ ] Field upgrade routine
- [ ] Clock Panel
- [ ] Configure Unit type (for imperial savages)
- [ ] systemd units
- [ ] install scripts?
- [ ] get WEBPASSWORD automagically
- [ ] system for changing background color
- [ ] rework images for better support of background color
- [ ] configurable drop-shadow (black over white, white over black)

## Process
- [ ] Tagging/Releases in Github
- [ ] Linting/SCA?

## Defect / Code Quality
- [ ] `requirements.txt` freeze package versions
- [ ] `Panel()` class
- [ ] allcaps constants/global vars
- [ ] general variable naming/capitalization cleanup/standardization
- [ ] function scopes impacting global vars
- [ ] Remove prints - use logging facility for debug
- [ ] Inconsistent string formatting
- [ ] "don't have to cast types when using .format() syntax"
- [ ] remove import json, us r.json
- [ ] schwack urllib, requests present
- [ ] sort out configparser for booleans
- [ ] move iconmap/url out of getweather()