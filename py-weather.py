#!/usr/bin/python3
#
#-- py-weather.py
#
#   Displays weather using the OPEN Weather API.
#
#   Requires:           python3
#
#   This program is free software: you can redistribute it and/or modify it
#   under  the terms of the GNU General Public License as published by  the
#   Free Software Foundation, either version 3 of the License, or (at  your
#   option) any later version.
#
#   This  program is distributed in the hope that it will  be  useful,  but
#   WITHOUT   ANY   WARRANTY;   without even  the   implied   warranty   of
#   MERCHANTABILITY  or  FITNESS  FOR A PARTICULAR  PURPOSE.  See  the  GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program.  If not, see <http://www.gnu.org/licenses/>. 
#
#   10 Feb 18   0.1   - Initial version - MT
#                     - Creates a separate weather object for each location
#                       specified on the command line - MT
#                     - Checks that the weather data could be obtained  for
#                       the specified location before adding weather object
#                       to the list of weather objects - MT 
#   14 Oct 18         - Added  a method to display a summary of the weather
#                       conditions (instead of just printing the data) - MT
#                     - Now encodes spaces in location names in URLs (which
#                       allows place names to contain spaces) - MT 
#                     - Updated  help text to show how to include the state
#                       and country code of a city in a location if this is 
#                       needed to unambiguously specify the location - MT
#   10 Feb 21         - Removed  custom  event handlers.  Instead uses  the
#                       standard  exception handling to trap  any  keyboard
#                       interupts (and errors) - MT
#
VERSION = "0.1"

import os, sys, signal

class weather(object):

  def __init__(self, _location, _appid):
    self.location = _location
    self.appid = _appid
    self.units = 'metric'
    self.weather = ""
    self.status = 0 
    self.error = None
    self.update() # Get the current weather for the specified location

  def update(self): # Update Weather data.

    import xmltodict, urllib, json
    import time
    
    _URI = ('https://api.openweathermap.org/data/2.5/weather?units=' + 
           urllib.parse.quote(self.units) + '&mode=xml&q=' + urllib.parse.quote(self.location) + '&appid=' + urllib.parse.quote(self.appid ))

    self.status = 0 # Clear any current errors
    self.error = ''
    try: 
      _socket = urllib.request.urlopen(_URI)
      _data=_socket.read()
      _socket.close()
      self.weather = xmltodict.parse(_data) # Convert XML response to a python dictionary 
      if _debug: 
        sys.stderr.write (self.weather['current']['city']['@name'] + "\n")
        sys.stderr.write (json.dumps(self.weather, indent=4) + "\n") # Dump dictionary as JSON.
      elif _verbose:
        self.list()
    except urllib.error.HTTPError as _Error:
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
    except Exception:
      import traceback
      self.status = -1
      sys.stderr.write (traceback.format_exc())
      exit(self.status)

  def list(self): # Print Weather data.
    import time, calendar

    _output = 'Location : \t\t'
    _output += self.weather['current']['city']['@name'] + '\n'
    _output += 'Country : \t\t'
    _output += self.weather['current']['city']['country'] + '\n'
    _output += 'Lat/Long : \t\t'
    _output += '%+06.2f' % float(self.weather['current']['city']['coord']['@lat']) + ',' + '%+07.2f' % float(self.weather['current']['city']['coord']['@lon']) + '\n'
    _output += 'Sunrise : \t\t' 
    _output += time.strftime('%a %d %b %Y %I:%M %p %Z', time.localtime(calendar.timegm(time.strptime(self.weather['current']['city']['sun']['@rise'],'%Y-%m-%dT%H:%M:%S')))) + '\n'
    _output += 'Sunset : \t\t'
    _output += time.strftime('%a %d %b %Y %I:%M %p %Z', time.localtime(calendar.timegm(time.strptime(self.weather['current']['city']['sun']['@set'],'%Y-%m-%dT%H:%M:%S')))) + '\n\n'
    _output += 'Description: \t\t'
    _output += self.weather['current']['weather']['@value'].title() + '\n'
    _output += 'Temprature : \t\t'
    _output += '%0.f' % round(float(self.weather['current']['temperature']['@value'])) + ' C\n'
    _output += 'Humidity : \t\t'
    _output += '%d' % float(self.weather['current']['humidity']['@value']) + ' %\n'
    _output += 'Pressure : \t\t'
    _output += '%d' % (float(self.weather['current']['pressure']['@value'])) + ' mb/hPa\n'
    if not self.weather['current']['clouds'] is None: # Check cloud data is available
      _output += 'Cloud Cover : \t\t' + '%d' % (float(self.weather['current']['clouds']['@value'])) + ' % '
      _output += '(' + self.weather['current']['clouds']['@name'].title() + ')\n'
    if not self.weather['current']['wind']['speed'] is None: # Check wind speed data is available
      _output += 'Wind Speed : \t\t' + '%d' % (float(self.weather['current']['wind']['speed']['@value']) * 3.6) + ' km/h ' 
      _output += '(' + self.weather['current']['wind']['speed']['@name'].title() + ')\n'
    if not self.weather['current']['wind']['direction'] is None: # Check wind direction data is available
      _output += 'Wind Direction : \t' +  '%d' % float(self.weather['current']['wind']['direction']['@value']) + u'\xb0 ' 
      _output += '(' + self.weather['current']['wind']['direction']['@code'] + ')\n\n'
    _output += 'Updated : \t\t' + time.strftime('%a %d %b %Y %I:%M %p %Z', time.localtime(calendar.timegm(time.strptime(self.weather['current']['lastupdate']['@value' ],'%Y-%m-%dT%H:%M:%S')))) + '\n\n'
    sys.stderr.write (_output)

  def dump(self): # Print Weather data.
    import json
    sys.stderr.write (json.dumps(self.weather, indent=4) + "\n") # Dump dictionary as JSON.
      
  
