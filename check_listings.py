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
from bs4 import BeautifulSoup
import re, requests
from neighbourhoods import hoods, cities
import pandas as pd
import matplotlib.path as mplPath

#url = "http://vancouver.craigslist.ca/search/apa?format=rss&is_paid=all&max_price=2000&min_price=1000&postedToday=1"
url = "http://vancouver.craigslist.ca/search/apa?format=rss"
apts = feedparser.parse( url )
conn = sqlite3.connect('vancouver.db')
c = conn.cursor()

def parse_int(string):
    return int(re.sub('[^0-9]', '', string))
               
def get_title(soup):
    title= soup.find_all(id='titletextonly')[0]
    return title.find(text=True, recursive=False).strip()

def get_bedrooms(soup):
    try:
        bedrooms = soup.select('.housing')[0]
    except:
        bedrooms = None
    return bedrooms
    
def get_price(soup):
    try:
        item = soup.select('.price')[0]
        price_string = item.find(text=True, recursive=False).strip()
        price = int(re.sub('[^0-9]', '', price_string))
    except:
        price = None
    return price

def get_coordinates(tree):
    try:
        longitude = float(tree.xpath('//*[@id="map"]//@data-longitude')[0])
        latitude = float(tree.xpath('//*[@id="map"]//@data-latitude')[0])
    except:
        longitude = None
        latitude = None
    return [latitude,longitude]

def get_address(soup):
    try:
        address = soup.select('.mapaddress')[0].find(text=True, recursive=False).strip()
    except:
        address = None
    return address

def get_location_soup(soup):
    # get the location using soup
    div = soup.find_all(id="map")[0]
    longitude = 0
    latitude = 0
    return [latitude,longitude]

def get_bedrooms(soup):
    try:
        attr = soup.select('.attrgroup')[0]
        bedrooms = None
        for s in attr.strings:
            if s.find("BR") != -1:
                bedrooms = parse_int(s)
    except:
        bathrooms = None
    return bedrooms

def get_bathrooms(soup):
    try:
        attr = soup.select('.attrgroup')[0]
        bathrooms = None
        for s in attr.strings:
            if s.find("Ba") != -1:
                text = s.find("Ba")
                bathrooms = float(s[:text])
    except:
        bathrooms = None
    return bathrooms

def get_area(soup):
    try:
        attr = soup.select('.attrgroup')[0]
        area = None
        prev_s = None
        for s in attr.strings:
            if s.find("ft") != -1:
                area = parse_int(prev_s)
            prev_s = s
    except:
        area = None
    return area

def get_all_the_stuff(soup):
    try:
        attrs = soup.select('.attrgroup')
        stuff = []
        for attr in attrs:
            for s in attr.strings:
                if s.strip() !='':
                    stuff.append(s.strip())
        stuff = ','.join(stuff)
    except:
        stuff = None
    return stuff

def get_date_available(soup):
    try:
        tag = soup.select(".housing_movein_now")[0]
        date = tag.attrs['data-date']
    except:
        date = None
    return date

def get_neighbourhood(latitude,longitude):
    # or, grab small from postig title text
    try:
        neighbourhood = None
        for k,v in hoods.items():
            if mplPath.Path(v.values).contains_point((longitude,latitude)): # for some reason, files are long,lat
                neighbourhood = k
                break
            if neighbourhood == None:
                neighbourhood = re.sub('[()]', '', soup.select('.postingtitletext')[0].small.find(text=True, recursive=False).strip())
    except:
        neighbourhood = None
    return neighbourhood

def get_location(soup):
    location = None
    try:
        location = re.sub('[()]', '', soup.select('.postingtitletext')[0].small.find(text=True, recursive=False).strip())
    except:
        location = None
    return location

def get_city(latitude,longitude):
    selected_city = None
    try:
        for city, coords in cities.items():
            if mplPath.Path(coords.values).contains_point((longitude,latitude)) == True:
                selected_city = city
                break
    except:
        selected_city = None
    return selected_city
        
def extra_processor (extras):
    unit_type= None
    parking= None
    smoking= None
    pets= None
    laundry = None
    furnished = False
    try:
        details = extras.split(',')
        # Unit
        if 'apartment' in details:
            unit_type = 'apartment'
        if 'house' in details:
            unit_type = 'house'
        if 'townhouse' in details:
            unit_type = 'townhouse'
        if 'condo' in details:
            unit_type = 'condo'
        if 'furnished' in details:
            furnished = True
        
        # Parking
        if 'attached garage' in details:
            parking = 'garage'
        if 'detached garage' in details:
            parking = 'garage'
        if 'street parking' in details:
            parking = 'street parking'
        if 'off-street parking' in details:
            parking= 'off-street parking'
        if 'carport' in details:
            parking = 'carport'
            
        # Smoking
        if 'no smoking' in details:
            smoking = False
            
        # Pets
        if 'cats are OK - purrr' in details:
            pets = 'cats'
        if 'dogs are OK - wooof' in details:
            pets = 'cats'
        if ('dogs are OK - wooof' in details) and ('cats are OK - purrr' in details):
            pets = 'dogs+cats'
            
        # Laundry
        if 'laundry in bldg' in details:
            laundry = 'building'
        if 'laundry on site' in details:
            laundry = 'building'
        if 'w/d in unit' in details:
            laundry = 'unit'
    except:
        None
    return [unit_type, parking, smoking, pets, laundry, furnished]
    
for entry in reversed(apts.entries):
    # Grab some in info from the entry
    post_date = entry.updated
    post_id = entry.id
    title = entry.title
    print(post_date)
    print(post_id)
    # check if the entry is already in the database
    c.execute('SELECT * FROM apartments WHERE id = ? AND date = ?', [post_id,post_date])
    if c.fetchone():
        print("Already in db...")
    else:
        # Go get the page
        page = requests.get(entry.link)
        tree = html.fromstring(page.content)
        soup = BeautifulSoup(page.text, "html.parser")
        latitude,longitude = get_coordinates(tree)
        
        #if latitude == None or longitude == None:
        #    print("No lat-long, moving to next entry")
        #    continue
        
        address = get_address(soup)
        price = get_price(soup)
        area = get_area(soup)
        bedrooms = get_bedrooms(soup)
        bathrooms = get_bathrooms(soup)
        extras = get_all_the_stuff(soup)
        unit_type, parking, smoking, pets, laundry, furnished = extra_processor(extras)
        date_available = get_date_available(soup)
        neighbourhood = get_neighbourhood(latitude,longitude)
        location = get_location(soup)
        city = get_city(latitude,longitude)
        
        listing = [post_date, post_id, title, latitude, longitude, address, date_available, price, area, neighbourhood,location,extras,bedrooms,bathrooms,city]
        c.execute('INSERT INTO apartments VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [post_date, post_id, title, latitude, longitude, address, date_available, price, area, neighbourhood, extras, bedrooms, bathrooms, unit_type, parking, smoking, pets, laundry, furnished, city, location])
        conn.commit()
        print("Added entry %s to db" % post_id)
        time.sleep(5)
    

c.close()