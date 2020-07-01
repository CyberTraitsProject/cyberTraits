import pandas as pd
import pickle
from useful_functions import *

# the traits we are doing machine learning on them
traits_names = ['Extraversion', 'Agreeableness',
                'Concientiousness', 'Neurotism',
                'Openess', 'Style']


def questionnaires_main(questionnaires_dir):
    """
    this method takes from the questionnaires file the values of the traits to every candidate,
    and put it in a dictionary.
    :param questionnaires_dir: the directory that contains the file of the questionnaires data
    :return: save the order data in a pickle file - questionnaires_info.pkl
    """

    questionnaires_file = "questionnaires_data.csv"
    questionnaires_full_path_file = os.path.join(questionnaires_dir, questionnaires_file)

    # check that the directory and the file are exist
    check_if_dir_exists(questionnaires_dir)
    check_if_file_exists(questionnaires_full_path_file)

    # {candidate_id1: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},
    # candidate_id2: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},
    # ....,
    # candidate_idN: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....}}
    questionnaires_info = {}

    questionnaires_df = pd.read_csv(questionnaires_full_path_file, usecols=['Beiwe "patient" ID'] + traits_names)
    candidates_ids_list = questionnaires_df['Beiwe "patient" ID']
    traits_data_lists = []
    for trait in traits_names:
        traits_data_lists.append(questionnaires_df[trait])

    for i, candidate_id in enumerate(candidates_ids_list):
        questionnaires_info[candidate_id] = {}
        for j, trait in enumerate(traits_names):
            questionnaires_info[candidate_id][trait] = traits_data_lists[j][i]

    # save the questionnaires info in a pickle file
    questionnaires_info_file = open('questionnaires_info.pkl', 'wb')
    pickle.dump(questionnaires_info, questionnaires_info_file)
    questionnaires_info_file.close()


if __name__ == '__main__':
    questionnaires_main(r'C:\Users\onaki\CyberTraits\cyberTraits\questionnaires')
