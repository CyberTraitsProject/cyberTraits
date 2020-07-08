import pickle
from questionnaires import traits_names
import pandas as pd
import os
from machine_learning_single_model import *
import joblib


def convert_list_to_dic_type(columns_list):
    """
    :param columns_list: the list of the columns
    :return: a dictionary that defines all the columns as float type, except of the column candidate_id
    """
    types_dict = {}
    for col in columns_list:
        if col != 'candidate_id':
            types_dict[col] = float
    return types_dict


def predict_traits_on_new_data():
    """
    :param final_ml_data_path: the path to the machine learning data results
    :return: the candidates list its predict on them and their predicted traits values
    """

    # {col_name1: {mean: mean1, scale: scale1},
    #  col_name2: {mean: mean2, scale: scale2}, ...
    #  col_nameN: {mean: meanN, scale: scaleN}}
    mean_scale_info_file_path = "mean_scale_info.pkl"
    mean_scale_info_file = open(mean_scale_info_file_path, 'rb')
    mean_scale_info = pickle.load(mean_scale_info_file)
    mean_scale_info_file.close()

    # {trait_name1: [col_name1, col_name2, ... , col_nameN1],
    #  trait_name2: [col_name1, col_name2, ... , col_nameN2], ...,
    #  trait_nameM: [col_name1, col_name2, ... , col_nameNM]}
    trait_cols_names_info_file_path = "traits_cols_names_info.pkl"
    trait_cols_names_info_file = open(trait_cols_names_info_file_path, 'rb')
    trait_cols_names_info = pickle.load(trait_cols_names_info_file)
    trait_cols_names_info_file.close()

    # open the machine learning file
    machine_learning_file = "machine_learning_data.csv"
    machine_learning_df = pd.read_csv(machine_learning_file)
    columns_list = machine_learning_df.columns

    dict_types = convert_list_to_dic_type(columns_list)
    # open the machine learning file
    machine_learning_file = "machine_learning_data.csv"
    machine_learning_df = pd.read_csv(machine_learning_file, dtype=dict_types)

    candidates_list = machine_learning_df['candidate_id']

    predicted_results = {}

    # pass on every trait
    for trait in traits_names:
        trait_models_list = []
        # pass on every model of the trait and save it in a list
        for i in range(START_RANDOM_STATE, START_RANDOM_STATE + NUM_SHUFFLES * 10, 10):
            trait_model_from_joblib = joblib.load(os.path.join(trait,  f'{trait}_model_{i}.pkl'))
            trait_models_list.append(trait_model_from_joblib)

        # takes the cols that this trait need for the models
        cols_list = trait_cols_names_info[trait]
        # takes the data of these cols
        cur_trait_df = machine_learning_df[cols_list]

        # scale the data
        for col in cur_trait_df.columns:
            mean = mean_scale_info[col]['mean']
            scale = mean_scale_info[col]['scale']
            # convert the column to float (in case the column is zero's, it defined as int)
            #cur_trait_df[col] = cur_trait_df[col].astype(float)
            for index in range(cur_trait_df.shape[0]):
                scaled_value = (cur_trait_df.loc[index, col] - mean) / scale
                cur_trait_df.at[index, col] = scaled_value

        # predict the data, by predicting with all the models and taking the average
        y_predicted = 0
        for i in range(NUM_SHUFFLES):
            # use the loaded model to make predictions
            y_predicted += trait_models_list[i].predict(cur_trait_df)
        y_predicted_avg = y_predicted / NUM_SHUFFLES

        if trait == 'Style':
            # classifier data --> need whole number
            predicted_results[trait] = y_predicted_avg.round()
        else:
            predicted_results[trait] = y_predicted_avg

    return candidates_list, predicted_results
