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


accelerometer_data_dic = {}

avr_and_sd_dic = {'night':      {'num_times': {'average': 0, 'sd': 0}, 'sum_time': {'average': 0, 'sd': 0}},
                  'day':        {'num_times': {'average': 0, 'sd': 0}, 'sum_time': {'average': 0, 'sd': 0}},
                  'evening':    {'num_times': {'average': 0, 'sd': 0}, 'sum_time': {'average': 0, 'sd': 0}}}


def get_list_of_power_on_durations(on_time, off_time):
    durations_list = []
    while get_part_of_day(on_time) != get_part_of_day(off_time) or on_time.date() != off_time.date():   # the on and the off time are in different dates or in different parts of days
        next_time = get_next_part_of_day_start_time(on_time)
        next_on_date_time = get_next_date_for_next_time(on_time, next_time)
        duration = (next_on_date_time - on_time).total_seconds() / 60
        durations_list.append(duration)
        on_time = next_on_date_time
    duration = (off_time - on_time).total_seconds() / 60
    durations_list.append(duration)
    return durations_list


def update_durations_in_accelerometer_data_dic(start_date_time, durations_list):
    part_of_day = get_part_of_day(start_date_time)
    cur_date = str(start_date_time.date())
    i = 0
    while i < len(durations_list):
        accelerometer_data_dic[cur_date][part_of_day]['num_times'] += 1
        accelerometer_data_dic[cur_date][part_of_day]['sum_time'] += durations_list[i]
        part_of_day = get_next_day_time(start_date_time)
        if part_of_day == 'night':
            start_date_time += datetime.timedelta(days=1)
            cur_date = str(start_date_time.date())
        i += 1


def calc_avr_and_sd_on_dic():
    array_list = [[[],[]], [[],[]], [[],[]]]  # [[[night_num_times],[night_sum_times]], [[day_num_times],[day_sum_times]], [[[evening_num_times],[evening_sum_times]]]]
    for date in accelerometer_data_dic:
        array_list[0][0].append(accelerometer_data_dic[date]['night']['num_times'])
        array_list[0][1].append(accelerometer_data_dic[date]['night']['sum_time'])
        array_list[1][0].append(accelerometer_data_dic[date]['day']['num_times'])
        array_list[1][1].append(accelerometer_data_dic[date]['day']['sum_time'])
        array_list[2][0].append(accelerometer_data_dic[date]['evening']['num_times'])
        array_list[2][1].append(accelerometer_data_dic[date]['evening']['sum_time'])
    avr_and_sd_dic['night']['num_times']['average']     = np.array(array_list[0][0]).mean()
    avr_and_sd_dic['night']['sum_time']['average']      = np.array(array_list[0][1]).mean()
    avr_and_sd_dic['night']['num_times']['sd']          = np.array(array_list[0][0]).std()
    avr_and_sd_dic['night']['sum_time']['sd']           = np.array(array_list[0][1]).std()
    avr_and_sd_dic['day']['num_times']['average']       = np.array(array_list[1][0]).mean()
    avr_and_sd_dic['day']['sum_time']['average']        = np.array(array_list[1][1]).mean()
    avr_and_sd_dic['day']['num_times']['sd']            = np.array(array_list[1][0]).std()
    avr_and_sd_dic['day']['sum_time']['sd']             = np.array(array_list[1][1]).std()
    avr_and_sd_dic['evening']['num_times']['average']   = np.array(array_list[2][0]).mean()
    avr_and_sd_dic['evening']['sum_time']['average']    = np.array(array_list[2][1]).mean()
    avr_and_sd_dic['evening']['num_times']['sd']        = np.array(array_list[2][0]).std()
    avr_and_sd_dic['evening']['sum_time']['sd']         = np.array(array_list[2][1]).std()

    print(array_list)
    print(avr_and_sd_dic)


def organize_data(path_dir, accelerometer_file, last_on_accelerometer_date):
    file_date = str(accelerometer_file).split(" ")[0]
    if file_date not in accelerometer_data_dic:
        accelerometer_data_dic[file_date] = []

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
            if curr_date_time.minute != i or curr_date_time.second != j:
                x_y_z_list_for_hour.append([0, 0, 0])
                if curr_date_time.minute > i or (curr_date_time.minute == i and curr_date_time.second > j):     # the wanted time is less then the current UTC_time TODO: if the file finished
                    continue
            else:
                x_y_z_list_for_hour.append([x_list[curr_line_index], y_list[curr_line_index], z_list[curr_line_index]])
            curr_line_index += 1

    """for i, accelerometer in enumerate(accelerometer_list):
        if accelerometer == OFF and last_on_accelerometer_date:
            on_time = get_date_time_from_UTC_time(last_on_accelerometer_date)
            off_time = get_date_time_from_UTC_time(UTC_times_list[i])
            last_on_accelerometer_date = None
        elif accelerometer == ON:
            on_time = get_date_time_from_UTC_time(UTC_times_list[i])
            if i + 1 < len(accelerometer_list):
                off_time = get_date_time_from_UTC_time(UTC_times_list[i+1])
            else:    # reached to the EOF
                last_on_accelerometer_date = UTC_times_list[i]
                return last_on_accelerometer_date
        else:
            continue
        durations_list = get_list_of_power_on_durations(on_time, off_time)
        update_durations_in_accelerometer_data_dic(on_time, durations_list)
    return None"""


def accelerometer_main(accelerometer_dir):
    if not os.path.isdir(accelerometer_dir):
        print("Directory", accelerometer_dir, "not exists")
        exit(1)
    for curr_accelerometer_file in os.listdir(accelerometer_dir):
        organize_data(accelerometer_dir, curr_accelerometer_file)
    calc_avr_and_sd_on_dic()
    print(accelerometer_data_dic)


if __name__ == "__main__":
    accelerometer_main("C:/Users/yafitsn/PycharmProjects/Project/data/1q9fj13m/accelerometer")
