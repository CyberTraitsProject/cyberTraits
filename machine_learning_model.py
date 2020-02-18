"""
this file is doing the machine learning itself.
the machine learning will be supervised, because n the learning we are getting the output values.
it takes the data, split it to 3 groups (by cross validation), and calculate 3 models.
every model, take one group for testing, and the another group for training.
the model of the learning will be linear regression.
we will summarize all the answers from the 3 models, and will do average on it.
the output will be the rounded value, between 1 to 5.
"""


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import StratifiedKFold


NUM_SPLITS = 3

def machine_learning_model_main(machine_learning_data_path, trait_name):
    machine_learning_df = pd.read_csv(machine_learning_data_path)

    # all the columns, except of the last column(the y)
    X_columns_names = machine_learning_df.columns[1:-2]

    # input values
    X = machine_learning_df[X_columns_names]
    #output values
    y = machine_learning_df[trait_name]

    # cross validation
    skf = StratifiedKFold(n_splits=NUM_SPLITS)

    regression_list = []
    X_test_data = []
    y_test_data = []

    for i, indexes in enumerate(skf.split(X, y)):

        # training data
        train_index = indexes[0]
        X_train, y_train = X.loc[train_index], y[train_index]

        # test data
        test_index = indexes[1]
        X_test, y_test = X.loc[test_index], y[test_index]

        X_test_data.append(X_test)
        y_test_data.append(y_test)

        print('---------X_train-----------')
        print(X_train)
        print('---------y_train-----------')
        print(y_train)

        regression_list.append(LinearRegression())
        regression_list[i].fit(X_train, y_train)


    # pass on every line in the data, send the line to every model, and calculate the round sum value.
    # print if the prediction is correct or not
    for i in range(len(X)):
        avg_y_pred = 0
        for regression in regression_list:
            y_pred = regression.predict([X.loc[i].values])
            avg_y_pred += float(y_pred)
        avg_y_pred /= NUM_SPLITS
        print(round(avg_y_pred))
        print('The pred is correct?', round(avg_y_pred) == y.loc[i])




if __name__ == '__main__':
    machine_learning_model_main(r"C:\Users\onaki\PycharmProjects\Cyber\machine_learning_data.csv", 'Secure')

