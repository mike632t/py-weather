#!/usr/bin/python3
#
#-- py-weather.py
#
#   Displays weather using the OPEN Weather API.
#
#   Requires:           python3, python3-tz, python3-pygame, 
#                       python3-cairosvg 
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
#   11 Feb 21   0.2   - Added  a graphical display using pygame to  display 
#                       the  current  weather conditions at  each  location
#                       an  image, selected using the icon name returned by
#                       the open weather API - MT
#                     - Rather  than updating the icons and  then  sleeping
#                       for 15 munutes the icon are updated once and before
#                       being redrawn in the loop, which allows the program
#                       to respond to events in a timely manner - MT
#                     - Now  uses the weather codes to  generate the  icons
#                       which gives a much better match between the weather
#                       conditions and the icon used - MT
#   16 Feb 21         - Can now resize the images (this needs bit of a fudge  - MT
#                     - Removed  the word 'Intensity' from the  description
#                       of the weather conditions if present ('Heavy  Rain'
#                       looks  better  than 'Heavy Intensity  Rain') - MT
#   20 Feb 21         - Adjusted the size of the icon to allow more text to
#                       be  displayed below the image.  (The graphic is now 
#                       only two thirds of the width of the icon) - MT
#                     - Height of the icon is determined automatically from
#                       it's width, which ensures there is enough space for
#                       the text below the graphic - MT 
#                     - Fixed  icon spacing so they are spaced  out  evenly
#                       over the full width of the display - MT
#                     - Ignores  any additional locations if there  is  not
#                       enough space on the display to display them - MT
#                     - Updating the size before drawing the icon means the
#                       width can be changed on the fly - MT
#

import io, sys, time, calendar
import xmltodict, urllib, json
import traceback
import pygame, cairosvg

NAME = "Weather Display"
VERSION = "0.2"

DISPLAY_SIZE = DISPLAY_WIDTH, DISPLAY_HEIGHT = (800, 480)
FPS = 60
INTERVAL = 900 # Update interval

BACKGROUND_COLOUR = 'grey10'
TEXT_COLOUR = 'white'
DARKTEXT_COLOUR = 'dark grey'


