#!/usr/bin/env python
# coding: utf-8

# # Monthly Analysis Notebook
# To use:
# > jupyter nbconvert --to script monthly_analysis.ipynb
# 
# > python monthly_analysis.py "/home/bram/Documents/blog/content/post/" "2018-12"
# 

# In[2]:


import numpy as np
import pandas as pd
import sqlite3
from analysis_functions import remove_price_outliers,remove_area_outliers,insert_plot
import datetime
from trends import get_all_listing_for_month
import os
from tabulate import tabulate
import colorlover as cl
import sys


from plotly import __version__
import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import *
from plotly import tools

from keys import mapbox_access_token
from params import blog_dir, this_month, output


from neighbourhoods import hoods, cities


# In[3]:


today = datetime.date.today()

if this_month == None:
    this_month = str(datetime.date(today.year,today.month,1))[:7]

def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

if is_interactive():
    notebook = True 
    init_notebook_mode()
else:
    notebook = False


# In[4]:


## Mapping

year = int(this_month[:4])
mm = int(this_month[5:])

if mm == 1:
    last_month = str(datetime.date(year-1,12,1))[:7]
else:
    last_month = str(datetime.date(year,mm-1,1))[:7]
    
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

month_name = month_names[int(this_month[5:7])]

# Generate the data directory
if not os.path.exists("data"):
    os.mkdir("data")
data_dir = "data/"+this_month+"/"
if not os.path.exists(data_dir):
    os.mkdir(data_dir)
    
year = str(year)

if output == True:
    report_file = blog_dir+"{}-{}_report.md".format(month_name,year)
    f = open(report_file, "w")

    print("---",file=f)
    print("title: Vancouver Monthly Rental Report {}".format(month_name + ', ' + year),file=f)
    print("date: {}".format(str(datetime.date.today())),file=f)
    print("draft: False",file=f)
    print("description: Monthly rental housing report for {}".format(month_name + ', ' + year),file=f)
    print("featuredImage: \"/img/{}.jpg\"".format(this_month),file=f)
    print("---",file=f)

    print("",file=f)
    print("This post shows the monthly breakdown for Vancouver rents in {}".format(month_name),file=f)

    print("<div>",file=f)
    print("<script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>",file=f)
    print("</div>",file=f)
    print("",file=f)


# In[5]:


def get_all_listing_for_month(month):
    # unfurnished listings filtered for outliers in price
    conn = sqlite3.connect('apartments.db')
    c = conn.cursor()
    sql = "SELECT * FROM apartments WHERE strftime(\"%Y-%m\", date) = '{}'".format(month)
    df = pd.read_sql_query(sql,conn)
    conn.close()
    return df


# In[6]:


prev_data = get_all_listing_for_month(last_month)
raw_data = get_all_listing_for_month(this_month)


# ## Metrics
# 
# 1. Median Rent
# This plot should show the distribution of median rent compared to last month's
# It should also produce a summary of the change and the characteristics of the median apartment
# 2. Median Rent by bedroom
# This plot should show 
# 3. Median Rent psf
# 4. Neighbourhood breakdown
# 5. Comparison to previous months
# 6. Maps
# 

# In[7]:


# Median Rent
price_data = remove_price_outliers(raw_data)
prev_price_data = remove_price_outliers(prev_data)
bin_size = 100
data = [Histogram(x=price_data['price'],
                  name='Apartments',
                  histnorm='probability',
                  xbins=dict(start=500,end=7000,size=bin_size)
         )]
median_price = price_data['price'].median()
mean_price = price_data['price'].mean()
prev_median_price = prev_price_data['price'].median()
prev_mean_price = prev_price_data['price'].mean()
median_price_bin_height = price_data.loc[(price_data['price'] >= round(median_price - bin_size/2 + 1,-2))
                                         & (price_data['price'] < round(median_price + bin_size/2 + 1,-2))].shape[0]/price_data.shape[0]
mean_price_bin_height = price_data.loc[(price_data['price'] >= round(mean_price - bin_size/2 + 0.001,-2))
                                         & (price_data['price'] < round(mean_price + bin_size/2,-2))].shape[0]/price_data.shape[0]

data.append(Bar(x=[median_price],
                y=[median_price_bin_height],
                width=bin_size/5,
                name='Median'))

data.append(Bar(x=[mean_price],
                y=[mean_price_bin_height],
                width=bin_size/5,
                name='Mean'))

layout=Layout(dict(title='Rents for {}, {}'.format(month_name,year),
                     xaxis = dict(title = 'Price ($)'),
                   barmode='overlay',
                     yaxis = dict(title = 'Number of Listings',tickformat=',.0%')))
fig = dict(data=data,layout=layout)
if notebook:
    iplot(fig)
if output:
    rent_dist = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

