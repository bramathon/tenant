import numpy as np
import pandas as pd

from neighbourhoods import hoods, cities

## This file provides basic statistics and analysis. Does not read or write any DB data, handles only dataframes

max_price = 7000
min_price = 500
max_area = 10000
min_area= 250

def remove_outliers(dataframe):
    # filter to reasonable area and price
    df = dataframe
    df = df[df['area'] > min_area] 
    df = df[df['area'] < max_area]
    df = df[df['price'] > min_price]
    df = df[df['price'] < max_price]
    return df

def median_rent_psf (dataframe):
    # returns rent per sqft for the given dataset and sdom
    # first, filter listings to those with reasonable areas listed
    df = dataframe
    
    # filter to reasonable area and price
    df = df[df['area'] > min_area] 
    df = df[df['area'] < max_area]
    df = df[df['price'] > min_price]
    df = df[df['price'] < max_price]
    df = df[df['furnished'] == 0]
    
    rent_psf = df['price']/df['area']
    median = rent_psf.median()
    uncertainty = np.sqrt(np.pi/2)*rent_psf.std()/np.sqrt(rent_psf.shape[0])
    
    return median, uncertainty

def median_rent (dataframe):
    df = dataframe
    
    # filter to reasonable area and price
    df = df[df['price'] > 250]
    df = df[df['price'] < 7000]
    df = df[df['furnished'] == 0]
    
    
    median = df['price'].median()
    uncertainty = np.sqrt(np.pi/2)*df['price'].std()/np.sqrt(df.shape[0])
    
    return median, uncertainty