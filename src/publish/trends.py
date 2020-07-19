import numpy as np
import pandas as pd
import math
import sqlite3
import datetime
from analysis_functions import median_rent


from plotly import __version__
import plotly.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import *
from plotly import tools

## Helper Functions
def generate_months(startdate=datetime.date(2017,1,1),enddate=datetime.date.today()):
    month = startdate.month
    year = startdate.year
    months = []
    i = 0 
    while (year < enddate.year) or (month < enddate.month):
        months.append(str(datetime.date(year,month,1))[:7])
        if (month % 12) == 0:
            year = year + 1
            month = 1
        else:
            month = month + 1        
    months.append(str(datetime.date(year,month,1))[:7])
    return months

cache = {}

def get_all_listing_for_month(month):
    # unfurnished listings filtered for outliers in price
    if month in cache:
        df = cache[month]
    else:
        conn = sqlite3.connect('apartments.db')
        c = conn.cursor()
        sql = "SELECT * FROM apartments WHERE strftime(\"%Y-%m\", date) = '{}'".format(month)
        df = pd.read_sql_query(sql,conn)
        cache[month] = df
        conn.close()
    return df

## Sanity Check
def check_data_for_wierdness(month):
    # Should really make some nice histograms here
    min_price = 500
    max_price = 7000
    print("Checking data stats for {}...".format(month))
    df = pd.read_sql_query("SELECT * FROM apartments WHERE strftime(\"%Y-%m\", date) = '{}' AND city='Vancouver'".format(month),conn)
    print("{} Listings in Vancouver".format(df.shape[0]))
    print("{} of {} below ${}".format(df.loc[df['price'] < min_price].shape[0],df.shape[0],min_price))
    print("{} of {} above ${}".format(df.loc[df['price'] > max_price].shape[0],df.shape[0],max_price))
    print("{} of {} furnished. Price difference: ${}".format(df.loc[df['furnished'] == 1].shape[0],df.shape[0],df.loc[df['furnished'] == 1]['price'].median()-df['price'].median()))
    print("{} of {} missing # of bedrooms. Price difference: ${}".format(df.loc[df['bedrooms'].isnull()].shape[0],df.shape[0],df.loc[df['bedrooms'].isnull()]['price'].median()-df['price'].median()))
    
def median_price_trend(months,city=None):
    old_months = ['2016-02','2016-03','2016-04','2016-05','2016-06','2016-07','2016-08','2016-09','2016-10','2016-11','2016-12']
    month_nums_real = []
    prices = []
    error_bar = []
    
    if city == None:
        month_nums = old_months+months
        prices = [1590,1500,1500,1650,1700,1800,1900,1900,1895,1850,1750]
        error_bar = [15.9,9.3,9.0,9.5,9.9,9.9,9.9,9.4,9.7,8.9,9.3,18.4]
        month_nums_real = old_months.copy()
    if city == 'Vancouver':
        month_nums = old_months+months
        prices = [1800,1700,1700,1800,1850,1950,2000,2100,2095,1995,1897]
        error_bar = [24.7,14.2,13.1,14.5,15.4,15.1,13.8,14.8,13.0,13.9,26.6]
        month_nums_real = old_months.copy()
    
    for month in months: # from 2017-01 and on
        
        data = get_all_listing_for_month(month)
        if city != None:
            data = data[data['City'] == city]
        med, unc = median_rent(data)
        if not math.isnan(med):
            month_nums_real.append(month)
            prices.append(med)
            error_bar.append(unc)
        
    return month_nums_real, prices, error_bar

def median_price_trend_by_bedroom(months,city=None,bedrooms=0):
    month_nums_real = []
    prices = []
    error_bar = []
    for month in months: # from 2017-01 and on
        
        data = get_all_listing_for_month(month)
        if city != None:
            data = data[data['City'] == city]
        data = data[data['bedrooms'] == bedrooms]
        med, unc = median_rent(data)
        if not math.isnan(med):
            month_nums_real.append(month)
            prices.append(med)
            error_bar.append(unc)
        
    return month_nums_real, prices, error_bar

def monthly_trend(months,metric=median_rent,city=None,select=None):
    # Select function operates on a dataframe, returns a dataframe
    month_nums_real = []
    prices = []
    error_bar = []
    for month in months:
        
        data = get_all_listing_for_month(month)
        if select != None:
            data = select(data)
        med, unc = metric(data)
        if not math.isnan(med):
            month_nums_real.append(month)
            prices.append(med)
            error_bar.append(unc)
        
    return month_nums_real, prices, error_bar