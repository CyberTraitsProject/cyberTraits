import pandas as pd
import os

questionnaires_info = {}    # {candidate_id1: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},
                            #  candidate_id2: {trait_1: score1, trait_2: score2, trait_3: score3, trait_4: score4, ....},...}


def questionnaires_main(questionnaires_dir):
    if not os.path.isdir(questionnaires_dir):
        print("Directory '", questionnaires_dir, "' not exists")
        exit(1)

    questionnaires_file = "candidate_submitted_trait_score_table_201911201800.csv"
    questionnaires_df = pd.read_csv(os.path.join(questionnaires_dir, questionnaires_file), usecols=['trait_name', 'candidate_national_id_number', 'trait_score_norm'])
    traits_names_list = questionnaires_df['trait_name']
    candidates_ids_list = questionnaires_df['candidate_national_id_number']
    scores_list = questionnaires_df['trait_score_norm']

    for i, candidate_id in enumerate(candidates_ids_list):
        if candidate_id not in questionnaires_info:
            questionnaires_info[candidate_id] = {}
        questionnaires_info[candidate_id][traits_names_list[i]] = scores_list[i]
    #print(questionnaires_info)
    return questionnaires_info



