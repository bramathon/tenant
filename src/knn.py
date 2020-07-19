import os
from sklearn import neighbors
from sklearn.metrics import mean_squared_error, mean_absolute_error
import argparse
import pickle as pkl
from data_utils import df_to_features_labels, train_val_test_split, normalize_data


def knn(train_data, test_data, n_neighbors):
    knn = neighbors.KNeighborsRegressor(n_neighbors=n_neighbors)
    Xtrain, ytrain = df_to_features_labels(train_data)
    Xtest, ytest = df_to_features_labels(test_data)
    knn.fit(Xtrain, ytrain)
    test_preds = knn.predict(Xtest)
    print('MSE: {0:3f}'.format(mean_squared_error(ytest, test_preds)))
    print('MAE: {0:3f}'.format(mean_absolute_error(ytest, test_preds)))


parser = argparse.ArgumentParser(description='KNN model runner')
parser.add_argument('--k', type=int, default=5)
parser.add_argument('--train', type=float, default=0.7)
args = parser.parse_args()

# allow running both from main directory and modelling directory
if 'modelling' in os.getcwd():
    dpath = './'
else:
    dpath = './modelling/'

#df = pkl.load(open(dpath, 'rb'))
#train, test = train_val_test_split(df, args.train, 0)
train = pkl.load(dpath + 'train.pickle')
test = pkl.load(dpath + 'test.pickle')
knn(train, test, args.k)
