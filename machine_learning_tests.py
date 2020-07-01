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


def get_cols_list_for_trait(model_results_dir, trait):
    description_file_path = os.path.join(model_results_dir, trait, 'description.txt')
    with open(description_file_path, 'r') as description_file:
        # the list of the cols found in line 4
        cols_list = description_file.readlines()[3].replace("'",'').split('[')[1].split(']')[0].split(',')
    return cols_list


def find_best_cols_and_its_fitted_model(model_results_dir, ml_data_dir, trait):
    optional_ml_models_dic = {'LinearRegression()': LinearRegression(),
                              'RANSACRegressor(random_state=38, min_samples=5)': RANSACRegressor(random_state=38, min_samples=5),
                              'DecisionTreeRegressor(max_depth=3)': DecisionTreeRegressor(max_depth=3),
                              'DecisionTreeClassifier(max_depth=5)': DecisionTreeClassifier(max_depth=5)}
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


class MachineLearningTests(unittest.TestCase):

    def setUp(self):
        self.scaled_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\machine_learning_data_Agreeableness.csv'
        self.origin_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\machine_learning_data_day_times_3.csv'
        self.scaled_info_file = r'C:\Users\onaki\CyberTraits\cyberTraits\final\day_times_3\mean_scale_info.pkl'
        self.questionnaires_file = r'C:\Users\onaki\CyberTraits\cyberTraits\questionnaires\questionnaires_data.csv'
        self.model_results_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\final models'
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

    def test_check_model_saved_well(self):
        """Checks if the models that saved and their columns are right"""
        for trait in traits_names:
            machine_learning_trait_cols_list = get_cols_list_for_trait(self.model_results_dir, trait)
            test_trait_cols_list, ml_model = find_best_cols_and_its_fitted_model(self.model_results_dir,
                                                                                 self.ml_data_dir, trait)

            self.assertEqual(machine_learning_trait_cols_list, test_trait_cols_list)


if __name__ == '__main__':
    unittest.main()
