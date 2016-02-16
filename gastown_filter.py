# -*- coding: utf-8 -*-
"""
Created on Sat Feb 13 15:31:26 2016

@author: bram
"""

import sqlite3
import matplotlib.path as mplPath
import googlemaps
import numpy as np

google_maps_key = "AIzaSyCC5u2Sl7CdEnX6UIjwLmnMglShafXcQQY"
google_places_key = "AIzaSyCjLdVxqxTC1raflH0gYefIDq-iAh08R6w"
gastown_place_id = "ChIJe_ROYXdxhlQRYYQ3bU2m_tE"
conn = sqlite3.connect('/home/bram/Documents/craiglist_crawler/apartments.db')
c = conn.cursor()

gmaps = googlemaps.Client(key=google_maps_key)
gplaces = googlemaps.Client(key=google_places_key) # we can get coordinates of the region centre roughly, but not the precise polygon

gmaps.reverse_geocode((40.714224, -73.961452))
gplaces.place("ChIJe_ROYXdxhlQRYYQ3bU2m_tE")


gastown_poly = [[49.285169, -123.110794],
                [49.284056, -123.111889],
                [49.282461, -123.109507],
                [49.281453, -123.104325],
                [49.281320, -123.099615],
                [49.284525, -123.099486],
                [49.283937, -123.103778]]

gastown_path = mplPath.Path(np.array(gastown_poly))

yaletown_poly = [[49.273360, -123.127174],
                [49.280032, -123.117933],
                [49.277490, -123.113921],
                [49.271946, -123.121324]]
                
yaletown_path = mplPath.Path(np.array(yaletown_poly))

c.execute('SELECT * FROM apartments ')

for (date, link, description, lat, long, address, available, price, area) in c.fetchall():
    print ([lat,long])
    if gastown_path.contains_point((lat, long)):
        print("Gastown Apartment: " + link)
    if yaletown_path.contains_point((lat, long)):
        print("Yaletown Apartment: " + link)
        

c.close()