if __name__ == '__main__': 

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

  try:      
    _debug = False
    _verbose = False
    _humidity = False

    _locations = []
    _count = 1
    _appid = ""
    while _count < len(sys.argv):
      _arg = sys.argv [_count]
      if _arg[:1] == "-" and len(_arg) > 1:
        if _arg in ["--help", "-?"]:
          _about()
        elif _arg in "--version":
          _version()
        elif _arg in "--verbose":
          _verbose = True
        elif _arg in ["--debug"]:
          _debug = True
        elif _arg in ["--humidity"]:
          _humidity = True
        elif _arg in "--appid":
          if _count < len(sys.argv):
            if sys.argv[_count + 1][:1] != "-":
              _appid = sys.argv[_count + 1]
              _count += 1
        else:
          if _arg[:2] == "--":
            _error ("unrecognized option -- '" + (_arg[1:] + "'"))
          else:
            _error ("invalid option -- '" + (_arg[1:] + "'"))
      else:
        _locations.append(_arg)
      _count += 1

    if _appid == "":
      _error ("APPID not specified")

    _weather = []

    for _location in _locations[:1]:
      _item = weather(_location, _appid) # Get the weather for the location (left, top, width, height)
      if not _item.status: # Only add it to the list of weather results if successful
        _weather.append(_item) 

    for _location in _locations[1:]:
      _item = weather( _location, _appid) # Get the weather for the location (left, top, width, height)
      if not _item.status: # Only add it to the list of weather results if successful
        _weather.append(_item) 
     
    for _item in _weather:
      _output = 'Location : \t\t'
      _output += _item.weather['current']['city']['@name'] + ' (' + _item.weather['current']['city']['country'] +')\n'
      _output += 'Temprature : \t\t'
      _output += '%0.f' % round(float(_item.weather['current']['temperature']['@value'])) + ' C\n'
      _output += 'Description: \t\t'
      _output += _item.weather['current']['weather']['@value'].title().replace('Intensity ','') + '\n'      
      sys.stdout.write(_output)

  except KeyboardInterrupt: # Ctrl-C
    pass
  except Exception: # Catch all other errors - otherwise the script will just fail silently!
    import traceback
    sys.stderr.write (traceback.format_exc())
    exit(1)

  exit(0)
