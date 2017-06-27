import plotly
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
import numpy as np
import sqlite3
import time
import datetime
import numpy as np
from neighbourhoods import hoods
import matplotlib.path as mplPath

stream_tokens = tls.get_credentials_file()['stream_ids']
token_1 = stream_tokens[-1]   # I'm getting my stream tokens from the end to ensure I'm not reusing tokens

stream_id1 = dict(token=token_1, maxpoints=60)

trace1 = go.Scatter(x=[], y=[],text=[],hoverinfo ="text",stream=stream_id1, name='1bed',mode = 'lines+markers')

data = [trace1]
layout = go.Layout(
    title='1 Bedroom Apartments for rent in Vancouver',
    yaxis=dict(title='Monthly Rent ($)', range=[0, 3500])
)

fig = go.Figure(data=data, layout=layout)
plot_url = py.plot(fig, filename='1bed-rent',auto_open=False)

s_1 = py.Stream(stream_id=token_1)

def in_vancouver(neighbourhood):
    in_town = False
    for k,v in hoods.items():
        if k == neighbourhood:
            in_town = True
    return in_town

def another_one(time):
    try:
        conn = sqlite3.connect('apartments.db')
        c = conn.cursor()
        c.execute('SELECT * FROM apartments WHERE strftime("%s", date) > strftime("%s", ?) AND bedrooms = 1 AND longitude < -123.0234968 AND latitude > 49.1988668', (time,))
        record = c.fetchone()
        c.close()
    except:
        record = None
    return record    

s_1.open()
current_listing_time = '2017-06-20T20:00:17-07:00' # starttime
time_between_points = 1

while True:
    listing = another_one(current_listing_time)
    if listing == None:
        s_1.heartbeat()
        time.sleep(time_between_points)
    else:
        current_listing_time = listing[0]
        title = listing[3]
        price = listing[7]
        area = listing[8]
        neighbourhood =listing[9]
        #x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            if area != None and price!= None and neighbourhood!= None:
                hover_text = "$" + str(price) + ", " + str(area) + "sqft, " + neighbourhood
            elif price!= None and neighbourhood!= None:
                hover_text = "$" + str(price) + ", "+ neighbourhood
            elif neighbourhood!= None:
                hover_text = neighbourhood
            else:
                hover_text = ""
        except:
            hover_text = ""
        print(hover_text)
        try:
            x = datetime.datetime.strptime(current_listing_time[0:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            y = price
            if price < 3500 and price > 500: # outliers
                s_1.write(dict(x=x,y=y,text=hover_text))
                time.sleep(time_between_points)
            else:
                s_1.heartbeat()
                time.sleep(time_between_points)
        except:
            s_1.heartbeat()
            time.sleep(time_between_points)
s_1.close()