## Report
if output:
    print("## Overall average rent",file=f)
    print("This figure shows the distribution of rents across all metro Vancouver craigslist listings",file=f)
    print("",file=f)

    print(tabulate([['This Month',median_price, mean_price,round(100*(mean_price-prev_mean_price)/prev_mean_price,1)],
                    ['Last Month',prev_median_price,prev_mean_price,""]],
               headers=[' ','Median Rent','Mean Rent','% Change'],
               tablefmt='pipe'),file=f)
    print(rent_dist,file=f)


# In[8]:


price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))
price_hist = []
utype_medians={}
for utype in ['apartment','house','condo','townhouse']:
    df_type = price_psf_data[price_psf_data.unit_type == utype]
    utype_medians[utype] = df_type['price'].median()
    price_hist.append(Histogram(x=df_type['price'],name=utype,xbins=dict(start=500,end=5000,size=100),histnorm='probability',opacity=0.75))
layout=Layout(dict(title='Rents for {}, {}, broken out by unit type'.format(month_name,year),
                   barmode='overlay',
                   xaxis = dict(title = 'Price',tickprefix='$'),
                   yaxis = dict(title = 'Percentage of Listings',
                   tickformat=',.0%')))
fig=dict(data=price_hist,layout=layout)
if notebook:
    iplot(fig)
if output:
    rent_dist_utype = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')

## Report

if output:
    print("## Rent by unit type",file=f)
    print("This figure shows the distribution of rents for each unit type. I've normalized each histogram to emphasize the price distirbution of different unit types",file=f)
    print("",file=f)
    print(tabulate([['Median Price:',utype_medians['condo'],utype_medians['apartment'],
                     utype_medians['townhouse'],utype_medians['house']]],
                   headers=[' ','Condo','Apartment','House','Townhouse'],
                   tablefmt='pipe'),file=f)
    print(rent_dist_utype,file=f)


# In[9]:


price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))
price_hist = []
utype_psf_medians={}
for utype in ['apartment','house','condo','townhouse']:
    df_type = price_psf_data[price_psf_data.unit_type == utype]
    ppsq = (df_type['price']/df_type['area'])
    utype_psf_medians[utype] = round(ppsq.median(),2)
    price_hist.append(Histogram(x=ppsq,name=utype,xbins=dict(start=0,end=5,size=0.1),histnorm='probability',opacity=0.75))
layout=Layout(dict(title='Rent per square foot for {}, {}, broken out by unit type'.format(month_name,year),
                   barmode='overlay',
                   xaxis = dict(title = 'Price per square foot',tickprefix='$'),
                   yaxis = dict(title = 'Percentage of Listings',tickformat=',.0%')))
fig=dict(data=price_hist,layout=layout)
if notebook:
    iplot(fig)
if output:
    rent_psf_dist_utype = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
    
## Report
if output:
    print("## Rent per square foot by unit type",file=f)
    print("This figure shows the distribution of rent per square for each unit type. I've normalized each histogram to emphasize the price distirbution of different unit types. It's also worth noting that larger units typically have a lower rent per square foot, so this may reflect a difference in size more than quality",file=f)
    print("",file=f)
    print(tabulate([['Median Price:',utype_psf_medians['condo'],utype_psf_medians['apartment'],
                     utype_psf_medians['townhouse'],utype_psf_medians['house']]],
                   headers=[' ','Condo','Apartment','House','Townhouse'],
                   tablefmt='pipe'),file=f)

    print(rent_psf_dist_utype,file=f)
    print(".",file=f)


# In[10]:


# rent by unit-type non normalized distruibution
price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))
price_hist = []
for utype in ['apartment','house','condo','townhouse']:
    df_type = price_psf_data[price_psf_data.unit_type == utype]
    price_hist.append(Histogram(x=df_type['price'],name=utype,xbins=dict(start=500,end=5000,size=100),))
layout=Layout(dict(title='Rents for {}, {}, broken out by unit type'.format(month_name,year),
                   barmode='overlay',
                   xaxis = dict(title = 'Price',tickprefix='$'),
                   yaxis = dict(title = 'Number of Listings')))
fig=dict(data=price_hist,layout=layout)
if notebook:
    iplot(fig)
if output:
    rent_dist_utype_breakdown = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')


# In[11]:


# per square foot non normalized distribution
price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))
price_hist = []
for utype in ['apartment','house','condo','townhouse']:
    df_type = price_psf_data[price_psf_data.unit_type == utype]
    ppsq = (df_type['price']/df_type['area'])
    price_hist.append(Histogram(x=ppsq,name=utype,xbins=dict(start=0,end=5,size=0.1)))
layout=Layout(dict(title='Rent per square foot for {}, {}, broken out by unit type'.format(month_name,year),
                   barmode='overlay',
                   xaxis = dict(title = 'Price per square foot',tickprefix='$'),
                   yaxis = dict(title = 'Number of Listings')))
