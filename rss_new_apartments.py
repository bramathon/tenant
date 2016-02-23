# -*- coding: utf-8 -*-
#!/usr/bin/python3.4
"""
Created on Mon Jan 25 20:03:09 2016

@author: bram
"""

import feedparser
from lxml import html
import requests
import sqlite3
import time
import numpy as np
import matplotlib.path as mplPath

#url = "http://vancouver.craigslist.ca/search/apa?format=rss&is_paid=all&max_price=2000&min_price=1000&postedToday=1"
url = "http://vancouver.craigslist.ca/search/apa?format=rss"
apts = feedparser.parse( url )
conn = sqlite3.connect('/home/bram/Documents/craiglist_crawler/apartments.db')
c = conn.cursor()

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

west_end_poly = [[49.284327, -123.120926],
                [49.284571, -123.136547],
                [49.293172, -123.141782],
                [49.290177, -123.146889],
                [49.284187, -123.144143],
                [49.275788, -123.135817],
                [49.276852, -123.132470]]
                
west_end_path = mplPath.Path(np.array(west_end_poly))
                
downtown_poly = [[49.289977, -123.146357],
                [49.275646, -123.135676],
                [49.269468, -123.123416],
                [49.274299, -123.106301],
                [49.282852, -123.084937],
                [49.289502, -123.113220],
                [49.295004, -123.135918]]
                
downtown_path = mplPath.Path(np.array(downtown_poly))
                
# run once
# c.execute('''CREATE TABLE apartments (date text, id text, title text, latitude real, longitude real, address text, date_available text, price integer, area integer)''')

for entry in reversed(apts.entries):
    # Grab some in info from the entry
    post_date = entry.updated
    post_id = entry.id
    title = entry.title
    # check if the entry is already in the database
    
    c.execute('SELECT * FROM apartments WHERE id = ?', [post_id,])
    
    # if it's not, grab the new info
    if c.fetchone():
        print("Already in db...")
    else:
        # Go get the page
        page = requests.get(entry.link)
        tree = html.fromstring(page.content)
        # Extract useful bits from the page
        try: # critical info
            longitude = float(tree.xpath('//*[@id="map"]//@data-longitude')[0])
            latitude = float(tree.xpath('//*[@id="map"]//@data-latitude')[0])
        except:
            print("No lat-long, moving to next entry")
            continue
        if gastown_path.contains_point((latitude, longitude)):
            neighbourhood = "gastown"
        elif yaletown_path.contains_point((latitude, longitude)):
            neighbourhood = "yaletown"
        elif west_end_path.contains_point((latitude, longitude)):
            neighbourhood = "west end"
        elif downtown_path.contains_point((latitude, longitude)):
            neighbourhood = "downtown"
        else:
            neighbourhood = None
         # we can live without this stuff
        try: 
            address = tree.xpath('//*[@id="pagecontainer"]/section/section/div[1]/div[1]/div[2]/text()')[0] 
        except: address = None
        try: 
            date_available = tree.xpath('//*[@id="pagecontainer"]/section/section/div[1]/p[1]/span[3]/text()')[0] 
        except: date_available = None
        try: 
            area = int(tree.xpath('//*[@id="pagecontainer"]/section/section/div[1]/p[1]/span[2]/b/text()')[0]) 
        except: area = None
        try: 
            price = int(tree.xpath('//*[@id="pagecontainer"]/section/h2/span[2]/span[1]/text()')[0][1:]) 
        except: price = None
   
        # Save the entry to the database
        c.execute('INSERT INTO apartments VALUES (?,?,?,?,?,?,?,?,?,?)', [post_date, post_id, title, latitude, longitude, address, date_available, price, area, neighbourhood])
        conn.commit()
        print("Added entry %s to db" % post_id)
    time.sleep(5) 
    
c.close()

