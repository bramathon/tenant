import numpy as np
import pandas as pd

from neighbourhoods import hoods, cities

## This file provides basic statistics and analysis. Does not read or write any DB data, handles only dataframes

max_price = 7000
min_price = 500
max_area = 10000
min_area= 250

## def remove_duplicates
## this function should search the data for likely duplicates and remove them

def insert_plot(plot_file,output_file):
    plot_html = open(plot_file,'r')
    plot_div = plot_html.read()
    plot_html.close()
    
    plot_div = plot_div.replace("<html><head><meta charset=\"utf-8\" /></head><body>",'')
    plot_div = plot_div.replace("</body></html>",'')
    print("",file=output_file)
    print("<div>",file=output_file)
    print(plot_div,file=output_file)
    print("</div>",file=output_file)
    print("",file=output_file)

def remove_price_outliers(dataframe):
    # filter to reasonable area and price
    df = dataframe
    df = df[df['price'] > min_price]
    df = df[df['price'] < max_price]
    return df

def remove_area_outliers(dataframe):
    # filter to reasonable area and price
    df = dataframe
    df = df[df['area'] > min_area] 
    df = df[df['area'] < max_area]
    return df

def remove_furnished(dataframe):
    df = dataframe
    df = df[df['furnished'] == 0]
    return df

def median_rent_psf (dataframe):
    # returns rent per sqft for the given dataset and sdom
    # first, filter listings to those with reasonable areas listed
    df = remove_furnished(remove_area_outliers(remove_price_outliers(dataframe)))
    
    rent_psf = df['price']/df['area']
    median = rent_psf.median()
    uncertainty = np.sqrt(np.pi/2)*rent_psf.std()/np.sqrt(rent_psf.shape[0])
    
    return median, uncertainty

def median_rent (dataframe):
    df = remove_furnished(remove_price_outliers(dataframe))
    
    median = df['price'].median()
    uncertainty = np.sqrt(np.pi/2)*df['price'].std()/np.sqrt(df.shape[0])
    
    return median, uncertainty