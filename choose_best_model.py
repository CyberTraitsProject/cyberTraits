import os
import pickle
import joblib


def take_best_models():
    """
    pass on all of the models results, takes the best results and summarize them.
    """
    all_models_dirs = r'C:\Users\onaki\CyberTraits\cyberTraits\final\summary all models results\all_models'
    dict = {'Extraversion': {},  # model: [cols]
            'Agreeableness': {},
            'Concientiousness': {},
            'Neurotism': {},
            'Openess': {},
            'Style': {}}

    for model_dir in os.listdir(all_models_dirs):
        all_trait_cols = pickle.load(open(os.path.join(all_models_dirs, model_dir, 'trait_cols_names_info.pkl'), 'rb'))
        for trait, cols in all_trait_cols.items():
            dict[trait][model_dir] = cols
    results_file_path = os.path.join(all_models_dirs, '..\\', 'summary_best_results')
    os.makedirs(results_file_path)
    for trait, models_cols in dict.items():
        file = open(os.path.join(results_file_path, f'{trait}_cols_results.txt'), 'w')
        for model, cols in models_cols.items():
            model_results_file = open(os.path.join(all_models_dirs, model, 'model_results.txt'), 'r')
            model_description_file = open(os.path.join(all_models_dirs, model, 'model_description.txt'), 'r')
            col_line = f'columns names: {cols}\n'
            lines = model_results_file.readlines()
            try:
                description = model_description_file.readlines()
            except:
                print()
            for idx, line in enumerate(lines):
                if col_line == line:
                    test_score = lines[idx+1]
                    train_score = lines[idx+2]
                    break
            s = f'{model}:\n{cols}\ntest score: {test_score}\ntrain score: {train_score}\n'
            file.write(f'{model}:\n{description}\n{len(cols)} {cols}\n{test_score}{train_score}\n')
            model_results_file.close()
        file.close()


def organize_best_to_one_file():
    """
    :return: pass on the best models, and summarize their results into one file.
    """
    main_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\final\final_models\64'
    final_descriptions = {'Extraversion': '',  # 'description': '',
                        'Agreeableness': '',
                        'Concientiousness': '',
                        'Neurotism': '',
                        'Openess': '',
                        'Style': ''}
    final_cols = {'Extraversion': '',  # 'cols': []
                        'Agreeableness': '',
                        'Concientiousness': '',
                        'Neurotism': '',
                        'Openess': '',
                        'Style': ''}
    for trait_dir_name in os.listdir(main_dir):
        trait_description_file = open(os.path.join(main_dir, trait_dir_name, 'description.txt'), 'r')
        cols_dict = pickle.load(open(os.path.join(main_dir, trait_dir_name, 'trait_cols_names_info.pkl'), 'rb'))
        final_descriptions[trait_dir_name] = trait_description_file.readlines()
        final_cols[trait_dir_name] = cols_dict[trait_dir_name]
        trait_description_file.close()

    # with open(os.path.join(main_dir, 'traits_cols_names_info.pkl'), 'wb')
    with open(os.path.join(main_dir, 'traits_descriptions.txt'), 'w') as final_description_file:
        for trait, description in final_descriptions.items():
            final_description_file.write(f'\n\n{trait}:\n')
            for line in description:
                final_description_file.write(str(line))

    pickle.dump(final_cols, open(os.path.join(main_dir, 'traits_cols_names_info.pkl'), 'wb'))


def copy_best_model_data_to_final_dir(final_dir, best_model_run_dir, trait):
    """
    Not In Use.
    create a final directory for the trait with its model data
    :param final_dir: the final data directory
    :param best_model_run_dir: the best model directory we chose
    :param trait: the name of the trait
    """
    trait_cols_file_path = os.path.join(best_model_run_dir, 'trait_cols_names_info.pkl')
    model_file_path = os.path.join(best_model_run_dir, 'traits_models', f'{trait}_model.pkl')
    description_text = 'linear_regression_random_forest_md_4_dt_3\n'\
                       'LinearRegression()\n'\
                       '10\n'\
                       "['power_state_3_day_avg', 'power_state_3_night_avg', 'calls_0_day_common', 'calls_0_day_median', 'calls_0_day_std', 'power_state_0_night_std', 'calls_percent_outgoing_day_avg', 'power_state_0_day_std', 'power_state_1_evening_std', 'calls_1_evening_common']\n"\
                       'test score:0.9873269022604326\n'\
                       'train score:0.7601169058808587\n'

    copy_trait_cols_file_path = os.path.join(final_dir, trait, 'trait_cols_names_info.pkl')
    copy_model_file_path = os.path.join(final_dir, trait, f'{trait}_model.pkl')
    description_file_path = os.path.join(final_dir, trait, 'description.txt')

    # copy the traits cols file
    pickle.dump(pickle.load(open(trait_cols_file_path, 'rb')), open(copy_trait_cols_file_path, 'wb'))

    # copy the ml model file
    joblib.dump(joblib.load(model_file_path), copy_model_file_path)

    # write the data to the description file
    open(description_file_path, 'w').write(description_text)


if __name__ == '__main__':
    take_best_models()
