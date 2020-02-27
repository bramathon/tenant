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


from keys import mapbox_access_token
import plotly.graph_objects as go

# cache the populated coordinates

populated_coordinates = np.array([])

def remove_empty_coords (X_test,coordinates,lat_step,long_step):
    global populated_coordinates
    # removes coordinates which have no data
    if populated_coordinates.any():
        print('Using cached coordinates')
        use_coordinates = np.array(populated_coordinates)
    else:
        populated_coordinates = []
        for lat,long in coordinates:
            if ((X_test['latitude'].between(lat,lat+lat_step)) & (X_test['longitude'].between(long,long + long_step))).any():
                populated_coordinates.append([lat,long])
        use_coordinates = np.array(populated_coordinates)
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
    
    # construct a square grid
    # throw away any points that are not close to real values
    lats, lat_step = np.linspace(X_test['latitude'].min(),X_test['latitude'].max(),num=300,retstep=True)
    longs, long_step = np.linspace(X_test['longitude'].min(),X_test['longitude'].max(),num=300,retstep=True)
    coordinate_list = np.array(np.meshgrid(lats,longs)).T.reshape(-1,2)
    
    # can this be vectorized?
    # now, remove the rows that aren't near real data
    # to do this, set a threshold value for how close we need to find a point
    # for each point in the dataframe, see if there is a point close enough
    use_coordinates = remove_empty_coords(X_test,coordinate_list,lat_step,long_step)

    df = pd.DataFrame(use_coordinates,columns=['latitude','longitude'])
    df.loc[:,'date'] = date
    df.loc[:,'area'] = area
    df.loc[:,'bedrooms'] = bedrooms
    df.loc[:,'pets'] = pets
    df.loc[:,'furnished'] = furnished
    df.loc[:,'unit_type'] = unit_type
    df['unit_type'] = pd.Categorical(df['unit_type'])
    df = df[['date', 'latitude', 'longitude', 'area', 'bedrooms', 'pets', 'furnished', 'unit_type']]
    
    #X_geo = df.to_numpy()
    y_geo = model.predict(df)
    df['price'] = y_geo

    fig = px.scatter_mapbox(df,lon='longitude',lat='latitude',color='price',width=1000,height=800)

    #fig = go.Figure(go.Scattermapbox(lon=list(map(str,list(df['longitude']))),lat=list(map(str,list(df['latitude'])))))#,marker=go.scattermapbox.Marker(size=14)))
    #go.scattermapbox.Marker(size=14,symbol='square',color=df['price'])
    #fig.update_layout(mapbox=dict(accesstoken=mapbox_access_token))
                  
    # need to fix view and scatter marker size
    #fig.data[0].marker = dict(size=10,opacity=0.5,symbol='square')
    #fig = px.scatter_mapbox(df,lon='longitude',lat='latitude',color='price')
    return fig

# def norm (series,method="var"):
#     """
#     Returns the (pandas) series, normalized by the selected method. 
#     - Method 'var' sets the centre at the median value and divides by the std.
#     - Method 'range' sets the centre at the median and the min->-1, max->1
#     Also returns a function that can be used to return the data to real units
#     """
#     assert isinstance(series,pd.Series), "data must be a Pandas series"
#     if method  == "var":
#         median = series.median()
#         std = series.std()
#         norm_series = (series - median)/std
#         to_real_units = "lambda x: x*{} + {}".format(std,median)
#         to_norm_units = "lambda x: (x-{})/{}".format(median,std)
#     elif method == "range":
#         data_range = series.max() - series.min()
#         norm_series = (series - series.min())/(0.5*data_range) - 1
#         to_real_units = "lambda x: (x+1)*0.5*{} + {}".format(data_range,series.min())
#         to_norm_units = "lambda x: (x - {})/(0.5*{})".format(series.min(),data_range)
#     return norm_series, to_real_units, to_norm_units
    
    

# def normalize_dataset (df,return_converters=False):
#     """
#     Converts the dataframe into a format useful for fitting models
#     - returns a dataframe
#     - return_converters will return a second value which is a dictionary of functions that can convert back to real units
#     """
#     assert all(col in df.columns.tolist() for col in  ['date', 'latitude','longitude','area','bedrooms','unit_type','pets','furnished','price'])
    
#     norm_df = pd.DataFrame()
    
#     norm_df['date'] = df['date'].astype(int)/1e9
#     norm_df['date'], real_date, norm_date = norm(norm_df['date'],method="range")
#     norm_df['latitude'], real_lat, norm_lat = norm(df['latitude'])
#     norm_df['longitude'], real_long, norm_long = norm(df['longitude'])
#     norm_df['area'], real_area, norm_area = norm(df['area'])

#     # code the bedrooms as binary variables

#     norm_df['studio'] = (df['bedrooms']==0.0).astype(int)
#     norm_df['1_bed'] = (df['bedrooms']==1.0).astype(int)
#     norm_df['2_bed'] = (df['bedrooms']==2.0).astype(int)
#     norm_df['3_bed'] = (df['bedrooms']==3.0).astype(int)
#     norm_df['4_bed'] = (df['bedrooms']==4.0).astype(int)
#     norm_df['5_bed'] = (df['bedrooms']==5.0).astype(int)
#     norm_df['6_bed'] = (df['bedrooms']==6.0).astype(int)
#     norm_df['mansion'] = (df['bedrooms']>=7.0).astype(int)

#     # code the unit type as binary variables

#     norm_df['apartment'] = (df['unit_type']=="apartment").astype(int)
#     norm_df['condo'] = (df['unit_type']=="condo").astype(int)
#     norm_df['house'] = (df['unit_type']=="house").astype(int)
#     norm_df['townhouse'] = (df['unit_type']=="townhouse").astype(int)

#     norm_df['pets'] = df['pets']
#     norm_df['furnished'] = df['furnished']

#     norm_df['price'], real_price, norm_price = norm(df['price'])

#     conversion_functions = {'to_date': real_date, 'to_latitude': real_lat, 'to_longitude': real_long, 'to_area': real_area, 'to_price': real_price,
#                             'from_date': norm_date, 'from_latitude': norm_lat, 'from_longitude': norm_long, 'from_area': norm_area, 'from_price': norm_price}
#     if return_converters:
#         return norm_df, conversion_functions
#     else:
#         return norm_df