from geopy import geocoders
import time 
import pickle

class Location(object):
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

    def __init__(self, **kwargs):
        if self.persistent:
            try:
                with open(".geocache.pickle", "r") as f:
                    self.cache = pickle.load(f)
            except IOError:
                self.cache = {}

    def code_this(self, placename):
        """
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
            location = self.get_location(self.code(placename))
            self.cache[placename] = location
            with open(".geocache.pickle", "w") as f:
                pickle.dump(self.cache, f)
        return location
        
    def code_list(self, placenames):
        """
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
            time.sleep(self.sleep_interval) # Avoid rate-limiting.
            locations[name] = self.code_this(name)
            
        return locations
    
class GoogleCoder(BaseCoder):
    coder = geocoders.GoogleV3()
    code = coder.geocode
    
    def get_location(self, response):
        """
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

