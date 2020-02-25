import numpy as np
import pandas as pd
import pickle as pkl

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