class weather(object):

  def __init__(self, _width, _location, _appid,_title = None):
    self.size = (self.width, self.height, ) = (_width, (_width + _width // 6))
    self.appid = _appid
    self.units = 'metric'
    self.location = _location
    self.description = ""
    self.status = 0 
    self.error = None
    self.update() # Get the current weather for the specified location
    
  def update(self): # Update Weather data.
    
    _URI = ('https://api.openweathermap.org/data/2.5/weather?units=' + 
           urllib.parse.quote(self.units) + '&mode=xml&q=' + urllib.parse.quote(self.location) + '&appid=' + urllib.parse.quote(self.appid ))

    self.status = 0 # Clear any current errors
    self.error = ''
    try: 
      _socket = urllib.request.urlopen(_URI)
      _data=_socket.read()
      _socket.close()
      self.weather = xmltodict.parse(_data) # Convert XML response to a python dictionary 
      self.description = self.weather['current']['weather']['@value'].title().replace('Intensity ', '')
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
      self.status = -1
      sys.stderr.write (traceback.format_exc())
      exit(self.status)

  def list(self): # Print Weather data.

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
    sys.stderr.write (json.dumps(self.weather, indent=4) + "\n") # Dump dictionary as JSON.

  def draw(self, _surface, _position): 

    def __load_svg(filename, _width):
      _svg = cairosvg.svg2svg(url = filename, dpi = (96 / (_width / 64))) # Convert svg to svg changing DPI to resize the image
      _bytes = cairosvg.svg2png(_svg)
      byte_io = io.BytesIO(_bytes)
      return pygame.image.load(byte_io)

    self.size = (self.width, self.height, ) = (self.width, (self.width + self.width // 6)) # Update size from width
    _buffer = pygame.Surface((self.width, self.height))
    _buffer.fill(pygame.Color(BACKGROUND_COLOUR))
    #_buffer.set_colorkey(pygame.Color(BACKGROUND_COLOUR))  # Background colour will not be blit.

    _image = __load_svg('./img/' + self.weather['current']['weather']['@icon'] + '.svg', self.width * 0.752)
    _left = (self.width - _image.get_width()) // 2
    _top = 0
    _buffer.blit(_image, (_left , _top - self.width // 16)) # Shifting the image up a little is a bit of a fudge but it looks better!
    
    _top = self.width // 24 * 15 # Use the icon height to work out how far to move down before displaying the temprature
    _font=pygame.font.Font(None, self.width // 3 ) # Display temprature in a font half the size of the weather symbol
    #_image = _font.render('%.1f' % round(float(self.weather['current']['temperature']['@value'])) + u'\u2103', True, pygame.Color(DARKTEXT_COLOUR)) # Display temprature using unicode symbol \u2103 for degrees C or \u2109 for degrees F
    _image = _font.render('%.0f' % round(float(self.weather['current']['temperature']['@value'])) + 'C', True, pygame.Color(DARKTEXT_COLOUR)) # Display temprature in C
    _left = (self.width - _image.get_width()) // 2
    _buffer.blit(_image, (_left , _top))
    
    _top += _image.get_height() # Use the previous image height to work out how far to move down before displaying the humidity
    _font=pygame.font.Font(None, self.width // 6 ) # Display humidity in a font a quarter of the height of the icon

    if _humidity :
      _image = _font.render(u'(' + ('%d' % float(self.weather['current']['humidity']['@value'])) + u'%)', True, pygame.Color(DARKTEXT_COLOUR)) # Display humidity
    else:
      _image = _font.render(self.weather['current']['weather']['@value'].title().replace('Intensity ', ''), True, pygame.Color(DARKTEXT_COLOUR)) # Display description
    _left = (self.width - _image.get_width()) // 2
    _buffer.blit(_image, (_left , _top))

    _top += _image.get_height() # Use the previous image height to work out how far to move down before displaying the location name
    _font=pygame.font.Font(None, self.width // 6 ) # Display location name in a font a quarter of the height of the icon
    
    _image = _font.render(self.weather['current']['city']['@name'], True, pygame.Color(DARKTEXT_COLOUR))
    _left = (self.width - _image.get_width()) // 2
    _buffer.blit(_image, (_left , _top))

    _surface.blit(_buffer, _position)
    del _buffer
  
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

  def _scan():
    event = pygame.event.poll() # Will return NOEVENT if there are no events in the queue.
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
      elif event.key == pygame.K_SPACE:
        return False
    elif event.type == pygame.MOUSEBUTTONUP:
      #sys.stderr.write (str(pygame.mouse.get_pos()) + '\n')
      return False
    elif event.type == pygame.MOUSEBUTTONDOWN:
      #sys.stderr.write (str(pygame.mouse.get_pos()) + '\n')
      pass
    return True

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
      _item = weather(288, _location, _appid) # Get the weather for the location (left, top, width, height)
      if not _item.status: # Only add it to the list of weather results if successful
        _weather.append(_item) 

    for _location in _locations[1:]:
      _item = weather(96, _location, _appid) # Get the weather for the location (left, top, width, height)
      if not _item.status: # Only add it to the list of weather results if successful
        if len(_weather) < 2: # Two icons should be no problem but 
          _weather.append(_item) 
        elif ((DISPLAY_SIZE)[0] // len(_weather) > 96): # check there is space for the icons before adding any more.
          _weather.append(_item) 
     
    pygame.init() 
    pygame.font.init()
    pygame.mouse.set_visible(False)

    _icon = pygame.Surface((32, 32)) # Create a blank icon (32 x 32) for the window
    _icon.fill(pygame.Color('black')) 
    _icon.set_colorkey(pygame.Color('black')) # Make it compleatly transparent
    pygame.display.set_icon(_icon) # Set it as the window's icon (or rather don't display an icon at all)
    pygame.display.set_caption(NAME) # Set window caption  

    _screen = pygame.display.set_mode((DISPLAY_SIZE))
    _screen.fill(pygame.Color('black'))
    _background = pygame.Surface((DISPLAY_SIZE)) # Create a drawing surface for the background    
    _background.fill(pygame.Color(BACKGROUND_COLOUR))
      
    _font=pygame.font.Font(None, 16)
    _logo = _font.render("Source - Open Weather", True, pygame.Color(TEXT_COLOUR))

    _now = time.time()
    _time = (_now - _now % INTERVAL) + INTERVAL
    
    while _scan(): # Wait for an event.

      _screen.blit(_background, (0, 0)) # Redrawing the background every time the display is updated fixes the transparency issue 
      _screen.blit(_logo, (_screen.get_width() -_logo.get_width() - 2, _screen.get_height() - _logo.get_height())) # Display the logo

      if len(_weather) > 0:
        _offset = _screen.get_width() // 2
        for _item in _weather[:1]: # Draw the first icon
          _item.width = 288
          _item.draw(_screen, (_offset - (_item.width // 2), 136))

        if len(_weather) > 1:
          _offset = (_screen.get_width() // (len(_weather) - 1)) // 2
          for _item in _weather[1:]: # Draw the icons
            _item.width = 96
            _item.draw(_screen, ((_offset - _item.width // 2), 8))        
            _offset += _screen.get_width() // (len(_weather) - 1)
          
      _now = time.time()
      
      if _time -_now <= 0:
        _time = (_now - _now % INTERVAL) + INTERVAL
        for _item in _weather: # Update the weather
          _item.update()

      pygame.display.flip()
      pygame.time.Clock().tick(FPS)

  except KeyboardInterrupt: # Ctrl-C
    pass
  except Exception: # Catch all other errors - otherwise the script will just fail silently!
    sys.stderr.write (traceback.format_exc())
    exit(1)

  exit(0)
