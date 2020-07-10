import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression, RANSACRegressor
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split
from questionnaires import traits_names
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from useful_functions import *
import joblib
import numpy as np

classifier_model_n = 'RandomForestClassifier(max_depth=3)'
regression_model_n = 'RandomForestRegressor(max_depth=3)'

trait_best_columns_dic = {}

NUM_SHUFFLES = 10
START_RANDOM_STATE = 2
RS_DIS = 10

# will contain the X, y data, in this shape:
# [{X_data: X_train_df_2,   y_train: y_train_df_2,  X_test: X_test_df_2,    y_test: y_test_df_2},
#  {X_data: X_train_df_12,  y_train: y_train_df_12, X_test: X_test_df_12,   y_test: y_test_df_12}, ... ,
#  {X_data: X_train_df_92,  y_train: y_train_df_92, X_test: X_test_df_92,   y_test: y_test_df_92}]
X_y_split_data = []


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


def run_greedy_algorithm_and_choose_the_best_model(results_dir, file, trait_name, classifier):
    """
    run the greedy algorithm on all the columns.
    try the best single column, than add it the column that gives the best test score, than add it another one and..
    until we have all of the columns.
    on every set, takes only these columns and run all of the machine learning models on it.
    writes all the results in the file.
    and save the models with he best results in pickle files.
    :param results_dir: the path to put the results there
    :param file: the file to write there the results
    :param trait_name: the name of the trait
    :param classifier: is a classifier problem or a regression problem
    :return: the names of the best columns
    """

    # the number of the columns in the train data
    num_columns = len(X_y_split_data[0]['X_train'].columns)
    columns_indexes = range(num_columns)

    # the list of the best indexes
    best_final_cols_indexes = []

    # will contain the data of the all the models, in this shape:
    # { test_score_1: {'train_score': train_score_1, 'models': models_1, 'cols_indexes': cols_indexes_1},
    #   test_score_2:  {'train_score': train_score_2, 'models': models_2, 'cols_indexes': cols_indexes_2},
    #   ...
    #   test_score_N:  {'train_score': train_score_N, 'models': models_N, 'cols_indexes': cols_indexes_N}}
    best_final_models_data_dic = {}

    # pass on every number of columns
    for i in range(num_columns):
        print(i)

        # will contain the data of the best model that contains the best col to add
        best_model_data_dic = {'test_score': - float('inf'), 'train_score': 0, 'models': [], 'cols_indexes': []}

        # pass on every column, and check if it good to add it
        for index in columns_indexes:

            # if already exists - continue
            if index in best_final_cols_indexes:
                continue
            else:
                columns_indexes_list = best_final_cols_indexes + [index]

            cur_cols_results = {'test_score_list': [], 'train_score_list': [], 'model_list': []}

            for idx in range(NUM_SHUFFLES):

                cols_names = X_y_split_data[idx]['X_train'].columns[columns_indexes_list]
                # takes only the current checked columns
                X_curr_train = X_y_split_data[idx]['X_train'][cols_names]
                X_curr_test = X_y_split_data[idx]['X_test'][cols_names]
                # the y values are the same
                y_curr_train = X_y_split_data[idx]['y_train']
                y_curr_test = X_y_split_data[idx]['y_test']

                # run the machine learning model on the current data
                if classifier:
                    classifier_model = RandomForestClassifier(max_depth=3)
                    test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                                 classifier_model)
                else:
                    regression_model = RandomForestRegressor(max_depth=3)
                    test_score, train_score, model = check_model(X_curr_train, X_curr_test, y_curr_train, y_curr_test,
                                                                 regression_model)

                cur_cols_results['test_score_list'].append(test_score)
                cur_cols_results['train_score_list'].append(train_score)
                cur_cols_results['model_list'].append(model)

            avg_test_score = (np.array(cur_cols_results['test_score_list'])).mean()
            # check if the curr model is better that the best
            if avg_test_score > best_model_data_dic['test_score']:
                best_model_data_dic['test_score'] = avg_test_score
                best_model_data_dic['train_score'] = (np.array(cur_cols_results['train_score_list'])).mean()
                best_model_data_dic['models'] = cur_cols_results['model_list']
                best_model_data_dic['cols_indexes'] = columns_indexes_list

        best_final_cols_indexes = best_model_data_dic['cols_indexes']

        if best_model_data_dic['test_score'] not in best_final_models_data_dic:
            best_final_models_data_dic[best_model_data_dic['test_score']] = {
                'train_score': best_model_data_dic['train_score'],
                'models': best_model_data_dic['models'],
                'cols_indexes': best_model_data_dic['cols_indexes']}

            # write the data to the file
            file.write('columns indexes: ' + str(
                best_final_models_data_dic[best_model_data_dic['test_score']]['cols_indexes']) + '\n')
            file.write('columns names: ' + str(
                list(X_y_split_data[0]['X_train'].columns[
                         best_final_models_data_dic[best_model_data_dic['test_score']]['cols_indexes']])) + '\n')
            file.write('test score:' + str(best_model_data_dic['test_score']) + '\n')
            file.write('train score:' + str(
                best_final_models_data_dic[best_model_data_dic['test_score']]['train_score']) + '\n\n')

    # create dir to the ml pickle files, and save them there
    trait_models_dir = os.path.join(results_dir, 'traits_models')
    if not os.path.isdir(trait_models_dir):
        os.makedirs(trait_models_dir)

    test_final_best_score = max(best_final_models_data_dic)

    for idx in range(NUM_SHUFFLES):
        cur_rs = idx * RS_DIS + START_RANDOM_STATE
        joblib.dump(best_final_models_data_dic[test_final_best_score]['models'][idx],
                    os.path.join(trait_models_dir, f'{trait_name}_model_{cur_rs}.pkl'))

    # return the names of the best final columns
    cols_best_names = list(X_y_split_data[0]['X_train'].columns[
                               best_final_models_data_dic[test_final_best_score]['cols_indexes']])
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

    # run on random_state = 2, 12, 22, ..., 102
    cur_random_state = START_RANDOM_STATE
    for i in range(NUM_SHUFFLES):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=cur_random_state,
                                                            shuffle=True)
        X_y_split_data.append({'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test})
        cur_random_state += RS_DIS

    columns_best_names = run_greedy_algorithm_and_choose_the_best_model(results_dir, file, trait_name, classifier)
    # add the best final columns to the dictionary, in its trait
    trait_best_columns_dic[trait_name] = columns_best_names

    # return the final columns best names
    return columns_best_names


def run_model_on_specific_cols(scaled_data_dir, final_models_dir, model, trait):
    """
    fit specific model, with splitting the data with specific random_state
    :param scaled_data_dir: the path to the scaled data
    :param final_models_dir: the path to the final models results
    :param model: the model to fit
    :param trait: the name of the trait
    """
    machine_learning_df = pd.read_csv(os.path.join(scaled_data_dir, f'machine_learning_data_{trait}.csv'))

    # all the columns, except of the first column(the candidate id) and the last column(the y)
    X_columns_names = machine_learning_df.columns[1:-1]

    # input values
    X = machine_learning_df[X_columns_names]
    # output values
    y = machine_learning_df[trait]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=12, shuffle=True)

    traits_cols_file_path = os.path.join(final_models_dir, 'traits_cols_names_info.pkl')
    trait_cols_list = pickle.load(open(traits_cols_file_path, 'rb'))[trait]

    # learn only on the cols list
    X_train = X_train[trait_cols_list]
    X_test = X_test[trait_cols_list]

    test_score, train_score, model = check_model(X_train, X_test, y_train, y_test, model)

    # save the model
    joblib.dump(model, os.path.join(final_models_dir, trait, f'{trait}_model_12.pkl'))

    open(os.path.join(final_models_dir, trait, 'description_12.txt'), 'w').write(f'test_score:{test_score}\n'
                                                                                 f'train_score:{train_score}')


def machine_learning_single_model_main(specific_run=False):
    """
    :param specific_run: boolean value, if to run the normal run (greedy model) or not
    """

    scaled_data_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3'

    if specific_run:
        # run specific model on specific cols, wo the greedy model
        model = LinearRegression()
        trait = 'Concientiousness'
        final_models_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\final_models'
        run_model_on_specific_cols(scaled_data_dir, final_models_dir, model, trait)
    else:
        results_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\all_models\random_forest_md_3_dt_3_64_ori'
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)

        description_file = os.path.join(results_dir, 'model_description.txt')
        if not os.path.isfile(description_file):
            open(description_file, 'w').close()

        file = open(os.path.join(results_dir, 'model_results.txt'), 'w')
        file.write('The Classifier Model : ' + classifier_model_n + '\n')
        file.write('The Regression Model : ' + regression_model_n + '\n')

        # run the models on all of the traits, for the trait 'Style' - run a classifier model
        for trait in traits_names:
            global X_y_split_data
            X_y_split_data = []
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


if __name__ == '__main__':
    machine_learning_single_model_main()
