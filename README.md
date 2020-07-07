# cyberTraits
The process to run the code:
============================
1.  run the method - create_csv_for_machine_learning.
    this method found in the file main_process.py.
    this method do:
    1.1 run method questionnaires_main, that found in the file questionnaires.py, 
        and that create the pickle file that contains the questionnaires data.
    1.2 run on every candidate that has app data + questionnaires data, 
        and calculate him all the calculations we defined on every sensor.
        all the candidates need to have a folder data for every sensor.
    1.3 create a file machine_learning_data.csv that contains the data for the machine learning, without the traits scores.
    1.4 save the list of the candidates in a pickle file.

2.  run the method - organize_data_to_machine_learning_main.
    this method found in the file organize_data_to_machine_learning_main.py.
    this method do:
    2.1 remove the columns that has the same values in all of the lines.
    2.2 scaling the data.
    2.3 save a pickle file, "mean_scale_info.pkl", that contains the scale data for every column (mean & scale values).
    2.4 create for every trait, a csv file for machine learning.
        the files names are in this shape - "machine_learning_data_TRAIT_NAME.csv"

3.  run the method - machine_learning_single_model_main.
    this method found in the file machine_learning_single_model.py.
    in the variables classifier_model, and regression_model, you need to put the models you want to investigate.
    and in the variables classifier_model_n, and regression_model_n, you need to put them as a strings
    also, in the variable results_dir you need to put the path to the directory you want the results will be there.
    this method do:
    3.1 run on every file of the machine learning (of every trait).
    3.2 split the data NUM_SHUFFLES times, to train(75%) and test(25%).
    3.3 run the greedy algorithm.
        this algorithm choose the set of the columns that give the best avg test score on all of the split data.
        in the algorithm process, if it found a set of columns that better than the best previous one, 
        it print the results to the model_results.txt file (the columns indexes, columns names, 
        test score and train score).
    3.4 after choosing the best set of models, save them in pickle files, 
        with this name TRAIT_NAME_model_RANDOM_STATE_NUMBER.pkl. 
    3.5 save the set of the best columns, for every trait, in a pickle file that called - "trait_cols_names_info.pkl".
    
    run this method on number kinds of machine learning model, for getting the best results.
    
4. run the method - take_best_models.
   this method found in the file choose_best_model.py
   in the variable all_models_dirs, put the path to the directory where all the models results found there.
   this method do:
   4.1 pass on every model we checked.
   4.2 pass on every trait results in it, and takes the best result.
   4.3 copy the results (model dir name, model name, number of columns, columns names, test score and train score) 
       to a file with the name - TRAIT_NAME_cols_results.txt'.

5. pass on the traits models results, and decide which model you want for every trait.
   create a directory, with the following data:
   5.1 create directory for every trait, and put in it:
       5.1.1 the set of the model files, you chose.
       5.1.2 'description.txt' file, that contains 6 lines with the following data: model dir name, model name, 
              number of columns, columns names, test score and train score.
       5.1.3 the 'trait_cols_names_info.pkl' of this model.
   5.2 put into it the file 'mean_scale_info.pkl' (from step 3).
   
6. run the method - organize_best_to_one_file.
   this method found in the file choose_best_model.py
   in the variable main_dir, put the path to the directory you created in the previous step.
   this method do:
   6.1 pass on every trait directory.
   6.2 takes its description from the 'description.txt' file.
   6.3 takes its cols list from the 'trait_cols_names_info.pkl' file.
   6.4 save the collected data in two files 
       6.4.1 'trait_cols_names_info.pkl' that contains the final cols list for every trait.
       6.4.2 'traits_description.txt' that contains the description on every trait model results.
       
7. run the file cyber_traits_gui.exe.
   put the path to the data you want to predict.
   press on 'enter path'.
   press on 'organize and predict data'.
   the program will give you a message with the path that the predicted traits scores results found there.
   
GOOD LUCK!