"""
This module provides classes for geocoding bibliographic data.

Each geocoder class should be based on :class:`.BaseCoder`\, and provide
``code`` and ``get_location`` methods that can be used by 
:func:`BaseCoder.code_this` and :func:`BaseCoder.code_list`\.

:class:`.BaseCoder` should **not** be used directly. Instead, instantiate a
child class, e.g. :class:`.GoogleCoder`\. For example:

.. code-block:: python

   >>> from tethne.services.geocode import GoogleCoder
   >>> google = GoogleCoder()
   >>> location = google.code_this("Marine Biological Laboratory")
   >>> location
   <tethne.services.geocode.Location object at 0x10153af10>

   >>> location.__dict__
   {'latitude': 41.5250098, 'place': u'Marine Biological Laboratory, 7 M B L Street, Woods Hole, MA 02543, USA', 'longitude': -70.6712845}
   
To avoid making redundant and costly requests, :class:`.BaseCoder` implements a
rather crude cacheing system, using ``Pickle``. Previous results are held in
memory until the :class:`.BaseCoder` is destroyed, at which time the
placename-:class:`.Location` mapping is pickled in the current working directory
as ``.geocache.pickle``. Disable by setting ``persistent`` to ``False``.

``sleep_interval`` determines the wait (in seconds) between API calls, to avoid 
triggering rate-limiting.

.. autosummary::

   Location
   BaseCoder
   GoogleCoder
   YahooCoder

"""

from geopy import geocoders
from geopy.exc import GeocoderTimedOut
import time 
import pickle
from ssl import SSLError

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

class Location(object):
    """
    Minimal geographic datum yielded by geocoders.
    """

    place = ""
    latitude = 0.
    longitude = 0.
    
    def __init__(self, place="", latitude=0., longitude=0., **kwargs):
        self.place = place
        self.latitude = latitude
        self.longitude = longitude

class BaseCoder(object):
    """
    Base class for geocoders.
    """
    persistent = True   # Triggers on-disk cacheing with Pickle
    sleep_interval = 0.5    # Avoid rate-limiting. Adjust as desired.
    timeout = 3         # Duration in seconds until timeout.
    max_tries = 3       # How many times to re-try after a timeout.

    def __init__(self, **kwargs):
        if self.persistent:
            try:
                with open(".geocache.pickle", "r") as f:
                    self.cache = pickle.load(f)
            except IOError:
                self.cache = {}
                
    def __del__(self):
        with open(".geocache.pickle", "w") as f:
            pickle.dump(self.cache, f)

    def code_this(self, placename):
        """
        Retrieve a :class:`.Location` for a placename.
        
        Parameters
        ----------
        placename : str or unicode
        
        Returns
        -------
        location : :class:`.Location`
        """
        
        if type(placename) not in [str, unicode]:
            raise ValueError("Encountered non-string in placenames list.")
        try:    # Check the cache first.
            location = self.cache[placename]
        except KeyError:    # Not in the cache, call the service.
            tries = 0
            hope = True
            while hope:
                try:
                    time.sleep(self.sleep_interval) # Avoid rate-limiting.
                    location = self.get_location(self.code(placename))
                    self.cache[placename] = location
                    hope = False
                except (GeocoderTimedOut, SSLError):
                    logger.warning("Geocoder timed out for {0}. Retrying."
                                                             .format(placename))
                    if tries >= self.max_tries:
                        location = None
                        hope = False
                        logger.warning("Geocoder gave up for {0}."
                                                             .format(placename))
                    else:
                        tries += 1
                except:
                    pass    # TODO: What else could go wrong?
        return location
        
    def code_list(self, placenames):
        """
        Retrieve :class:`.Location` for a list of placenames.
        
        Parameters
        ----------
        placenames : list
        
        Returns
        -------
        locations : dict
            Placename - :class:`.Location` mapping.
        """

        locations = {}
        for name in placenames:
            locations[name] = self.code_this(name)
            
        return locations
    
class GoogleCoder(BaseCoder):
    """
    Uses the Google Geocoding API, via the ``geopy.geocoders.GoogleV3`` coder.
    """

    coder = geocoders.GoogleV3(timeout=3)
    code = coder.geocode
    
    def get_location(self, response):
        """
        Yields :class:`.Location` based on a response from Google Geocoding API.
        
        Parameters
        ----------
        response : tuple
            GoogleV3 geocoder response: (u'Name', (Lat, Lon))
        
        Returns
        -------
        location : :class:`.Location`
        """
        if response is None: return None

        return Location(place=response[0], 
                        latitude=response[1][0],
                        longitude=response[1][1])

class YahooCoder(BaseCoder):
    """
    Uses the Yahoo PlaceMaker API.
    """

    yahoo_base = "http://where.yahooapis.com/v1/places"

    lat_searchpath = ".//{http://where.yahooapis.com/v1/schema.rng}centroid/" +\
                     "{http://where.yahooapis.com/v1/schema.rng}latitude"
    lon_searchpath = ".//{http://where.yahooapis.com/v1/schema.rng}centroid/" +\
                     "{http://where.yahooapis.com/v1/schema.rng}longitude"
    name_searchpath = ".//{http://where.yahooapis.com/v1/schema.rng}name"
    
    def __init__(self, yahoo_id, **kwargs):
        self.yahoo_id = yahoo_id
        super(YahooCoder, self).__init__(self, **kwargs)
    
    def code(self, name):
        """
        Constructs and sends a Yahoo PlaceMaker API query.
        
        Parameters
        ----------
        name : string
        
        Returns
        -------
        HTTPResponse
        """
        import urllib2
        
        rpath = "{0}.q('{1}')?appid={2}".format(self.yahoo_base,
                                                urllib2.quote(name),
                                                self.yahoo_id)
        return urllib2.urlopen(rpath).read()
    
    def get_location(self, response):
        """
        Yields :class:`.Location` based on a response from Yahoo PlaceMaker API.
                
        Parameters
        ----------
        response : HTTPResponse
        
        Returns
        -------
        location : :class:`.Location`
        """
        
        import xml.etree.ElementTree as ET

        rx = ET.fromstring(response)
        try:
            lat = float(rx.findall(self.lat_searchpath)[0].text)
            lon = float(rx.findall(self.lon_searchpath)[0].text)
            
            place = str(rx.findall(self.name_searchpath)[0].text)
        except IndexError:
            return None     # Nothing found.

        return Location(place=place,
                        latitude=lat,
                        longitude=lon)

