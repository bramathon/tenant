import numpy as np
import pickle as pkl

'''
Splits a dataframe into train/val/test dataframes

'''
def train_val_test_split(dataframe, train_frac, val_frac=0):
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

#x = pkl.load(open('./modelling/clean_dataset.pickle', 'rb'))
#x,y = df_to_features_labels(x)





