
import pandas as pd
import os
from date_time import *
import numpy as np




def calc_avr_and_sd_on_dic(data_dic, data_type):
    array_list = [[], [], []]  # [[night_num_times], [day_num_times], [evening_num_times]]
    avr_and_sd_list = []
    titles_list = []
    for date in data_dic:
        for i, day_time in enumerate(day_times):
            array_list[i].append(len(data_dic[date][day_time]))

    for i, day_time in enumerate(day_times):
        avr_and_sd_list.append(np.array(array_list[i]).mean())
        titles_list.append(data_type + '_' + day_time + '_avg')

        avr_and_sd_list.append(np.array(array_list[i]).std())
        titles_list.append(data_type + '_' + day_time + '_std')

    #print(array_list)
    #print(avr_and_sd_dic)
    return titles_list, avr_and_sd_list


def organize_data(path_dir, wifi_file, data_dic):
    file_date = str(wifi_file).split(" ")[0]
    wifi_df = pd.read_csv(os.path.join(path_dir, wifi_file), usecols=['hashed MAC'])
    hashed_MAC_list_unique = wifi_df['hashed MAC'].unique()
    part_of_day = get_part_of_day(get_date_time_from_file_name(wifi_file.replace(".csv", "")))
    if file_date not in data_dic:
        data_dic[file_date] = {'night':    np.array([]),
                               'day':      np.array([]),
                               'evening':  np.array([])}
    all_hashed_MAC = np.append(data_dic[file_date][part_of_day], hashed_MAC_list_unique)
    data_dic[file_date][part_of_day] = np.unique(all_hashed_MAC)
