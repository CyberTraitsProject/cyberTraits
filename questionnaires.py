import pandas as pd
import os

questionnaires_info = {}  # {candidate_id1: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},

traits_names = ['Extraversion', 'Agreeableness',
                'Concientiousness', 'Neurotism', 'Openess']

#  candidate_id2: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},...}


def questionnaires_main(questionnaires_dir):
    if not os.path.isdir(questionnaires_dir):
        print("Directory '", questionnaires_dir, "' not exists")
        exit(1)

    questionnaires_file = "questionnaires_data.csv"

    questionnaires_df = pd.read_csv(os.path.join(questionnaires_dir, questionnaires_file), usecols=['Beiwe "patient" ID'] + traits_names)
    candidates_ids_list = questionnaires_df['Beiwe "patient" ID']
    traits_data_lists = []
    for trait in traits_names:
        traits_data_lists.append(questionnaires_df[trait])

    for i, candidate_id in enumerate(candidates_ids_list):
        questionnaires_info[candidate_id] = {}
        for j, trait in enumerate(traits_names):
            questionnaires_info[candidate_id][trait] = traits_data_lists[j][i]
    print(questionnaires_info)
    return questionnaires_info

#questionnaires_main(r'C:\Users\onaki\CyberTraits\cyberTraits\questionnaires')
