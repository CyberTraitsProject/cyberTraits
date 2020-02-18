"""
1. pass on the accelerometer files and take the data for every hour.
2. take the data of every 1 second. if we dont have information on specific time, we need to take the values 0, 0, 0.
3. calculate the MAD. n=60*60=3600

----------------------------------------------------

what we get:
MAD of every hour.

to do an average of every hour in the tested days - 24 values.

"""


import pandas as pd
import os
from date_time import *
import numpy as np

N = 60 * 60 # 60 minutes * 60 seconds


accelerometer_data_dic = {0: [],   1: [],     2: [],     3: [],     4: [],     5: [],
                          6: [],   7: [],     8: [],     9: [],     10: [],    11: [],
                          12: [],  13: [],    14: [],    15: [],    16: [],    17: [],
                          18: [],  19: [],    20: [],    21: [],    22: [],    23: []}



def calc_MAD_avg_for_hour():

    avr_MAD_list = []   # list of MAD averages for every hour in the day, ascending
    accelerometer_titles_list = []

    sorted_hours_keys = sorted(accelerometer_data_dic)
    for hour in sorted_hours_keys:
        if len(accelerometer_data_dic[hour]) == 0:  # for not sending empty array to average function
            avr_MAD_list.append(0)
        else:
            avr_MAD_list.append(np.average(accelerometer_data_dic[hour]))

        accelerometer_titles_list.append('avg_MAD_of_' + str(hour) + "_o'clock")

    #print(avr_MAD_list)
    return accelerometer_titles_list, avr_MAD_list


def get_ri(x_y_z_arr):     # the accelerometer result in time i
    return pow((pow(x_y_z_arr[0], 2) + pow(x_y_z_arr[1], 2) + pow(x_y_z_arr[2], 2)), -2)   # (x^2 + y^2 + z^2)^-2


def calculate_average(x_y_z_list_for_hour):
    ri_arr = [get_ri(x_y_z) for x_y_z in x_y_z_list_for_hour]
    r_avg = 1/N * sum(ri_arr)
    return ri_arr, r_avg


def calculate_MAD(x_y_z_list_for_hour):
    ri_arr, r_avg = calculate_average(x_y_z_list_for_hour)
    dis_arr = [np.abs(ri - r_avg) for ri in ri_arr]
    MAD = 1/N * sum(dis_arr)
    return MAD


def organize_data(path_dir, accelerometer_file):
    """file_date = str(accelerometer_file).split(" ")[0]
    if file_date not in accelerometer_data_dic:
        accelerometer_data_dic[file_date] = []"""

    accelerometer_df = pd.read_csv(os.path.join(path_dir, accelerometer_file), usecols=['UTC time', 'x', 'y', 'z'])

    x_list = accelerometer_df['x']
    y_list = accelerometer_df['y']
    z_list = accelerometer_df['z']
    UTC_times_list = accelerometer_df['UTC time']

    x_y_z_list_for_hour = []    # will contain 60*60 values, that every value is [x,y,z]

    curr_line_index = 0
    curr_date_time = get_date_time_from_UTC_time(UTC_times_list[curr_line_index])
    for i in range(60):
        for j in range(60):
            if (curr_date_time.minute != i or curr_date_time.second != j) or curr_line_index + 1 == len(UTC_times_list):    # the curr time is more or little then the wanted time, or we finished all the lines in the file --> there is a need to fulfill the values with 0,0,0
                continue
            else:
                x_y_z_list_for_hour.append([x_list[curr_line_index], y_list[curr_line_index], z_list[curr_line_index]])
                while curr_date_time.minute == i and curr_date_time.second <= j and curr_line_index + 1 != len(UTC_times_list):
                    curr_line_index += 1
                    curr_date_time = get_date_time_from_UTC_time(UTC_times_list[curr_line_index])
    MAD = calculate_MAD(x_y_z_list_for_hour)
    accelerometer_data_dic[curr_date_time.hour].append(MAD)


def accelerometer_main(accelerometer_dir):

    # for cleaning the previous data
    global accelerometer_data_dic
    accelerometer_data_dic = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [],
                              6: [], 7: [], 8: [], 9: [], 10: [], 11: [],
                              12: [], 13: [], 14: [], 15: [], 16: [], 17: [],
                              18: [], 19: [], 20: [], 21: [], 22: [], 23: []}

    if not os.path.isdir(accelerometer_dir):
        print("Directory", accelerometer_dir, "not exists")
        return calc_MAD_avg_for_hour()
    for curr_accelerometer_file in os.listdir(accelerometer_dir):
        organize_data(accelerometer_dir, curr_accelerometer_file)
    return calc_MAD_avg_for_hour()
