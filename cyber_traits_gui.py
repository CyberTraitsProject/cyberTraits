from tkinter import *
from tkinter.ttk import *
from useful_functions import *
from main_process import create_csv_for_machine_learning
from predict_traits_score import predict_traits_on_new_data
# import multiprocessing
import time
import numpy as np

data_folder = ''


# Function responsible for the updation
# of the progress bar value
def darw_bar():
    progress['value'] = 20
    window.update_idletasks()
    time.sleep(0.5)

    progress['value'] = 40
    window.update_idletasks()
    time.sleep(0.5)

    progress['value'] = 50
    window.update_idletasks()
    time.sleep(0.5)

    progress['value'] = 60
    window.update_idletasks()
    time.sleep(0.5)

    progress['value'] = 80
    window.update_idletasks()
    time.sleep(0.5)

    progress['value'] = 100


def folder_path_clicked():
    """
    handle the button "enter path"
    """
    global data_folder
    data_folder = path_txt.get()
    predicted_done_lbl.grid_forget()
    if not os.path.isdir(data_folder):
        error_path_lbl.grid(column=2, row=0)
        error_path_lbl.configure(text='Path not found, Please enter another one')
        organize_predict_data_btn.grid_forget()
    else:
        error_path_lbl.grid_forget()
        organize_predict_data_btn.grid(column=0, row=2)


def organize_predict_clicked():
    """
    handle the button "organize and predict data"
    """
    wait_lbl.grid(column=2, row=2)
    progress.grid(column=1, row=2)
    data_folder_n = os.path.normpath(data_folder)

    # start to fulfill the progress bar
    darw_bar()
    # create the csv file for machine learning
    create_csv_for_machine_learning(data_folder_n, is_research=False)
    # predict the traits scores
    predicted_traits_file = predict_traits()

    wait_lbl.grid_forget()
    progress.grid_forget()

    predicted_done_lbl.grid(column=0, row=3)
    predicted_done_lbl['text'] = 'Predicted Done.\nResults found in file:\n' + \
                                 os.path.join(os.path.abspath(os.getcwd()), predicted_traits_file)


def predict_traits():
    """
    predict the traits values of the requested candidates
    :return: the path to the predicted results
    """
    final_ml_data_path = r'C:\Users\onaki\CyberTraits\cyberTraits\final\final_models'
    # {{trait1: [y predicted lists for all the candidates],
    #   trait2: [y predicted lists for all the candidates], ... ,
    #   traitN: [y predicted lists for all the candidates]}
    candidates_list, predicted_values_dic = predict_traits_on_new_data(final_ml_data_path)

    # print the results of the prediction
    predicted_traits_file = 'predicted_traits.csv'
    titles_list = ['candidate_id'] + list(predicted_values_dic)
    predicted_traits_list = []
    # pass on every candidate
    for i, candidate in enumerate(candidates_list):
        curr_candidate_traits_scores_list = [candidate]
        # pass on every trait
        for trait, trait_scores in predicted_values_dic.items():
            curr_candidate_traits_scores_list.append(trait_scores[i])
        predicted_traits_list.append(curr_candidate_traits_scores_list)
    predicted_traits_list.insert(0, titles_list)
    np.savetxt(predicted_traits_file, np.array(predicted_traits_list), delimiter=',', fmt='%s')
    return predicted_traits_file


window = Tk()
window.title("Welcome to Cyber Traits app")
window.geometry('1000x400')

enter_path_lbl = Label(window, text="Enter full path to data folder", font=("Arial Bold", 14))
enter_path_lbl.grid(column=0, row=0)

error_path_lbl = Label(window, text="Path not found, Please enter another one", font=("Arial Bold", 12))#, bg='red')

path_txt = Entry(window, width=50)
path_txt.grid(column=1, row=0)

enter_path_btn = Button(window, text="Enter Path", command=folder_path_clicked)
enter_path_btn.grid(column=0, row=1)

organize_predict_data_btn = Button(window, text="Organize and Predict Data", command=organize_predict_clicked)

predicted_done_lbl = Label(window, text='', font=("Arial Bold", 10))
wait_lbl = Label(window, text="Processing, please wait..")
# Progress bar widget
progress = Progressbar(window, orient=HORIZONTAL, length=100, mode='determinate')

window.mainloop()
