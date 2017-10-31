
# coding: utf-8

# In[17]:

import numpy as np
import pandas as pd
import sqlite3
from plotly import __version__
#import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import *
import calendar
from neighbourhoods import hoods
init_notebook_mode()


# In[2]:

def extra_processor (extras):
    unit_type= None
    parking= None
    smoking= False
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
        
        # furnished
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
            
        # Laundry
        if 'laundry in bldg' in details:
            laundry = 'building'
        if 'laundry on site' in details:
            laundry = 'building'
        if 'w/d in unit' in details:
            laundry = 'unit'
    except:
        None
    return [unit_type, parking, smoking, pets, laundry,furnished]
    


# In[22]:

conn = sqlite3.connect('apartments.db')
c = conn.cursor()

def table_change():
    c.execute("ALTER TABLE 'main'.'apartments' ADD COLUMN 'unit_type' TEXT")
    c.execute("ALTER TABLE 'main'.'apartments' ADD COLUMN 'parking' TEXT")
    c.execute("ALTER TABLE 'main'.'apartments' ADD COLUMN 'smoking' BOOL")
    c.execute("ALTER TABLE 'main'.'apartments' ADD COLUMN 'pets' TEXT")
    c.execute("ALTER TABLE 'main'.'apartments' ADD COLUMN 'laundry' TEXT")
    c.execute("DELETE FROM apartments WHERE date(date) < date('2017-06-15))")

def update_record_extras(df):
    record_id = df['id']
    unit_type,parking,smoking,pets,laundry,furnished = extra_processor(df['extras'])
    #c = conn.cursor()
    c.execute('UPDATE apartments SET unit_type=?, parking=?, smoking=?, pets=?, laundry=?, furnished=? WHERE id=?', (unit_type,parking,smoking,pets,laundry,furnished,record_id))
    #.execute("UPDATE apartments SET unit_type=? WHERE id=?", (unit_type,record_id))
    
def process_extras():
    # this function modifies the database!!!

    # start date of data is June 15, 2017
    # ALTER TABLE "main"."apartments" ADD COLUMN "unit_type" TEXT
    # ALTER TABLE "main"."apartments" ADD COLUMN "parking" TEXT
    # ALTER TABLE "main"."apartments" ADD COLUMN "smoking" BOOL
    # ALTER TABLE "main"."apartments" ADD COLUMN "pets" TEXT
    # ALTER TABLE "main"."apartments" ADD COLUMN "laundry" TEXT
    
    sql = "SELECT extras,id FROM apartments WHERE date(date) > date('2017-10-19');"
    df = pd.read_sql_query(sql,conn)
    length = df.shape[0]
    five_percent = int(length/20)
    progress = 0
    for i, data in df.iterrows():
        if (i % five_percent) == 0:
              progress = int(i*100/length)
              print("{}%".format(progress))
        update_record_extras(data)
    print("Finished!")
    #df.apply(update_record_extras,axis=1)


# In[ ]:

process_extras()


# In[154]:




# In[ ]:



