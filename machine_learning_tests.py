import unittest
from organize_data_to_machine_learning import *
from global_tests_functions import *
from machine_learning_single_model import *


def get_scaled_data_in_df(scaled_file):
    # open the machine learning scaled file
    machine_learning_df = pd.read_csv(scaled_file)

    # get the columns and drop the last one (the trait values)
    columns = machine_learning_df.columns.tolist()
    cols_to_use = columns[:-1]
    machine_learning_df = pd.read_csv(scaled_file, usecols=cols_to_use)

    return machine_learning_df


def scale_data(file_to_scale, scaled_info_file_path):
    # open the pickle file, that contains the scaled info
    scaled_info_file = open(scaled_info_file_path, 'rb')
    scaled_info = pickle.load(scaled_info_file)
    scaled_info_file.close()

    # open the machine learning file, only the wanted cols
    machine_learning_df = pd.read_csv(file_to_scale, usecols=['candidate_id'] + list(scaled_info.keys()))

    # scale the data
    for col in machine_learning_df.columns[1:]:
        mean = scaled_info[col]['mean']
        scale = scaled_info[col]['scale']
        machine_learning_df[col] = machine_learning_df[col].apply(lambda x: (x - mean) / scale)

    return machine_learning_df


def get_candidates_traits_scores(scaled_file):
    # takes the trait name from the file name
    trait_name = (scaled_file.split('_')[-1]).split('.')[0]
    # open the machine learning scaled file
    machine_learning_df = pd.read_csv(scaled_file, usecols=['candidate_id', trait_name])

    return machine_learning_df, trait_name


def give_trait_score_for_every_candidate(trait_name, origin_file, questionnaires_file):
    # open the questionnaires file
    questionnaires_df = pd.read_csv(questionnaires_file, usecols=['Beiwe "patient" ID', trait_name])
    beiwe_id_list = list(questionnaires_df['Beiwe "patient" ID'])
    scores_list = list(questionnaires_df[trait_name])
    # open the origin file
    origin_df = pd.read_csv(origin_file, usecols=['candidate_id'])
    candidates_list = origin_df['candidate_id']

    candidates_trait_scores_dic = {'candidate_id': [], trait_name: []}

    for candidate in candidates_list:
        index = beiwe_id_list.index(candidate)
        trait_score = scores_list[index]
        candidates_trait_scores_dic['candidate_id'].append(candidate)
        candidates_trait_scores_dic[trait_name].append(trait_score)

    candidates_trait_scores_df = pd.DataFrame(data=candidates_trait_scores_dic)
    return candidates_trait_scores_df


def get_cols_list_test_train_score_for_trait(model_results_dir, trait):
    description_file_path = os.path.join(model_results_dir, trait, 'description.txt')
    with open(description_file_path, 'r') as description_file:
        description_lines_data = description_file.readlines()
        # the list of the cols found in line 4
        cols_list = description_lines_data[3].replace("'", '').replace(' ', '').split('[')[1].split(']')[0].split(',')
        # the test score found in line 5
        test_score = float(description_lines_data[4].replace("\n", '').split(':')[1])
        # the train score found in line 4
        train_score = float(description_lines_data[5].replace("\n", '').split(':')[1])
        print('description file', cols_list)
    return cols_list, test_score, train_score


