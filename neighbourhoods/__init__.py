import pandas as pd

hoods = {
    "Gastown": pd.read_csv("neighbourhoods/gastown.csv"),
    "Yaletown": pd.read_csv("neighbourhoods/yaletown.csv"),
    "Arbutus Ridge": pd.read_csv("neighbourhoods/arbutus_ridge.csv"),
    "Downtown": pd.read_csv("neighbourhoods/downtown.csv"),
    "Dunbar-Southlands": pd.read_csv("neighbourhoods/dunbar_southlands.csv"),
    "Fairview": pd.read_csv("neighbourhoods/fairview.csv"),
    "Grandview-Woodland": pd.read_csv("neighbourhoods/grandview_woodlands.csv"),
    "Hasting-Sunrise": pd.read_csv("neighbourhoods/hastings_sunrise.csv"),
    "Kensington": pd.read_csv("neighbourhoods/kensington.csv"),
    "Kerrisdale": pd.read_csv("neighbourhoods/kerrisdale.csv"),
    "Killarney": pd.read_csv("neighbourhoods/killarney.csv"),
    "Kitsilano": pd.read_csv("neighbourhoods/kitsilano.csv"),
    "Marpole": pd.read_csv("neighbourhoods/marpole.csv"),
    "Mount Pleasant": pd.read_csv("neighbourhoods/mount_pleasant.csv"),
    "Oakridge": pd.read_csv("neighbourhoods/oakridge.csv"),
    "Renfrew-Collingwood": pd.read_csv("neighbourhoods/renfrew_collingwood.csv"),
    "Riley Park": pd.read_csv("neighbourhoods/riley_park.csv"),
    "Shawnessy": pd.read_csv("neighbourhoods/shawnessy.csv"),
    "South Cambie": pd.read_csv("neighbourhoods/south_cambie.csv"),
    "Stratchona": pd.read_csv("neighbourhoods/strathcona.csv"),
    "Sunset": pd.read_csv("neighbourhoods/sunset.csv"),
    "Victoria-Fraserview": pd.read_csv("neighbourhoods/victoria_fraserview.csv"),
    "West End": pd.read_csv("neighbourhoods/west_end.csv"),
    "West Point Grey": pd.read_csv("neighbourhoods/west_point_grey.csv")}

cities = {"Vancouver": pd.read_csv("neighbourhoods/vancouver.csv")}