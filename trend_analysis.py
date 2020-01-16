#!/usr/bin/env python
# coding: utf-8

# # Trend analysis notebook
# 
# This notebook produces the monhtly trend plots for the Vancouver rental market. Including:
# 1. Median Rent for Vancouver and GVRD (back to Feb 2016)
# 2. Median Rent per square foot for Vancouver and GVRD
# 3. Median Rent per square foot, broken out by bedrooms (Vancouver)
# 4. Composition of Bedrooms
# 5. Composition of Unit Types
# 6. Composition of Furnished
# 7. Composition of City
# 
# ## To Do
# * Possibly reduce number of cities reported
# * Decide what to do with furnished vs non-furnished
# 
# To run the script, first make sure any notebook-specific stuff is commented out, then run 
# 
# > ```jupyter nbconvert --to script trend_analysis.ipynb```
# 
# > ```python trend_analysis.py "/home/bram/Documents/blog/content/post/" ```

# In[ ]:


import numpy as np
import pandas as pd
import sqlite3
import sys
from analysis_functions import median_rent, median_rent_psf, insert_plot, remove_price_outliers
from trends import generate_months, median_price_trend, monthly_trend, get_all_listing_for_month
import calendar
import datetime
import math
import os

from plotly import __version__
import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import *
from plotly import tools

from params import blog_dir, this_month, output
#init_notebook_mode()


# In[ ]:


# Generate the data directory
# to run a different month than current, just do it from the notebook

# months = generate_months()
# if not os.path.exists("data"):
#     os.mkdir("data")
# data_dir = "data/"+months[-1]+"/"
# if not os.path.exists(data_dir):
#     os.mkdir(data_dir)


# In[ ]:


# Global Parameters

today = datetime.date.today()

if this_month == None:
    months = generate_months()
    this_month = months[-1]
else:
    months = generate_months(enddate=datetime.date(int(this_month[:4]),int(this_month[5:7]),1))
    
def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

if is_interactive():
    notebook = True 
    init_notebook_mode()
else:
    notebook = False


# In[ ]:


year = int(this_month[:4])
mm = int(this_month[5:])

# we analyze entire months at once, so we have to decide on a day. I've chosen the last day of that month
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

post_date = str(last_day_of_month(datetime.date(year,mm,1)))# if mm != 12 else str(datetime.date(year,1,1))

print("Analyzing data up to {}".format(this_month))

month_names = {1: 'January',
               2: 'February',
               3: 'March',
               4: 'April',
               5: 'May',
               6: 'June',
               7: 'July',
               8: 'August',
               9: 'September',
               10: 'October',
               11: 'November',
               12: 'December'
              }

if output == True:
    report_file = blog_dir+month_names[int(this_month[5:7])]+ '-' + this_month[0:4]+"_trends.md"
    f = open(report_file, "w")

    print("---",file=f)

    print("title: Rent Trends - {}".format(month_names[int(this_month[5:7])] + ', ' + this_month[0:4]),file=f)
    print("date: {}".format(post_date),file=f)
    print("draft: False",file=f)
    print("writer: 'Bram'",file=f)
    print("showonlyimage: true",file=f)
    print("image: 'img/{}.jpg'".format(this_month),file=f)
    print("description: My Analysis of monthly trends in Vancouver's rental housing market",file=f)
    print("---",file=f)
    
    print("",file=f)
    print("This post shows the trends in the Vancouver rental market. Series is from from June, 2017 to today",file=f)
    
    print("",file=f)
    print("<!--more-->",file=f)
    
    print("<div>",file=f)
    print("<script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>",file=f)
    print("</div>",file=f)


# In[ ]:


## Median rent trend
# This the broadest metric

print("Analyzing Median Price...")

gvrd_months, gvrd_med_price, gvrd_unc = median_price_trend(months,)
van_months, van_med_price, van_unc = median_price_trend(months,city='Vancouver')

# Plotting
data = [Scatter(x=van_months, 
                y=van_med_price,
                name="Vancouver",
                error_y=dict(type='data',
                             array=van_unc,
                             visible=True)),
        Scatter(x=gvrd_months, 
                y=gvrd_med_price,
                name="GVRD",
                error_y=dict(type='data',
                             array=gvrd_unc,
                             visible=True))
       ]
