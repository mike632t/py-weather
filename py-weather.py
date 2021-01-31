#!/usr/bin/python
#
# py-pygame-display-icons.py
#
# Displays weather using the OPEN Weather API.
#
# This  program  is free software: you can redistribute it and/or  modify it
# under the terms of the GNU General Public License as published by the Free
# Software  Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This  program  is  distributed  in the hope that it will  be  useful,  but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public  License
# for more details.
#
# You  should  have received a copy of the GNU General Public License  along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# 10 Feb 18     0.A - Initial version - MT
# 07 Oct 18     0.B - Changed dictionary to use Open Weather Icon names - MT
#
# http://openweathermap.org/forecast5
#

VERSION = "0.1"

import os, sys, signal

def _about():
  sys.stdout.write(
    "Usage: " + sys.argv[0] + " [LOCATION]...\n" +
    "Display weather conditions at LOCATION(s).\n" + "\n" +
    "      --appid <key>        specify the API key \n" +
    "  -?, --help               display this help and exit\n" +
    "      --version            output version information and exit\n" +
    "      --debug              dump raw data as JSON\n" +
    "\nExample:\n" +
    "  " + os.path.basename(sys.argv[0]) + " London display weather in London.\n")
  raise SystemExit
  
  
def _version():
  sys.stdout.write(os.path.basename(sys.argv[0]) + " " + str(VERSION) +"\n"
    "License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.\n"
    "This is free software: you are free to change and redistribute it.\n"
    "There is NO WARRANTY, to the extent permitted by law.\n")
  raise SystemExit
  
  
def _error(_error):
  sys.stderr.write(os.path.basename(sys.argv[0]) + ": " + _error + "\n")
  raise SystemExit
  
  
def _abort(signal, frame):
  pygame.quit()
  exit(0) 
  
  
def _handler(signum, frame):
  pass
  

def _beaufort_scale(_speed):
  if _speed > 32.7:
    return 12
  elif _speed > 28.5:
    return 11
  elif _speed > 24.5:
    return 10
  elif _speed > 20.5:
    return 9
  elif _speed > 17.2:
    return 8
  elif _speed > 13.9:
    return 7
  elif _speed > 13.9:
    return 6
  elif _speed > 10.8:
    return 6
  elif _speed > 8.0:
    return 5
  elif _speed > 5.5:
    return 4
  elif _speed > 3.4:
    return 3
  elif _speed > 1.6:
    return 2
  elif _speed > 0.5:
    return 1
  else:
    return 0
  

