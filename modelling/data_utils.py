import numpy as np
import pandas as pd
import pickle as pkl
from sklearn import metrics
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_dataset (scale=False,one_hot=False,test_size=0.2,categorize_bedrooms=False):
    """
    Loads the dataset and splits into test/train sets.
    
    scaling will choose whether to scale the data
    
    one_hot will one-hot encode the categorical variables
    
    returns X_train, X_test, y_train, y_test
    If scale is true, also return X_scaler, y_scaler
    """
    raw_df = pd.read_pickle("dataset.pickle")
    
    y = pd.DataFrame()
    X = pd.DataFrame()
    
    y['price'] = raw_df['price']
    
    if scale:
        y_scaler = StandardScaler()
        y_array = y['price'].to_numpy().reshape(-1, 1)
        y['price'] = y_scaler.fit_transform(y_array)
    
    scaled_columns = ['date', 'latitude', 'longitude', 'area']
    category_columns = ['unit_type']
    
    X['date'] = raw_df['date'].astype(int)/1e9
    X['latitude'] = raw_df['latitude']
    X['longitude'] = raw_df['longitude']
    X['area'] = raw_df['area']
    X['bedrooms'] = raw_df['bedrooms']
    
    if categorize_bedrooms:
        X['bedrooms'] = pd.Categorical(X['bedrooms'])
        category_columns.append('bedrooms')
    else:
        scaled_columns.append('bedrooms')
        
    if scale:
        X_scaler = StandardScaler()
        X[scaled_columns] = X_scaler.fit_transform(X[scaled_columns])
    
    # binary variables
    X['pets'] = raw_df['pets']
    X['furnished'] = raw_df['furnished']
    X['unit_type'] = raw_df['unit_type']
    
    X['unit_type'] = pd.Categorical(X['unit_type'])
    X['bedrooms'] = pd.Categorical(X['bedrooms']) if categorize_bedrooms else X['bedrooms']
    #df['unit_type'] = df['unit_type'].cat.codes
    
    if one_hot:
        # categorical variable one-hot encoded
        for col in category_columns:
            X[col] = pd.Categorical(X[col])
            dfDummies = pd.get_dummies(X[col], prefix = col)
            X = pd.concat([X, dfDummies], axis=1)
            X = X.drop(columns=col)

    print("X Columns: {}",format(X.columns))
    print("X Shape: {}".format(X.shape))
    print("y Shape: {}".format(y.shape))
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    if scale:
        return X_train, X_test, y_train, y_test, X_scaler, y_scaler
    else:
        return X_train, X_test, y_train, y_test
    
def check_predictions(X_test,y_test,y_pred,n=10):
    """
    Prints n test values vs predictions, to get a feel for how well the algorithm is doing.
    """
    #df = pd.concat([X_test,pd.Series(y_test,name='y_test'),pd.Series(y_pred,name='y_pred')])
    y_pred = np.asarray(y_pred)
    y_test = np.asarray(y_test)
    y_pred = np.round(y_pred)
    df = pd.DataFrame({'y_test':y_test,'y_pred':y_pred})
    df = pd.concat([pd.DataFrame(X_test),df],axis=1)
    df['error'] = y_test - y_pred
    return df.sample(n=n)

def core_metrics (y_test,y_pred):
    y_test = np.asarray(y_test).reshape(-1)
    y_pred = np.asarray(y_pred).reshape(-1)
    mae = metrics.mean_absolute_error(y_test,y_pred)
    r_squared = metrics.explained_variance_score(y_test,y_pred)
    median_error = metrics.median_absolute_error(y_test,y_pred)
    print("Mean Absolute Error: {:.0f}".format(mae))
    print("Median Absolute Error: {:.0f}".format(median_error))
    print("Explained Variance: {:.2f}".format(r_squared))
    df = pd.DataFrame({'y_test':y_test,'y_pred':y_pred})
    df['error'] = y_test - y_pred
    fig = px.histogram(df,x='error',histnorm='probability density')
    fig.show()

def train_val_test_split(dataframe, train_frac, val_frac=0):
    '''
    Splits a dataframe into train/val/test dataframes
    '''
    test_frac = 1 - train_frac - val_frac
    assert test_frac > 0, 'Train fraction and val fraction cannot be >= 1'
    train_split = int(train_frac*len(dataframe))
    val_split = train_split + int(val_frac*len(dataframe))
    # get random state to split data so it is split consistently
    rng = np.random.RandomState(1234)
    order = rng.permutation(range(len(dataframe)))
    train = dataframe.iloc[order[:train_split]]
    test = dataframe.iloc[order[val_split:]]
    if val_frac != 0:
        val = dataframe.iloc[order[train_split:val_split]]
        return train, val, test
    else:
        return train, test


'''
Creates features and labels from a dataframe
'''
def df_to_features_labels(dataframe):
    feature_names = ['latitude',
                     'longitude',
                     'area',
                     'studio',
                     '1_bed',
                     '2_bed',
                     '3_bed',
                     '4_bed',
                     '5_bed',
                     '6_bed',
                     'mansion',
                     'apartment',
                     'condo',
                     'house',
                     'townhouse',
                     'pets',
                     'furnished']
    x = dataframe[feature_names]
    y = dataframe['price']
    return x, y

### PLOTTING ###