layout = Layout(dict(title = 'Median Rent for Apartments',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Median Price ($)'),))
fig = dict(data=data,layout=layout)
median_rent_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
if output == True:
    print("",file=f)
    print("## Median rent trend",file=f)
    print("",file=f)
    print("This figure shows the median rent of all listings in Vancouver and the GVRD as long as far back as the data goes. It's the broadest possible statistic\n",file=f)
    print("",file=f)
    print(median_rent_trend,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Median Rent psf

print("Analyzing Median Price Per Square Foot...")

gvrd_months, gvrd_med_price, gvrd_unc = monthly_trend(months,metric=median_rent_psf)
van_months, van_med_price, van_unc = monthly_trend(months,metric=median_rent_psf,select=lambda df: df.loc[df['City'] == 'Vancouver'])

# Plotting
data = [Scatter(x=van_months, 
                y=van_med_price,
                name="Vancouver",
                error_y=dict(type='data',
                             array=van_unc,
                             visible=True)),
        Scatter(x=gvrd_months, 
                y=gvrd_med_price,
                name="GVRD",
                error_y=dict(type='data',
                             array=gvrd_unc,
                             visible=True))
       ]
layout = Layout(dict(title = 'Median Rent for Apartments',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Median Price ($)'),))
fig = dict(data=data,layout=layout)
median_rent_psf_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Median rent per square foot trend",file=f)
    print("",file=f)
    print("This figure shows the median rent per square foot of all listings in Vancouver and the GVRD. If the median unit size is decreasing, it may appear that rents are falling. Examining rent per square foot can therefore be a more useful statistic to determine the direction of the rental market\n",file=f)
    print("",file=f)
    print(median_rent_psf_trend,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Rents by bedroom
print("Analyzing Median broken out by bedrooms...")

data = []
for bedroom in [0,1,2,3,4]:
    month_nums, med_price, unc = monthly_trend(months,metric=median_rent,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['bedrooms'] == bedroom)])
    trace = Scatter(x = month_nums,
                    y = med_price,
                    name = "{} bedroom".format(bedroom),
                    error_y = dict(type='data',
                                   array = unc,
                                   visible = True
                                  )
                   )
    data.append(trace)

# Plotting
layout = Layout(dict(title = 'Median Rent for an apartment by number of bedrooms (Vancouver)',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Median Price ($)'),))
fig = dict(data=data,layout=layout)
median_rent_trend_by_bedrooms = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Median rent trend broken out by bedrooms",file=f)
    print("",file=f)
    print("This figure shows the median rent of all listings, broken out by number of bedrooms, in Vancouver and the GVRD.\n",file=f)
    print("",file=f)
    print(median_rent_trend_by_bedrooms,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Rent per square foot by bedroom
print("Analyzing Median Price Per Square Foot, broken out by bedrooms...")

data = []
for bedroom in [0,1,2,3,4]:
    month_nums, med_price, unc = monthly_trend(months,metric=median_rent_psf,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['bedrooms'] == bedroom)])
    trace = Scatter(x = month_nums,
                    y = med_price,
                    name = "{} bedroom".format(bedroom),
                    error_y = dict(type='data',
                                   array = unc,
                                   visible = True
                                  )
                   )
    data.append(trace)

# Plotting
layout = Layout(dict(title = 'Median Rent per square foot for an apartment by number of bedrooms (Vancouver)',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Median Price ($)'),))
fig = dict(data=data,layout=layout)
median_rent_psf_trend_by_bedrooms = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Median rent per square foot trend broken out by bedrooms",file=f)
    print("",file=f)
    print("This figure shows the median rent per square foot of all listings, broken out by number of bedrooms, in Vancouver and the GVRD.\n",file=f)
    print("",file=f)
    print(median_rent_psf_trend_by_bedrooms,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Makeup of bedrooms over time
print("Analyzing Bedrooms Composition...")

data = []
def count(df):
    total_number = df.shape[0]
    if total_number == 0:
        total_number = np.nan
    return total_number, 0.0

month_nums, num_listings_total, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['bedrooms'] >= 0) & (df['bedrooms'] <= 5)])

for bedroom in [0,1,2,3,4,5]:
    month_nums, num_listings, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['bedrooms'] == bedroom)])
    trace = dict(x = month_nums,
                 y=np.array(num_listings)/np.array(num_listings_total),
                 name = "{} bedroom".format(bedroom),
                 stackgroup='one')
    data.append(trace)

# Plotting
layout = Layout(dict(title = 'Proportion of listings by number of bedrooms (Vancouver)',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Percentage of Listings',
                                 tickformat=',.0%',
                                 range= [0,1]),))
fig = dict(data=data,layout=layout)
bedroom_composition_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Bedrooms composition trend",file=f)
    print("",file=f)
    print("This figure shows composition of bedrooms within Vancouver over time. This will indicate if the market is shifting towards homes with fewer bedrooms, as might be expected \n",file=f)
    print("",file=f)
    print(bedroom_composition_trend,file=f)

if notebook == True:
    iplot(fig)


# In[ ]:


## Makeup of unit types over time
print("Analyzing Unit Type Composition...")

data = []
def count(df):
    total_number = df.shape[0]
    if total_number == 0:
        total_number = np.nan
    return total_number, 0.0

month_nums, num_listings_total, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['unit_type'].notnull())])

