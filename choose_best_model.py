import os
import pickle


def take_best_models():
    all_models_dirs = r'C:/Users/yafits/Documents/My Received Files/final_results'
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

    for trait, models_cols in dict.items():
        file = open(f'/Users/yafits/Documents/My Received Files/cols_results/{trait}_cols_results.txt', 'w')
        for model, cols in models_cols.items():
            model_results_file = open(os.path.join(all_models_dirs, model, 'model_results.txt'), 'r')
            model_description_file = open(os.path.join(all_models_dirs, model, 'model_description.txt'), 'r')
            col_line = f'columns names: {cols}\n'
            lines = model_results_file.readlines()
            description = model_description_file.readlines()
            for idx, line in enumerate(lines):
                if col_line == line:
                    test_score = lines[idx+1]
                    train_score = lines[idx+2]
                    break
            s = f'{model}:\n{cols}\ntest score: {test_score}\ntrain score: {train_score}\n'
            file.write(f'{model}:\n{description}\n{len(cols)} {cols}\n{test_score}{train_score}\n')
            model_results_file.close()
        file.close()


def orgenize_best_to_one_file():
    main_dir = r'C:\Users\yafits\Documents\My Received Files\final models'
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
        trait_model = f'{trait_dir_name}_model.pkl'
        # model_dict = pickle.load(open(os.path.join(main_dir, trait_dir_name, trait_model), 'rb'))
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


if __name__ == '__main__':
    orgenize_best_to_one_file()
