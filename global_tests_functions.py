import os
import pandas as pd
import numpy as np
from collections import Counter
import math
from math import pow
from date_time import *


def count_num_dates(sensor_dir):
    """
    run on every file, and count the number of the files that have different dates.
    :param sensor_dir: the folder the sensor data found there
    :return: the num of the dates we have files data on it
    """
    dates_list = []
    for curr_sensor_file in os.listdir(sensor_dir):
        date = curr_sensor_file.split(" ")[0]
        if date not in dates_list:
            dates_list.append(date)
    return len(dates_list)


def count_num_hours(sensor_dir):
    """
    count the number of the files.
    (every file has data on one hour)
    :param sensor_dir: the folder the sensor data found there
    :return: the num of the hours we have files data on it
    """
    return len(os.listdir(sensor_dir))


def combine_all_files_to_one_file(sensor_dir):
    """
    run on all of the files, and combined them to one file.
    :param sensor_dir: the folder the sensor data found there
    :return: the combined file
    """
    extension = 'csv'
    all_filenames = os.listdir(sensor_dir)
    # combine all files in the list
    combined_csv = pd.concat([pd.read_csv(os.path.join(sensor_dir, f)) for f in all_filenames])
    # the name of the sensor
    sensor_name = sensor_dir.split('\\')[-1]
    # export to csv
    combined_csv.to_csv(f'combined_{sensor_name}_csv.csv', index=False, encoding='utf-8-sig')
    return f'combined_{sensor_name}_csv.csv'


def count_num_data(sensor_data, kind_index):
    """
    run on every date and hour data and summarize the specific kind.
    :param sensor_data: the data of the sensor (from the code, not from the test)
    :param kind_index: the index we wants to take the data from
    :return: sum the kind of the data
    """
    count = 0
    for date, hours_data in sensor_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            count += hour_data[kind_index]
    return count


def count_num_strings_in_file(file, string, col_name):
    """
    count how many times the string found in the col in this file
    :param file: the file to read the data from (the test combined file)
    :param string: to string to search
    :param col_name:the name of the column
    :return: the num times the string found in the col in this file
    """
    sensor_df = pd.read_csv(file, usecols=[col_name])
    return (sensor_df[col_name] == string).sum()


def round_list(list_of_lists):
    """
    run on every list in the list, and round it.
    :param list_of_lists: list of [x,y,z] values
    :return: the round list
    """
    n_list_of_lists = []
    for c_list in list_of_lists:
        n_list_of_lists.append(list(np.around(np.array(c_list), 4)))
    return n_list_of_lists


def add_zeros_to_list(sensor_data_list):
    while len(sensor_data_list) != NUM_TESTED_DATES:
        sensor_data_list.append(0)
    return sensor_data_list


def do_avg_on_list(sensor_data_list):
    sensor_data_list = add_zeros_to_list(sensor_data_list)
    return np.average(np.array(sensor_data_list))


def do_std_on_list(sensor_data_list):
    sensor_data_list = add_zeros_to_list(sensor_data_list)
    return np.std(np.array(sensor_data_list))


def do_median_on_list(sensor_data_list):
    if not len(sensor_data_list):
        return 0
    return np.median(np.array(sensor_data_list))


def do_common_on_list(sensor_data_list):
    return np.bincount(np.array(sensor_data_list)).argmax()#Counter(sensor_data_list).most_common(1)[0][0]


def get_day_time_index(cur_hour, day_times):
    for i, c_day_time in enumerate(day_times):
        if int(cur_hour) in day_times[c_day_time]:
            return i


def get_key_from_hour(hour, day_times):
    for key, hours_list in day_times.items():
        if hour in hours_list:
            return key


def do_S_on_dic(phones_durations_dic, num_hours_in_dt):
    sum_time_in_sec = num_hours_in_dt * 60 * 60 # =T
    # calculate the Fi list
    Fi_list = []
    for phone_number, duration_time in phones_durations_dic.items():
        Fi_list.append(duration_time / sum_time_in_sec)
    S = 0
    for Fi in Fi_list:
        S += Fi * math.log10(Fi)
    return -1 * S


def do_MAD_on_xyz_lists(xyz_lists, num_hours_in_dt):
    ri_list = []
    for xyz in xyz_lists:
        ri_list.append(pow(pow(xyz[0], 2) + pow(xyz[1], 2) + pow(xyz[2], 2), -2))
    avg_r = sum(ri_list) / (num_hours_in_dt * 60 * 60)
    abs_list = []
    for ri in ri_list:
        abs_list.append(abs(ri - avg_r))
    MAD = sum(abs_list) / (num_hours_in_dt * 60 * 60)
    return MAD


def convert_nan_to_0(np_arr):
    for i, value in enumerate(np_arr):
        if np.isnan(value):
            np_arr[i] = 0
    return np_arr


sensor_candidate_dir = ''
