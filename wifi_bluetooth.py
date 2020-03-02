import pandas as pd
import os
from date_time import *
# import numpy as np


'''def calc_avr_and_sd_on_dic(data_dic, data_type):
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

    return titles_list, avr_and_sd_list'''


def organize_data(path_dir, sensor_file, sensor_data):
    sensor_df = pd.read_csv(os.path.join(path_dir, sensor_file), usecols=['hashed MAC'])
    hashed_MAC_list_unique = sensor_df['hashed MAC'].unique()
    # part_of_day = get_part_of_day(get_date_time_from_file_name(sensor_file.replace(".csv", "")))
    '''if file_date not in sensor_data.data_dic:
        sensor_data.data_dic[file_date] = {day_times[NIGHT]:    np.array([]),
                               day_times[DAY]:      np.array([]),
                               day_times[EVENING]:  np.array([])}'''
    date = get_date_from_file_name(sensor_file)
    hour = get_date_time_from_file_name(sensor_file).hour
    # sensor_data.data_dic[hour].append(hashed_MAC_list_unique)
    if date not in sensor_data.data_dic:
        sensor_data.data_dic[date] = {}
    sensor_data.data_dic[date][hour] = hashed_MAC_list_unique
    '''all_hashed_MAC = np.append(sensor_data.data_dic[file_date][hour], hashed_MAC_list_unique)
    sensor_data.data_dic[hour] = np.unique(all_hashed_MAC)'''