class weather(object):
  def __init__(self, _key, _location, _title = None):
    self.units = 'metric'
    self.location = _location
    self.update()
  
  def update(self): # Update Weather data.

    import xmltodict, urllib2, json
    import time
    
    _URI = 'https://api.openweathermap.org/data/2.5/weather?units=' + self.units + '&mode=xml&q=' + self.location + '&appid=' + _key 

    self.status = 0 # Clear any current errors
    self.error = ''
    try: 
      _socket = urllib2.urlopen(_URI)
      _data=_socket.read()
      _socket.close()
      self.weather = xmltodict.parse(_data) # Convert XML response to a python dictionary 
      if _debug: 
        sys.stderr.write (self.location + "\n")
        sys.stderr.write (json.dumps(self.weather, indent=4) + "\n") # Dump dictionary as JSON.
    except urllib2.HTTPError as _Error:
      self.status = _Error.code
      if _Error.code == 404:
        sys.stderr.write ('Error : ' + str(_Error.code) + ' - ' + 'Location (' + _location + ') not found.')
        self.error = 'Location (' + _location + ') not found.'
      elif _Error.code == 401: 
        sys.stderr.write ('Error : ' + str(_Error.code) + ' - ' + 'Check your application ID is valid.')
        self.error = 'Check your application ID is valid.'
      else:
        sys.stderr.write ('Error : ' + str(_Error.code) + ' - ' + _Error.reason)
        self.error = str(_Error.reason)
      sys.stderr.write ('\n')
    except urllib2.URLError as _Error:
      self.status = -1
      self.error = str(_Error.reason)
      sys.stderr.write ('Error : ' + self.error + '\n')
      exit(self.status)
    except Exception:
      import traceback
      self.status = -1
      sys.stderr.write (traceback.format_exc())
      exit(self.status)

  def show(self): # Print Weather data.
    import time, calendar

    _kph = 3.6
    _mph = 2.23694

    _output =  ('Location : \t\t' + self.weather['current']['city']['@name'] + '\n')
    _output += ('Country : \t\t' + self.weather['current']['city']['country'] + '\n')
    _output += ('Lat/Long : \t\t' + 
                '%+06.2f' % float(self.weather['current']['city']['coord']['@lat']) + ',' + 
                '%+07.2f' % float(self.weather['current']['city']['coord']['@lon']) + '\n')
    _output += ('Sunrise : \t\t' + time.strftime('%a %d %b %Y %I:%M %p %Z', 
                time.localtime(calendar.timegm(time.strptime(self.weather['current']['city']['sun']['@rise'],'%Y-%m-%dT%H:%M:%S')))) + '\n')
    _output += ('Sunset : \t\t' + time.strftime('%a %d %b %Y %I:%M %p %Z', 
                time.localtime(calendar.timegm(time.strptime(self.weather['current']['city']['sun']['@set'],'%Y-%m-%dT%H:%M:%S')))) + '\n\n')
    _output += ('Description: \t\t' + self.weather['current']['weather']['@value'].title() + '\n')
    _output += ('Temprature : \t\t')
    _output += ('%.1f' % float(self.weather['current']['temperature']['@value']) + ' C\n')
    _output += ('Humidity : \t\t' + '%d' % float(self.weather['current']['humidity']['@value']) + ' %\n')
    _output += ('Pressure : \t\t')
    _output += ('%d' % (float(self.weather['current']['pressure']['@value'])) + ' mb/hPa\n') 
    _output += ('Cloud Cover : \t\t' + '%d' % (float(self.weather['current']['clouds']['@value'])) + ' % ' +
                self.weather['current']['clouds']['@name'].title() + '\n')
    _output += ('Wind Speed : \t\t' + '%d' % (float(self.weather['current']['wind']['speed']['@value']) * _kph) + ' km/h ' + 
                '(' + self.weather['current']['wind']['speed']['@name'].title() + 
                ' Force ' + str(_beaufort_scale(float(self.weather['current']['wind']['speed']['@value']))) + ')\n')      
    _output += ('Wind Direction : \t' +  '%d' % float(self.weather['current']['wind']['direction']['@value']) + u'\xb0 ' + '(' + 
                self.weather['current']['wind']['direction']['@code'] + ')\n\n')
    _output += ('Updated : \t\t' + time.strftime('%a %d %b %Y %I:%M %p %Z', 
                time.localtime(calendar.timegm(time.strptime(self.weather['current']['lastupdate']['@value' ],'%Y-%m-%dT%H:%M:%S')))) + '\n')
    sys.stderr.write (_output)

  def dump(self): # Print Weather data.
    import json
    sys.stderr.write (json.dumps(self.weather, indent=4) + "\n") # Dump dictionary as JSON.
 
  
_debug = False
_mode='xml' # json, xml, html
_units='metric' # standard, metric, imperial

_locations = []
_count = 1
_key= ""
while _count < len(sys.argv):
  _arg = sys.argv[_count]
  if _arg[:1] == "-" and len(_arg) > 1:
    if _arg in ["--debug"]:
      _debug = True
    elif _arg in ["--help", "-?"]:
      _about()
    elif _arg in "--version":
      _version()
    elif _arg in "--appid":
      if _count < len(sys.argv):
        if sys.argv[_count + 1][:1] <> "-":
          _key = sys.argv[_count + 1]
          _count += 1
    else:
      if _arg[:2] == "--":
        _error ("unrecognized option -- '" + (_arg + "'"))
      else:
        _error ("invalid option -- '" + (_arg[1:] + "'"))
  else:
    _locations.append(_arg)
  _count += 1

if _key == "":
  _error ("APPID not specified")
 
signal.signal(signal.SIGHUP, _handler)
signal.signal(signal.SIGINT, _abort) # Set up interrupt event handlers
signal.signal(signal.SIGTERM, _abort)

_reports = []  
for _location in _locations:
  _item =  weather(_key, _location) # Get the weather for each location
  if not _item.status: # Only add it to the list of weather results if successful
    _reports.append(_item) 
    
for _report in _reports:
  _report.show()

exit(0)