from keys import mapbox_access_token
import plotly.graph_objects as go

# cache the populated coordinates

px.set_mapbox_access_token(mapbox_access_token)

populated_coordinates = np.array([])

def remove_empty_coords (X,lats,longs,lat_step,long_step):
    global populated_coordinates
    # removes coordinates which have less than 5 listings in cell+NN
    if populated_coordinates.any():
        print('Using cached coordinates')
        use_coordinates = np.array(populated_coordinates)
    else: 
        use_coordinates = []
        for lat in lats:
            lat_df = X[X['latitude'].between(lat - lat_step,lat+lat_step)]
            if len(lat_df) > 5:
                for long in longs:
                    if np.sum(lat_df['longitude'].between(long - long_step,long + long_step)) > 5:
                        use_coordinates.append([lat,long])
        use_coordinates = np.array(use_coordinates)
        populated_coordinates = use_coordinates # set cache
    return use_coordinates

def map_model (X_test,model):
    # model should take X_test as an arugment to it's predict function
    # we are going to map the price for the typical apartment around the whole city
    
    # typical apartment characteristics
    date = X_test['date'].median()
    area = X_test['area'].median()
    bedrooms = X_test['bedrooms'].mode()[0]
    pets = X_test['pets'].mode()[0]
    furnished = X_test['furnished'].mode()[0]
    unit_type = X_test['unit_type'].mode()[0]
    
    title = "Price for a {}sqft, {} bed {}".format(area,bedrooms,unit_type)
    
    lats, lat_step = np.linspace(X_test['latitude'].min(),X_test['latitude'].max(),num=300,retstep=True)
    longs, long_step = np.linspace(X_test['longitude'].min(),X_test['longitude'].max(),num=600,retstep=True)
    coordinate_list = np.array(np.meshgrid(lats,longs)).T.reshape(-1,2)
    
    use_coordinates = remove_empty_coords(X_test,lats,longs,lat_step,long_step)

    df = pd.DataFrame(use_coordinates,columns=['latitude','longitude'])
    df.loc[:,'date'] = date
    df.loc[:,'area'] = area
    df.loc[:,'bedrooms'] = bedrooms
    df.loc[:,'pets'] = pets
    df.loc[:,'furnished'] = furnished
    df.loc[:,'unit_type'] = unit_type
    df['unit_type'] = pd.Categorical(df['unit_type'])
    df = df[['date', 'latitude', 'longitude', 'area', 'bedrooms', 'pets', 'furnished', 'unit_type']]
    
    y_geo = model.predict(df)
    df['Price ($)'] = y_geo
    df['marker_size'] = 8
    center = dict(lat=49.2623962, lon=-123.115429) # city hall
    fig = px.scatter_mapbox(df,lon='longitude',lat='latitude',color='Price ($)',width=1200,height=1000,center=center,size='marker_size',
                            zoom=11,size_max=5,opacity=0.6,title=title)
    
#     fig = go.Figure()
#     fig.add_trace(go.Scattermapbox(lon=df['longitude'],
#                                    lat=df['latitude'],
#                                    mode='markers',
#                                    marker={'size': 15, 'color': df['price']})
#                                   )
#    fig.update_layout(mapbox=go.layout.Mapbox(accesstoken=mapbox_access_token,center=center,zoom=12),height=1000,width=1200)   
    return fig

def time_evolution (X,model):
    """
    Plot the time evolution of prices for the typical apartment
    """
    # typical apartment characteristics
    area = X['area'].median()
    lat = X['latitude'].median()
    long = X['longitude'].median()
    bedrooms = X['bedrooms'].mode()[0]
    pets = X['pets'].mode()[0]
    furnished = X['furnished'].mode()[0]
    unit_type = X['unit_type'].mode()[0]
    
    title = "Price for a {}sqft, {} bed {}".format(area,bedrooms,unit_type)
    
    dates = np.linspace(X['date'].min(),X['date'].max(),num=24)
    
    lats, lat_step = np.linspace(X_test['latitude'].min(),X_test['latitude'].max(),num=300,retstep=True)
    longs, long_step = np.linspace(X_test['longitude'].min(),X_test['longitude'].max(),num=600,retstep=True)
    coordinate_list = np.array(np.meshgrid(lats,longs)).T.reshape(-1,2)
    
    use_coordinates = remove_empty_coords(X_test,lats,longs,lat_step,long_step)
    
    prices = []
    
    for d in dates:
        df = pd.DataFrame(use_coordinates,columns=['latitude','longitude'])
        df.loc[:,'date'] = d
        df.loc[:,'area'] = area
        df.loc[:,'bedrooms'] = bedrooms
        df.loc[:,'pets'] = pets
        df.loc[:,'furnished'] = furnished
        df.loc[:,'unit_type'] = unit_type
        df['unit_type'] = pd.Categorical(df['unit_type'])
        df = df[['date', 'latitude', 'longitude', 'area', 'bedrooms', 'pets', 'furnished', 'unit_type']]
        price = model.predict(df).mean()
        prices.append(price)
        
    plot_df = pd.DataFrame({'Date': dates, 'Price ($)': prices})
    plot_df['Date'] = pd.to_datetime(plot_df['Date'],unit='s')
    return px.scatter(plot_df,x='Date',y='Price ($)',trendline='ols',title=titleheight=1000,width=1200)