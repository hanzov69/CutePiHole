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

## Process / Other
- [ ] Tagging/Releases in Github
- [x] Linting/SCA?
- [ ] BOM
- [x] 3D Models for case

## Defect / Code Quality
- [x] `requirements.txt` freeze package versions
- [x] `Panel()` class
- [x] allcaps constants/global vars
- [x] general variable naming/capitalization cleanup/standardization
- [x] function scopes impacting global vars
- [ ] Remove prints - use logging facility for debug
- [x] Inconsistent string formatting
- [x] "don't have to cast types when using .format() syntax"
- [x] remove import json, us r.json
- [x] schwack urllib, requests present
- [ ] sort out configparser for booleans
- [x] move iconmap/url out of getweather()