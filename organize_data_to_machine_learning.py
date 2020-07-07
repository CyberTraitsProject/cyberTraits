from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectKBest, GenericUnivariateSelect
import numpy as np
import pickle
from questionnaires import traits_names
import pandas as pd
from useful_functions import *


def scaling_data(machine_learning_df):
    """
    this method scale the data.
    i.e.- takes every cell, and puts in it = (cell_value - cells_col_mean) / cells_col_std
    :param machine_learning_df: machine learning data frame - the data itself
    :return: the data frame after scaling
    """

    # copy to a new data frame
    scaled_features = machine_learning_df.copy()

    # takes all the columns except of the column candidate_name
    col_names = machine_learning_df.columns[1:]
    features = scaled_features[col_names]

    # calculate the scaling only on the values and not on the titles
    scaler = StandardScaler().fit(features.values)
    features = scaler.transform(features.values)

    mean_scale_dic = {}
    mean_list = scaler.mean_
    scale_list = scaler.scale_
    for i, col_name in enumerate(col_names):
        mean_scale_dic[col_name] = {'mean': mean_list[i], 'scale': scale_list[i]}
    # save the questionnaires info in a pickle file
    mean_scale_info_file = open('mean_scale_info.pkl', 'wb')
    pickle.dump(mean_scale_dic, mean_scale_info_file)
    mean_scale_info_file.close()

    # insert the scaled value to the data frame
    scaled_features[col_names] = features

    return scaled_features


def create_machine_learning_file_to_every_trait(machine_learning_df, candidates_list, questionnaires_info):
    """
    this method create for every trait a csv file, that contains the y values -
    the results of the traits from the questionnaires.
    :param machine_learning_df: machine learning data frame - the data itself
    :param candidates_list: the list of the candidates to put their traits values
    :param questionnaires_info: the questionnaires information of every candidate
    """

    # add the data of the trait for every candidate
    # currently, create 5 files, that every file contains the data of the specific trait
    for trait in traits_names:
        trait_scores = []
        # pass on the candidates, and add them the trait score
        for i, candidate in enumerate(candidates_list):
            trait_scores.append(questionnaires_info[candidate][trait])
        curr_machine_learning_df = machine_learning_df.copy()
        curr_machine_learning_df[trait] = trait_scores

        # feature selection - method #2
        #curr_machine_learning_df = feature_selection_by_select_k_best(curr_machine_learning_df)

        curr_machine_learning_df.to_csv(f'machine_learning_data_{trait}.csv', index=False)
        #curr_machine_learning_df = machine_learning_df.drop([trait], axis=1)


def feature_selection_by_variance_threshold(machine_learning_df):
    """
    this method select the columns that have variance threshold
    :param machine_learning_df: machine learning data frame - the data itself
    :return: the data frame after the feature selection
    """

    # copy to a new data frame
    features_selection = machine_learning_df.copy()

    # takes all the columns except of the column candidate_name
    col_names = machine_learning_df.columns[1:]
    features = features_selection[col_names]

    sel = VarianceThreshold()   # threshold=(.8 * (1 - .8)))
    sel.fit_transform(features)

    cols = sel.get_support(indices=True)
    print(type(cols))
    features_df_new = features_selection.iloc[:, np.concatenate((np.array([0]), cols + 1))]
    print(features_df_new.head())

    return features_df_new


def feature_selection_by_select_k_best(machine_learning_df):
    """
    select the k best columns, that giving the most well data, and return it.
    :param machine_learning_df: machine learning data frame - the data itself
    :return: the data frame after the feature selection (the data of the k best cols)
    """

    # copy to a new data frame
    features_selection = machine_learning_df.copy()

    # takes all the columns except of the column candidate_name and the trait_score
    print('#1', machine_learning_df.head())
    col_names = machine_learning_df.columns[1:-1]
    features = features_selection[col_names]

    # Create and fit selector
    selector = SelectKBest(GenericUnivariateSelect, k=7)
    last_col = machine_learning_df.columns[-1]
    last_col_index = len(machine_learning_df.columns) - 2
    target = machine_learning_df[last_col]
    selector.fit(features, target)
    print('#2', features.head())
    # Get columns to keep and create new data frame with those only
    cols = selector.get_support(indices=True)
    print('--------------------------', np.concatenate((np.array([0]), cols + 1)))
    cols_indexes = np.concatenate((np.array([0]), cols + 1))
    print('#3', features.head())
    features_df_new = features_selection.iloc[:, cols_indexes]
    features_df_new[last_col] = features_selection[last_col]

    return features_df_new


def get_candidates_list():
    """
    open the pickle file that contains all the candidates
    :return: the candidates list that have both app & questionnaires data
    """

    # load the candidates list
    candidates_list_file_path = 'candidates_list.pkl'
    check_if_file_exists(candidates_list_file_path)
    candidates_list_file = open(candidates_list_file_path, 'rb')
    candidates_dic = pickle.load(candidates_list_file)
    candidates_list_file.close()

    # collect all the candidates id that have app data and questionnaires data
    candidates_list = [candidate_id for candidate_id in candidates_dic if candidates_dic[candidate_id]]
    return candidates_list


def organize_data_to_machine_learning_main():
    """
    this method organize the data for doing the machine learning:
    1. load the questionnaires info from the pickle file.
    2. load the candidates list from the pickle file.
    3. scale the data.
    4. do feature selection by variance threshold.
    5. create a machine learning file to every trait, with the y data = the trait score
       (also do feature selection, but currently it works bad)
    """

    candidates_list = get_candidates_list()

    # load the questionnaires data
    questionnaires_info_file_path = 'questionnaires_info.pkl'
    check_if_file_exists(questionnaires_info_file_path)
    questionnaires_info_file = open(questionnaires_info_file_path, 'rb')
    questionnaires_info = pickle.load(questionnaires_info_file)
    questionnaires_info_file.close()

    # open the machine learning file
    machine_learning_file = "machine_learning_data_day_times_3.csv"
    check_if_file_exists(machine_learning_file)
    machine_learning_df = pd.read_csv(machine_learning_file)

    # feature selection - method #1
    machine_learning_df = feature_selection_by_variance_threshold(machine_learning_df)

    # scale the data - every cell will be (cell_value - cell_cols_mean) / cell_cols_std
    machine_learning_df = scaling_data(machine_learning_df)

    # create to every trait, a machine learning file that contains to every candidate he's score to this trait
    create_machine_learning_file_to_every_trait(machine_learning_df, candidates_list, questionnaires_info)


if __name__ == '__main__':
    organize_data_to_machine_learning_main()
