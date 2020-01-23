import numpy as np

'''
Splits a dataframe into train/val/test dataframes

'''
def split_dataframe(dataframe, train_frac, val_frac=0):
    test_frac = 1 - train_frac - val_frac
    assert test_frac > 0, 'Train fraction and val fraction cannot be >= 1'
    train_split = int(train_frac*len(dataframe))
    val_split = train_split + int(val_frac*len(dataframe))
    # get random state to split data so it is split consistently
    rng = np.random.RandomState(1234)
    order = rng.permutation(range(len(dataframe)))
    train = dataframe.iloc[order[:train_split]]
    if val_frac != 0:
        val = dataframe.iloc[order[train_split:val_split]]
    else:
        val = None
    test = dataframe.iloc[order[val_split:]]

    return train, val, test