def find_best_cols_and_its_fitted_model(model_results_dir, ml_data_dir, trait):
    optional_ml_models_dic = {'LinearRegression()': LinearRegression(),
                              'RANSACRegressor(random_state=38, min_samples=5)': RANSACRegressor(random_state=38, min_samples=5),
                              'DecisionTreeRegressor(max_depth=3)': DecisionTreeRegressor(max_depth=3),
                              'DecisionTreeClassifier(max_depth=3)': DecisionTreeClassifier(max_depth=3),
                              'DecisionTreeClassifier(max_depth=5)': DecisionTreeClassifier(max_depth=5),
                              'DecisionTreeRegressor(max_depth=5)': DecisionTreeRegressor(max_depth=5),
                              'RandomForestClassifier(max_depth=4)': RandomForestClassifier(max_depth=4),
                              'RandomForestClassifier()': RandomForestClassifier(),
                              'RandomForestRegressor()': RandomForestRegressor(),
                              'RandomForestClassifier(max_depth=3)': RandomForestClassifier(max_depth=3),
                              'RandomForestRegressor(max_depth=3)': RandomForestRegressor(max_depth=3),
                              'RandomForestClassifier(max_depth=3, random_state=0)': RandomForestClassifier(max_depth=3, random_state=0),
                              'RandomForestRegressor(max_depth=3, random_state=0)': RandomForestRegressor(max_depth=3, random_state=0),
                              'RandomForestClassifier(random_state=0)': RandomForestClassifier(random_state=0),
                              'RandomForestRegressor(random_state=0)': RandomForestRegressor(random_state=0),
                              'RandomForestClassifier(max_depth=5)': RandomForestClassifier(max_depth=5),
                              'AdaBoostClassifier()': AdaBoostClassifier(),
                              'RANSACRegressor(random_state=42, min_samples=3)': RANSACRegressor(random_state=42, min_samples=3)
                              }
    description_file_path = os.path.join(model_results_dir, trait, 'description.txt')
    with open(description_file_path, 'r') as description_file:
        # the name of the model found in line 2
        # its format for example -  DecisionTreeRegressor(max_depth=3)
        model_str = description_file.readlines()[1].replace('\n', '')

    global regression_model
    regression_model = optional_ml_models_dic[model_str]
    ml_trait_file_path = os.path.join(ml_data_dir, f'machine_learning_data_{trait}.csv')
    if trait == 'Style':
        cols_names = machine_learning_model_main(None, ml_trait_file_path, trait, classifier=True)
    else:
        cols_names = machine_learning_model_main(None, ml_trait_file_path, trait, classifier=False)
    ml_model = joblib.load(os.path.join('traits_models', f'{trait}_model.pkl'))

    return cols_names, ml_model


def get_X_and_y_data(ml_data_dir, trait):
    # open the X y data files
    '''X_train_df = pd.read_csv(os.path.join(model_results_dir, 'X_y_data', 'X_train.csv'))
    X_test_df = pd.read_csv(os.path.join(model_results_dir, 'X_y_data', 'X_test.csv'))
    y_train_df = pd.read_csv(os.path.join(model_results_dir, 'X_y_data', 'y_train.csv'))
    y_test_df = pd.read_csv(os.path.join(model_results_dir, 'X_y_data', 'y_test.csv'))'''
    machine_learning_df = pd.read_csv(os.path.join(ml_data_dir, f'machine_learning_data_{trait}.csv'))

    # all the columns, except of the first column(the candidate id) and the last column(the y)
    X_columns_names = machine_learning_df.columns[1:-1]

    # input values
    X = machine_learning_df[X_columns_names]
    # output values
    y = machine_learning_df[trait]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, shuffle=True)

    return X_train, X_test, y_train, y_test


def find_best_cols(model_results_dir, trait):
    # get the cols names from the pickle file
    traits_cols_file_path = os.path.join(model_results_dir, trait, 'trait_cols_names_info.pkl')
    traits_cols_file = open(traits_cols_file_path, 'rb')
    traits_cols_dic = pickle.load(traits_cols_file)
    traits_cols_file.close()
    cols_list = traits_cols_dic[trait]
    print('pickle file:',cols_list)
    return cols_list


def get_ml_model(model_results_dir, trait):
    # get the model from the pickle file
    model_file_path = os.path.join(model_results_dir, trait, f'{trait}_model.pkl')
    trait_model = joblib.load(model_file_path)
    return trait_model


def calc_train_test_scores_of_model(ml_data_dir, trait_model, cols_list, trait):
    X_train, X_test, y_train, y_test = get_X_and_y_data(ml_data_dir, trait)
    test_score = trait_model.score(X_test[cols_list], y_test)
    train_score = trait_model.score(X_train[cols_list], y_train)
    return test_score, train_score