fig=dict(data=price_hist,layout=layout)
if notebook:
    iplot(fig)
if output:
    rent_psf_dist_utype_breakdown = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')


# In[12]:


# Mapping
def unit_description(row):
    if (not np.isnan(row['bedrooms'])) and (row['unit_type'] != None):
        return "{} bedroom {}, ${}".format(int(row['bedrooms']),row['unit_type'], row['price'])
    elif (not np.isnan(row['bedrooms'])):
        return "{} bedroom, ${}".format(int(row['bedrooms']), row['price'])
    else:
        return "${}".format(row['price'])


# In[13]:


price_data = remove_price_outliers(raw_data)
price = price_data['price']
info = price_data.apply(lambda row: unit_description(row), axis=1).values.tolist()
colorscale = list(zip(np.linspace(0.0,1.0,num=11),cl.scales['11']['div']['RdYlBu'][::-1]))

data = Scattermapbox(
                lat=price_data.latitude, 
                lon=price_data.longitude, 
                name="Rent",
                hoverinfo = 'text',
                text = info,
                mode = 'markers',
                marker = dict(color=price_data.price, colorscale=colorscale,cmax=3500,cmin=750,autocolorscale=False,cauto = False))

plots = [data]
layout = Layout(
            autosize=True,
            mapbox = dict(
                accesstoken=mapbox_access_token,
                domain = dict(x=[0,1],y=[0,1]),
                center = dict(lon=-123.1,lat=49.26),
                zoom = 10.5))
fig = dict(data=plots,layout=layout)

if notebook:
    iplot(fig)
if output:
    rent_map = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
    
## Report
if output:
    print("## Map of all listings, showing rent",file=f)
    print("This map shows all the listings for the month, coloured by the price",file=f)
    print("",file=f)
    print(rent_map,file=f)
    print(".",file=f)


# In[14]:


price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))

ppsf = price_psf_data['price']/price_psf_data['area']
info = price_psf_data.apply(lambda row: unit_description(row), axis=1).values.tolist()

colorscale = list(zip(np.linspace(0.0,1.0,num=11),cl.scales['11']['div']['RdYlBu'][::-1]))
data = Scattermapbox(
                lat=price_psf_data.latitude, 
                lon=price_psf_data.longitude, 
                name="Rent per square foot",
                hoverinfo = 'text',
                text = info,
                mode = 'markers',
                marker = dict(color=ppsf, colorscale=colorscale,cmax=5.0,cmin=1.0,autocolorscale=False,cauto = False))

plots = [data]
layout = Layout(
            title = 'Map of listings coloured by rent per square foot',
            autosize=True,
            mapbox = dict(
                accesstoken=mapbox_access_token,
                domain = dict(x=[0,1],y=[0,1]),
                center = dict(lon=-123.1,lat=49.26),
                zoom = 10.5))
fig = dict(data=plots,layout=layout)

if notebook:
    iplot(fig)
if output:
    rent_psf_map = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
    
## Report, 
if output:
    print("## Map of all listings, showing rent per square foot",file=f)
    print("This map shows all the listings for the month, coloured by the price per square foot",file=f)
    print("",file=f)
    print(rent_psf_map,file=f)
    print(".",file=f)


# In[15]:


price_psf_data = remove_area_outliers(remove_price_outliers(raw_data))

ppsf = price_psf_data['price']/price_psf_data['area']
info = price_psf_data.apply(lambda row: unit_description(row), axis=1).values.tolist()

data = []

for utype in ['house','condo','townhouse','apartment']:
    df_type = price_psf_data[price_psf_data.unit_type == utype]
    info = df_type.apply(lambda row: unit_description(row), axis=1).values.tolist()
    data.append(Scattermapbox(
                    lat=df_type.latitude, 
                    lon=df_type.longitude, 
                    name=utype,
                    hoverinfo = 'text',
                    text = info,
                    mode = 'markers'))

layout = Layout(
            title = "Map of listings by unit type",
            autosize=True,
            mapbox = dict(
                accesstoken=mapbox_access_token,
                domain = dict(x=[0,1],y=[0,1]),
                center = dict(lon=-123.1,lat=49.26),
                zoom = 10.5))

fig = dict(data=data,layout=layout)

if notebook:
    iplot(fig)
if output:
    unit_type_map = plot(fig,include_plotlyjs=False,show_link=False,auto_open=False,output_type='div')
    
## Report, 
if output:
    print("## Map of all listings, showing rent per square foot",file=f)
    print("This map shows all the listings for the month, coloured by the price per square foot",file=f)
    print("",file=f)
    print(unit_type_map,file=f)
    print(".",file=f)


# In[ ]:




