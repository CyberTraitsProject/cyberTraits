
import pandas as pd
import os
from date_time import *
import numpy as np

avr_and_sd_dic = {'night':      {'average': 0, 'sd': 0},
                  'day':        {'average': 0, 'sd': 0},
                  'evening':    {'average': 0, 'sd': 0}}


def calc_avr_and_sd_on_dic(data_dic):
    array_list = [[], [], []]  # [[night_num_times], [day_num_times], [evening_num_times]]
    for date in data_dic:
        array_list[0].append(len(data_dic[date]['night']))
        array_list[1].append(len(data_dic[date]['day']))
        array_list[2].append(len(data_dic[date]['evening']))
    avr_and_sd_dic['night']['average']     = np.array(array_list[0]).mean()
    avr_and_sd_dic['night']['sd']          = np.array(array_list[0]).std()
    avr_and_sd_dic['day']['average']       = np.array(array_list[1]).mean()
    avr_and_sd_dic['day']['sd']            = np.array(array_list[1]).std()
    avr_and_sd_dic['evening']['average']   = np.array(array_list[2]).mean()
    avr_and_sd_dic['evening']['sd']        = np.array(array_list[2]).std()

    print(array_list)
    print(avr_and_sd_dic)


def organize_data(path_dir, wifi_file, data_dic):
    file_date = str(wifi_file).split(" ")[0]
    wifi_df = pd.read_csv(os.path.join(path_dir, wifi_file), usecols=['hashed MAC'])
    hashed_MAC_list_unique = wifi_df['hashed MAC'].unique()
    part_of_day = get_part_of_day(get_date_time_from_file_name(wifi_file.replace(".csv", "")))
    if file_date not in data_dic:
        data_dic[file_date] = {    'night':    np.array([]),
                                        'day':      np.array([]),
                                        'evening':  np.array([])}
    all_hashed_MAC = np.append(data_dic[file_date][part_of_day], hashed_MAC_list_unique)
    data_dic[file_date][part_of_day] = np.unique(all_hashed_MAC)