def get_traits_cols_final_dic(model_results_dir):
    # get the cols names from the pickle file
    traits_cols_file_path = os.path.join(model_results_dir, 'traits_cols_names_info.pkl')
    traits_cols_file = open(traits_cols_file_path, 'rb')
    traits_cols_dic = pickle.load(traits_cols_file)
    traits_cols_file.close()
    return traits_cols_dic


def get_trait_cols_for_trait(model_results_dir, trait):
    # get the cols names from the pickle file
    traits_cols_file_path = os.path.join(model_results_dir, trait, 'trait_cols_names_info.pkl')
    traits_cols_file = open(traits_cols_file_path, 'rb')
    traits_cols_dic = pickle.load(traits_cols_file)
    traits_cols_file.close()
    return traits_cols_dic[trait]


class MachineLearningTests(unittest.TestCase):

    def setUp(self):
        self.scaled_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\machine_learning_data_Agreeableness.csv'
        self.origin_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\machine_learning_data_day_times_3.csv'
        self.scaled_info_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\mean_scale_info.pkl'
        self.questionnaires_file = r'C:\Users\onaki\CyberTraits\cyberTraits\questionnaires\questionnaires_data.csv'
        self.model_results_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\final_models'
        self.ml_data_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3'

    def test_scaling_data(self):
        """Checks if mean and the scale values for every columns saved well"""
        organize_data_scaled_data_df = get_scaled_data_in_df(self.scaled_file)
        test_scaled_data_df = scale_data(self.origin_file, self.scaled_info_file)

        pd.testing.assert_frame_equal(organize_data_scaled_data_df, test_scaled_data_df)

    def test_traits_values_collected_well(self):
        """Checks if the traits values collected well to every candidate"""
        organize_data_traits_candidates_scores_df, trait_name = get_candidates_traits_scores(self.scaled_file)
        test_traits_candidates_scores_df = give_trait_score_for_every_candidate(trait_name,
                                                                                self.origin_file,
                                                                                self.questionnaires_file)

        pd.testing.assert_frame_equal(organize_data_traits_candidates_scores_df, test_traits_candidates_scores_df)

    def test_check_model_cols_and_scores_are_correct(self):
        """Checks if the model that saved and its columns are right"""
        for trait in traits_names:
            # check that the columns are the same
            machine_learning_trait_cols_list, test_score, train_score = get_cols_list_test_train_score_for_trait(
                                                                            self.model_results_dir, trait)
            test_trait_cols_list = find_best_cols(self.model_results_dir, trait)
            self.assertEqual(machine_learning_trait_cols_list, test_trait_cols_list)

            # check the number of the columns in the ml model is equal to the number of the cols
            trait_model = get_ml_model(self.model_results_dir, trait)
            try:
                self.assertEqual(len(test_trait_cols_list), trait_model.n_features_)
            except:
                # linear regression doesnt have the attribute n_features_. it has rank_ instead.
                self.assertEqual(len(test_trait_cols_list), trait_model.rank_)

            # check that the scores on the test and the train data are the same
            test_test_score, test_train_score = calc_train_test_scores_of_model(self.ml_data_dir, trait_model,
                                                                                test_trait_cols_list, trait)
            self.assertEqual(test_score, test_test_score)
            self.assertEqual(train_score, test_train_score)

    def test_check_final_cols_are_correct(self):
        """Checks if the final cols are right"""
        traits_cols_dic = get_traits_cols_final_dic(self.model_results_dir)

        for trait in traits_names:
            machine_learning_final_traits_cols = traits_cols_dic[trait]
            test_final_traits_cols = get_trait_cols_for_trait(self.model_results_dir, trait)

            self.assertEqual(machine_learning_final_traits_cols, test_final_traits_cols)


if __name__ == '__main__':
    unittest.main()
