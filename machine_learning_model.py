import pandas as pd
from sklearn.linear_model import LinearRegression, RANSACRegressor
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split
from questionnaires import traits_names
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessClassifier, GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from useful_functions import *
import itertools
from sklearn.metrics import confusion_matrix, mean_squared_error

classifier_models = [RandomForestClassifier(), SVC(), KNeighborsClassifier(n_neighbors=4),
                     GaussianProcessClassifier(1.0*RBF(1.0)), DecisionTreeClassifier(max_depth=5),
                     MLPClassifier(alpha=1, max_iter=1000), AdaBoostClassifier(), GaussianNB()]
classifier_models_n = ['RandomForestClassifier()', 'SVC()', 'KNeighborsClassifier(n_neighbors=4)',
                       'GaussianProcessClassifier(1.0*RBF(1.0))', 'DecisionTreeClassifier(max_depth=5)',
                       'MLPClassifier(alpha=1, max_iter=1000)', 'AdaBoostClassifier()', 'GaussianNB()']
regression_models = [LinearRegression(), RandomForestRegressor(max_depth=None, random_state=0)]#,
                     #RANSACRegressor(random_state=42, min_samples=3)]
regression_models_n = ['LinearRegression()', 'RandomForestRegressor(max_depth=None, random_state=0)']#,
                       #'RANSACRegressor(random_state=42, min_samples=3)']


def check_model(file, X_train, X_test, y_train, y_test, model, classifier):
    """
    gets a model, fit it on the data and checks the results.
    write them in the file.
    :param file: the file to write there the results
    :param X_train: the X train data
    :param X_test: the X test data
    :param y_train: the y train data
    :param y_test: the y test data
    :param classifier: is a classifier problem or a regression problem
    :param model: the machine learning model
    """

    # fit the model on the train data
    model.fit(X_train, y_train)
    # predict the test data
    y_pred = model.predict(X_test)
    file.write('y_test: ' + str(y_test) + '\n')
    file.write('y_pred: ' + str(y_pred) + '\n')
    if classifier:
        # run the confusion matrix and check the score
        file.write('confusion_matrix: ' + str(confusion_matrix(y_test, y_pred, labels=[1, 2, 3, 4])) + '\n')
        # return the mean accuracy on the given test data and labels -
        # return the fraction of correctly classified samples
        score = model.score(X_test, y_test)
        file.write('score: ' + score + '\n')
    else:
        # check the RSS
        # = (y_pred_1 - y_true_1)^2 + (y_pred_2 - y_true_2)^2 + ... + (y_pred_n - y_true_n)^2
        file.write('mean_squared_error:' + str(mean_squared_error(y_test, y_pred)) + '\n')


def run_ml_model_on_every_combination(file, X_train, X_test, y_train, y_test, classifier):
    """
    create all the combination of taking 3 columns from all the columns.
    on every set, takes only these columns and run all of the machine learning models on it.
    writes all the results in the file.
    :param file: the file to write there the results
    :param X_train: the X train data
    :param X_test: the X test data
    :param y_train: the y train data
    :param y_test: the y test data
    :param classifier: is a classifier problem or a regression problem
    """

    # the number of the columns in the train data
    num_columns = len(X_train.columns)
    columns_indexes = range(num_columns)
    # all the combinations - 3 from N, without replacement
    combinations_list = list(itertools.combinations(columns_indexes, 3))

    # run on every set, and run all the machine learning models
    for columns_indexes_3 in combinations_list:
        columns_indexes_3_list = list(columns_indexes_3)
        cols_names = X_train.columns[columns_indexes_3_list]
        file.write('current combination cols names: ' + str(cols_names) + '\n')
        # takes only the 3 columns
        X_curr_train = X_train[cols_names]
        X_curr_test = X_test[cols_names]
        # the y values are the same
        y_curr_train = y_train
        y_curr_test = y_test

        # pass on every machine learning model, and run it on the current data
        if classifier:
            for i, classifier_model in enumerate(classifier_models):
                file.write('the model: ' + str(classifier_models_n[i]) + '\n')
                check_model(file, X_curr_train, X_curr_test, y_curr_train, y_curr_test, classifier_model, classifier)
        else:
            for i, regression_model in enumerate(regression_models):
                file.write('the model: ' + str(regression_models_n[i]) + '\n')
                check_model(file, X_curr_train, X_curr_test, y_curr_train, y_curr_test, regression_model, classifier)


def machine_learning_model_main(file, machine_learning_data_path, trait_name, classifier=False):
    """
    this method is doing the machine learning itself.
    the machine learning will be supervised, because the y values are known.
    for the traits - 'Extraversion', 'Agreeableness', 'Concientiousness', 'Neurotism', 'Openess' -
    we will do regression models,  because it is continuous values.
    and for the trait - 'Style' - we will do classification models, because it the values divided to classes.
    we are taking the data, split it to train (75%), and test (25%) and run number of models.
    we are running the models on the train data, ant than predict the test data, and checking the distances
    between the real data to the predicted data.
    :param machine_learning_data_path: full path to the machine learning file
    :param trait_name: the name of the trait we want to do machine learning on it
    :param classifier: if the data is classifier or not
    """

    # open the machine learning file
    check_if_file_exists(machine_learning_data_path)
    machine_learning_df = pd.read_csv(machine_learning_data_path)

    # all the columns, except of the first column(the candidate id) and the last column(the y)
    X_columns_names = machine_learning_df.columns[1:-1]

    # input values
    X = machine_learning_df[X_columns_names]
    # output values
    y = machine_learning_df[trait_name]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, shuffle=True)

    run_ml_model_on_every_combination(file, X_train, X_test, y_train, y_test, classifier)


if __name__ == '__main__':
    file = open('machine_learning_results.txt', 'w')
    # run the models on all of the traits, for the trait 'Style' - run a classifier model
    for trait in traits_names:
        file.write(str(trait) + ':\n')
        machine_learning_trait_file = f"C:/Users/onaki/CyberTraits/cyberTraits/machine_learning_data_{trait}.csv"
        if trait == 'Style':
            machine_learning_model_main(file, machine_learning_trait_file, trait, classifier=True)
        else:
            machine_learning_model_main(file, machine_learning_trait_file, trait)
    file.close()
