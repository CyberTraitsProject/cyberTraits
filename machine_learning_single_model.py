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

classifier_model_n = 'DecisionTreeClassifier(max_depth=3)'
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

    # the number of the columns in the train data
    num_columns = len(X_train.columns)
    columns_indexes = range(num_columns)

    # will contain the data of the best final model
    best_final_model_data_dic = {'test_score': - float('inf'), 'train_score': 0, 'model': 0, 'cols_indexes': []}

    # pass on every number of columns
    for i in range(num_columns):
        print(i)

        # will contain the data of the best model that contains the best col to add
        best_model_data_dic = {'test_score': - float('inf'), 'train_score': 0, 'model': 0, 'cols_indexes': []}

        # pass on every column, and check if it good to add it
        for index in columns_indexes:

            # if already exists - continue
            if index in best_final_model_data_dic['cols_indexes']:
                continue
            else:
                columns_indexes_list = best_final_model_data_dic['cols_indexes'] + [index]

            cols_names = X_train.columns[columns_indexes_list]
            # takes only the current checked columns
            X_curr_train = X_train[cols_names]
            X_curr_test = X_test[cols_names]
            # the y values are the same
            y_curr_train = y_train
            y_curr_test = y_test

            # run the machine learning model on the current data
            if classifier:
                classifier_model = DecisionTreeClassifier(max_depth=3)
                test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                             classifier_model)
            else:
                regression_model = DecisionTreeRegressor(max_depth=3)
                test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                             regression_model)

            # check if the curr model is better that the best
            if test_score > best_model_data_dic['test_score']:
                best_model_data_dic['test_score'] = test_score
                best_model_data_dic['train_score'] = train_score
                best_model_data_dic['model'] = model
                best_model_data_dic['cols_indexes'] = columns_indexes_list

        # check if the curr final model is better that the best final model
        if best_model_data_dic['test_score'] > best_final_model_data_dic['test_score']:
            best_final_model_data_dic['test_score'] = best_model_data_dic['test_score']
            best_final_model_data_dic['train_score'] = best_model_data_dic['train_score']
            best_final_model_data_dic['model'] = best_model_data_dic['model']
            best_final_model_data_dic['cols_indexes'] = best_model_data_dic['cols_indexes']

            # write the data to the file
            if file:
                file.write('columns indexes: ' + str(best_final_model_data_dic['cols_indexes']) + '\n')
                file.write('columns names: ' + str(list(X_train.columns[best_final_model_data_dic['cols_indexes']])) + '\n')
                file.write('test score:' + str(best_final_model_data_dic['test_score']) + '\n')
                file.write('train score:' + str(best_final_model_data_dic['train_score']) + '\n\n')

    # create dir to the ml pickle files, and save them there
    trait_models_dir = os.path.join(results_dir, 'traits_models')
    if not os.path.isdir(trait_models_dir):
        os.makedirs(trait_models_dir)
    joblib.dump(best_final_model_data_dic['model'], os.path.join(trait_models_dir, f'{trait_name}_model.pkl'))

    # return the names of the best final columns
    cols_best_names = list(X_train.columns[best_final_model_data_dic['cols_indexes']])
    return cols_best_names


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

    # split the data for train and test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, shuffle=True)

    columns_best_names = run_greedy_algorithm_and_choose_the_best_model(results_dir, file, X_train, X_test, y_train, y_test,
                                                                        trait_name, classifier)
    # add the best final columns to the dictionary, in its trait
    trait_best_columns_dic[trait_name] = columns_best_names

    # return the final columns best names
    return columns_best_names


if __name__ == '__main__':

    results_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\all_models\decision_tree_md_3_dt_1'
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