for unit_type in ['apartment','townhouse','house','condo']:
    month_nums, num_listings, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['unit_type'] == unit_type)])
    trace = dict(x = month_nums,
                 y=np.array(num_listings)/np.array(num_listings_total),
                 name = unit_type,
                 stackgroup='one')
    data.append(trace)

# Plotting
layout = Layout(dict(title = 'Proportion of listings by unit type (Vancouver)',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Percentage of Listings',
                                 tickformat=',.0%',
                                 range= [0,1]),))
fig = dict(data=data,layout=layout)
unit_type_composition_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Unit type composition trend",file=f)
    print("",file=f)
    print("This figure shows composition of unit types within Vancouver over time. Craigslist specifies 4 unit types: houses, townhouses, apartments and condos. It's up to the poster to select one of these options and entirely subjective so trends will be difficult to interpret. One could speculator that apartments are more often purpose-built rental, while condos are strata units rented on the aftermarket. The extremely small share of townhouses is notable. Basement suites are also unclear, they could be under houses, or apartments.\n",file=f)
    print("",file=f)
    print(unit_type_composition_trend,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Makeup of furnished vs unfurnished
print("Analyzing Furnished Composition")

data = []
def count(df):
    total_number = df.shape[0]
    if total_number == 0:
        total_number = np.nan
    return total_number, 0.0

month_nums, num_listings_total, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver')])

for furnished in [0,1]:
    month_nums, num_listings, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == 'Vancouver') & (df['furnished'] == furnished)])
    trace = dict(x = month_nums,
                 y=np.array(num_listings)/np.array(num_listings_total),
                 name = 'furnished' if furnished == 1 else 'unfurnished',
                 stackgroup='one')
    data.append(trace)

airbnb = Scatter(x=['2018-09'],
                 y=[0.642],
                 mode='markers+text',
                 name='Airbnb regulation',
                 text=['Airbnb regulated'],
                 textposition='top right'
                )

data.append(airbnb)

# Plotting
layout = Layout(dict(title = 'Proportion of furnished listings (Vancouver)',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Percentage of Listings',
                                 tickformat=',.0%',
                                 range= [0,1]),))
fig = dict(data=data,layout=layout)
furnished_composition_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

if output == True:
    print("",file=f)
    print("## Furnished composition trend",file=f)
    print("",file=f)
    print("This figure shows the composition of furnished vs unfurnished units in Vancouver. It also indicates the date which new regulations reuslted in the delisting of thousands of units from airbnb. We may expect to see an increase in furnished units as these airbnbs return to the long term rental market\n",file=f)
    print("",file=f)
    print(furnished_composition_trend,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:


## Makeup of listing by city
print("Analyzing City Composition...")

data = []
def count(df):
    total_number = df.shape[0]
    if total_number == 0:
        total_number = np.nan
    return total_number, 0.0

all_month_nums, num_listings_total, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'].notnull())])

cities = ['Vancouver', 'New Westminster', 'Coquitlam', 'Burnaby',
       'West Vancouver', 'Surrey', 'Richmond', 'Electoral Area A',
       'North Vancouver District', 'Langley Township',
       'North Vancouver City', 'Delta', 'Port Coquitlam', 'Pitt Meadows',
       'White Rock', 'Maple Ridge', 'Port Moody', 'Anmore',
       'Langley City', 'Belcarra', 'Tsawwassen First Nation']
for city in cities:
    month_nums, num_listings, unc = monthly_trend(months,metric=count,select=lambda df: df.loc[(df['City'] == city)])
    y=[]
    for m,total in zip(all_month_nums,num_listings_total):
        if m in month_nums:
            y.append(num_listings[month_nums.index(m)]/total)
        
    trace = dict(x = month_nums,
                 y=y,
                 name = city,
                 stackgroup='one')
    data.append(trace)

# Plotting
layout = Layout(dict(title = 'Proportion of listings by city',
                     xaxis = dict(title = 'Month'),
                     yaxis = dict(title = 'Percentage of Listings',
                                 tickformat=',.0%',
                                 range= [0,1]),))
fig = dict(data=data,layout=layout)
city_composition_trend = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
    
if output == True:
    print("",file=f)
    print("## City composition trend",file=f)
    print("",file=f)
    print("This figure shows the composition of listings in each municipal area. Vancouver clearly dominates the rental market, despite containing a relatively smaller fraction of the region's population\n",file=f)
    print("",file=f)
    print(city_composition_trend,file=f)
    
if notebook == True:
    iplot(fig)


# In[ ]:





# In[ ]:




