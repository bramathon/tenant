import pandas as pd
import json

hoods = {
    "Gastown": pd.read_csv("scraper/vancouver_neighbourhoods/gastown.csv"),
    "Yaletown": pd.read_csv("scraper/vancouver_neighbourhoods/yaletown.csv"),
    "Arbutus Ridge": pd.read_csv("scraper/vancouver_neighbourhoods/arbutus_ridge.csv"),
    "Downtown": pd.read_csv("scraper/vancouver_neighbourhoods/downtown.csv"),
    "Dunbar-Southlands": pd.read_csv("scraper/vancouver_neighbourhoods/dunbar_southlands.csv"),
    "Fairview": pd.read_csv("scraper/vancouver_neighbourhoods/fairview.csv"),
    "Grandview-Woodland": pd.read_csv("scraper/vancouver_neighbourhoods/grandview_woodlands.csv"),
    "Hastings-Sunrise": pd.read_csv("scraper/vancouver_neighbourhoods/hastings_sunrise.csv"),
    "Kensington": pd.read_csv("scraper/vancouver_neighbourhoods/kensington.csv"),
    "Kerrisdale": pd.read_csv("scraper/vancouver_neighbourhoods/kerrisdale.csv"),
    "Killarney": pd.read_csv("scraper/vancouver_neighbourhoods/killarney.csv"),
    "Kitsilano": pd.read_csv("scraper/vancouver_neighbourhoods/kitsilano.csv"),
    "Marpole": pd.read_csv("scraper/vancouver_neighbourhoods/marpole.csv"),
    "Mount Pleasant": pd.read_csv("scraper/vancouver_neighbourhoods/mount_pleasant.csv"),
    "Oakridge": pd.read_csv("scraper/vancouver_neighbourhoods/oakridge.csv"),
    "Renfrew-Collingwood": pd.read_csv("scraper/vancouver_neighbourhoods/renfrew_collingwood.csv"),
    "Riley Park": pd.read_csv("scraper/vancouver_neighbourhoods/riley_park.csv"),
    "Shaunessy": pd.read_csv("scraper/vancouver_neighbourhoods/shawnessy.csv"),
    "South Cambie": pd.read_csv("scraper/vancouver_neighbourhoods/south_cambie.csv"),
    "Strathcona": pd.read_csv("scraper/vancouver_neighbourhoods/strathcona.csv"),
    "Sunset": pd.read_csv("scraper/vancouver_neighbourhoods/sunset.csv"),
    "Victoria-Fraserview": pd.read_csv("scraper/vancouver_neighbourhoods/victoria_fraserview.csv"),
    "West End": pd.read_csv("scraper/vancouver_neighbourhoods/west_end.csv"),
    "West Point Grey": pd.read_csv("scraper/vancouver_neighbourhoods/west_point_grey.csv")}

file = open("scraper/vancouver_neighbourhoods/AdminBoundary.geojson")
all_coords = json.loads(file.read())

cities = {}

for city_coords in all_coords['features']:
    municipality_name = city_coords['properties']['ShortName']
    if city_coords['geometry']['type'] == 'MultiPolygon':
        geojson_coords = city_coords['geometry']['coordinates'][0][0] # for multipolygon, just take the first one for now
    else:
        geojson_coords = city_coords['geometry']['coordinates'][0]
    cities[municipality_name] = pd.DataFrame(geojson_coords)
    
#cities = {"Vancouver": pd.read_csv("/home/bram/Documents/craiglist_crawler/vancouver_neighbourhoods/vancouver.csv")}
