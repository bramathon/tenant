# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 19:54:27 2016

@author: bram
"""

# select for apartments posted in the last 3 days, in gastown

import sqlite3
from datetime import timedelta, datetime
#import plotly
from geopy import distance
import matplotlib.path as mplPath
import numpy as np
import neighbourhoods
#from keys import gmail_password, my_email, destination_email

def find_similar_listings(latitude,longitude,area):
    # find similar listings for comparison (max 5)
    # need to weigh distance and area
    # should add parking to the db
    # units at exact address should be given priority
#    print('Locating apartments within about')
#    print(distance.distance((latitude,longitude),(latitude+0.0025,longitude))) # 0.0025 should be replaced by some statistical measure
    conn = sqlite3.connect('apartments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM apartments WHERE latitude < ? AND latitude > ? AND longitude < ? AND longitude > ?', (latitude + 0.0025,latitude-0.025,longitude+0.0025,longitude-0.0025))
    costs = []
    links = []
    for (date, link, description, lat, long, address, available, price, a, neighbourhood) in c.fetchall():
        links.append(link)
        if a and area:
            costs.append(distance.distance((lat,long),(latitude,longitude)).meters + abs(area - a))
        else:
            costs.append(distance.distance((lat,long),(latitude,longitude)).meters + 200) # 200 should be replaced by some statistical measure
    min_list = sorted(zip(links,costs), key=lambda t: t[1])
    return [i[0] for i in min_list[:5]] #return top five links
    
def send_email(user, pwd, recipient, subject, body):
    import smtplib

    gmail_user = my_email
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")
        

def gastown_filter(listing):
    # if a listing meets the requirements of the filter, send a notification
    # we should also grab the photos in this case (to do)
    # don't like this data structure at all, need something more robust, particularly as we plan to destruct extras into more useful fields
    post_date = listing[0]
    post_id  = listing[1]
    title  = listing[2]
    latitude  = listing[3]
    longitude = listing[4]
    address = listing[5]
    date_available = listing[6]
    price = listing[7]
    area = listing[8]
    neighbourhood = listing[9]
    extras = listing[10]
    
    if neighbourhood=='gastown' and price <2000:
        body = "Link: %s \n Address: %s \n Date Available: %s \n Price: %f \n Square Footage: %i \n Extra Info: %s" % (post_id,address,date_available,price,area,extras)
        send_email(my_email,gmail_password,destination_email,title,body)

#def extra_processor(extras):
#    # we collect a variable number of extra informations from the craigslist ad
#    # this includes cats, dogs, smoking, w/d and really lots of other random stuff

#def temp_function():
#    # function that is frequently rewritten to test stuff
#    conn = sqlite3.connect('/home/bram/Documents/craiglist_crawler/apartments.db')
#    c = conn.cursor()
#    c.execute('SELECT * FROM apartments WHERE price < 2000 AND price > 1900')
