import pickle
from questionnaires import traits_names
from sklearn.externals import joblib
import pandas as pd
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, AdaBoostClassifier


def predict_traits_on_new_data(data_path):
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
    trait_cols_names_info_file_path = "trait_cols_names_info.pkl"
    trait_cols_names_info_file = open(trait_cols_names_info_file_path, 'rb')
    trait_cols_names_info = pickle.load(trait_cols_names_info_file)
    trait_cols_names_info_file.close()

    # open the machine learning file
    machine_learning_file = "machine_learning_data.csv"
    machine_learning_df = pd.read_csv(machine_learning_file)

    candidates_list = machine_learning_df['candidate_id']

    predicted_results = {}

    for trait in traits_names:
        # Load the model from the file
        trait_model_from_joblib = joblib.load(os.path.join('traits_models', f'{trait}_model.pkl'))

        cols_list = trait_cols_names_info[trait]
        cur_trait_df = machine_learning_df[cols_list]

        # scale the data
        for col in cur_trait_df.columns:
            mean = mean_scale_info[col]['mean']
            scale = mean_scale_info[col]['scale']
            cur_trait_df[col] = cur_trait_df[col].apply(lambda x: (x - mean) / scale)

        # Use the loaded model to make predictions
        y_predicted = trait_model_from_joblib.predict(cur_trait_df)

        predicted_results[trait] = y_predicted

    return candidates_list, predicted_results
