import pickle
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
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from useful_functions import *
import itertools
from sklearn.metrics import confusion_matrix, mean_squared_error
import joblib


classifier_model = DecisionTreeClassifier(max_depth=3)
classifier_model_n = 'DecisionTreeClassifier(max_depth=3)'
regression_model = DecisionTreeRegressor(max_depth=3)
regression_model_n = 'DecisionTreeRegressor(max_depth=3)'

trait_best_columns_dic = {}


def check_model(X_train, X_test, y_train, y_test, model):
    """
    gets a model, fit it on the data and checks the results.
    :param X_train: the X train data
    :param X_test: the X test data
    :param y_train: the y train data
    :param y_test: the y test data
    :param model: the machine learning model
    """

    # fit the model on the train data
    model.fit(X_train, y_train)
    # predict the test data
    test_score = model.score(X_test, y_test)
    train_score = model.score(X_train, y_train)

    return test_score, train_score, model


def run_greedy_algorithm_and_choose_the_best_model(results_dir, file, X_train, X_test, y_train, y_test, trait_name, classifier):
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

    # will contain for every test score, its columns and model.
    # columns_scores_models_dic = { score_1 : {columns_names: [...], model: ML_model_1},
    #                               score_2 : {columns_names: [...], model: ML_model_2}, ... ,
    #                               score_n : {columns_names: [...], model: ML_model_n}}
    columns_scores_models_dic = {}

    # the number of the columns in the train data
    num_columns = len(X_train.columns)
    columns_indexes = range(num_columns)
    columns_best_indexes = []
    columns_best_names = []
    model = ''
    i = 0
    while len(columns_best_indexes) < num_columns:
        print(i)
        i += 1
        models_results = []
        models_indexes = []
        train_models_results = []

        for index in columns_indexes:

            if index in columns_best_indexes:
                continue
            else:
                columns_indexes_list = columns_best_indexes + [index]

            cols_names = X_train.columns[columns_indexes_list]
            # file.write('current combination cols names: ' + str(cols_names) + '\n')
            # takes only the 3 columns
            X_curr_train = X_train[cols_names]
            X_curr_test = X_test[cols_names]
            # the y values are the same
            y_curr_train = y_train
            y_curr_test = y_test

            # pass on every machine learning model, and run it on the current data
            if classifier:
                test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                             classifier_model)
            else:
                test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                             regression_model)

            models_indexes.append(columns_indexes_list)
            models_results.append(test_score)
            train_models_results.append(train_score)

        best_score = max(models_results)

        index_best_score = models_results.index(best_score)
        columns_best_indexes = models_indexes[index_best_score]
        best_train_score = train_models_results[index_best_score]
        columns_best_names = list(X_train.columns[columns_best_indexes])

        if best_score not in columns_scores_models_dic:
            columns_scores_models_dic[best_score] = {}
            columns_scores_models_dic[best_score]['columns_names'] = columns_best_names
            columns_scores_models_dic[best_score]['model'] = model

        if file:
            file.write('columns indexes: ' + str(columns_best_indexes) + '\n')
            file.write('columns names: ' + str(columns_best_names) + '\n')
            file.write('test score:' + str(best_score) + '\n')
            file.write('train score:' + str(best_train_score) + '\n\n')

    best_final_score = max(columns_scores_models_dic)

    columns_best_final_names = columns_scores_models_dic[best_final_score]['columns_names']
    trait_models_dir = os.path.join(results_dir, 'traits_models')
    if not os.path.isdir(trait_models_dir):
        os.makedirs(trait_models_dir)
    # Save the best model in a pickle file (by joblib)
    best_model = columns_scores_models_dic[best_final_score]['model']
    joblib.dump(best_model, os.path.join(trait_models_dir, f'{trait_name}_model.pkl'))

    return list(columns_best_final_names)


def machine_learning_model_main(results_dir, file, machine_learning_data_path, trait_name, classifier=False):
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

    columns_best_names = run_greedy_algorithm_and_choose_the_best_model(results_dir, file, X_train, X_test, y_train, y_test,
                                                                        trait_name, classifier)
    trait_best_columns_dic[trait_name] = columns_best_names

    return columns_best_names


if __name__ == '__main__':

    results_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\aaa'
    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)

    description_file = os.path.join(results_dir, 'model_description.txt')
    if not os.path.isfile(description_file):
        open(description_file, 'w').close()

    file = open(os.path.join(results_dir, 'model_results.txt'), 'w')
    file.write('The Classifier Model : ' + classifier_model_n + '\n')
    file.write('The Regression Model : ' + regression_model_n + '\n')

    scaled_data_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_1'

    # run the models on all of the traits, for the trait 'Style' - run a classifier model
    for trait in traits_names:
        file.write(str(trait) + ':\n')
        machine_learning_trait_file = os.path.join(scaled_data_dir, f'machine_learning_data_{trait}.csv')
        if trait == 'Style':
            machine_learning_model_main(results_dir, file, machine_learning_trait_file, trait, classifier=True)
        else:
            print(machine_learning_model_main(results_dir, file, machine_learning_trait_file, trait))
    file.close()
    trait_cols_names_info_file = open(os.path.join(results_dir, 'trait_cols_names_info.pkl'), 'wb')
    pickle.dump(trait_best_columns_dic, trait_cols_names_info_file)
    trait_cols_names_info_file.close()
