'''
from sklearn.model_selection import StratifiedKFold
NUM_SPLITS = 2
regression_list = []
X_test_data = []
y_test_data = []
# cross validation
skf = StratifiedKFold(n_splits=NUM_SPLITS)
with open(f'machine_learning_{trait}_results.txt', 'w') as f:
    for i, indexes in enumerate(skf.split(X, y)):

        # training data
        train_index = indexes[0]
        X_train, y_train = X.loc[train_index], y[train_index]

        # test data
        test_index = indexes[1]
        X_test, y_test = X.loc[test_index], y[test_index]

        X_test_data.append(X_test)
        y_test_data.append(y_test)

        f.write('---------X_train-----------' + '\n')
        f.write(str(X_train) + '\n')
        f.write('---------y_train-----------' + '\n')
        f.write(str(y_train) + '\n')

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
        f.write(str(round(avg_y_pred)) + '\n')
        f.write('The pred is correct? ' + str(round(avg_y_pred) == y.loc[i]) + '\n')
        f.write('The pred is: ' + str(avg_y_pred) + ' The real is: ' + str(y.loc[i]) + '\n')'''

