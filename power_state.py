"""
define 4 macro- 1. Screen turned on
				2. Screen turned off
				3. Device Idle (Doze) state change signal received; device not in idle state
				4. Device Idle (Doze) state change signal received; device in idle state

1. pass on the power_state files and take the data for every day from the hours 9:00-18:00.
2. takes two things:    2.1. count how much times the phone was on "Screen turned on" state.
						2.2. summarize how much time the phone was in "Screen turned on" state.

1. pass on the power_state files and take the data for every day from the hours 18:00-00:00.
2. takes two things:    2.1. count how much times the phone was on "Screen turned on" state.
						2.2. summarize how much time the phone was in "Screen turned on" state.

1. pass on the power_state files and take the data for every day from the hours 00:00-9:00.
2. takes two things:    2.1. count how much times the phone was on "Screen turned on" state.
						2.2. summarize how much time the phone was in "Screen turned on" state.

-----------------------------------------------------------------------------------------

to calculate    1. the average of the number of times the phone wan on "Screen turned on" state, for day, evening and night - 3 values.
				2. the SD of the number of times the phone wan on "Screen turned on" state, for day, evening and night - 3 values.
				3. the average of the time the phone wan on "Screen turned on" state, for day, evening and night - 3 values.
				4. the SD of the time the phone wan on "Screen turned on" state, for day, evening and night - 3 values.
"""

import pandas as pd
import os
from date_time import *
import numpy as np


check_variables = ['num_times', 'sum_time']

power_states_data_dic = {}


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


def update_durations_in_power_states_data_dic(start_date_time, durations_list):
    part_of_day = get_part_of_day(start_date_time)
    cur_date = str(start_date_time.date())
    i = 0
    while i < len(durations_list):
        power_states_data_dic[cur_date][part_of_day]['num_times'] += 1
        power_states_data_dic[cur_date][part_of_day]['sum_time'] += durations_list[i]
        #print(durations_list[i])
        part_of_day = get_next_day_time(start_date_time)
        if part_of_day == 'night':
            start_date_time += datetime.timedelta(days=1)
            cur_date = str(start_date_time.date())
        i += 1


def calc_avr_and_sd_on_dic():

    array_list = [[[],[]], [[],[]], [[],[]]]  # [[[night_num_times],[night_sum_times]], [[day_num_times],[day_sum_times]], [[[evening_num_times],[evening_sum_times]]]]
    avr_and_sd_list = []
    power_state_titles_list = []

    for date in power_states_data_dic:
        for i, day_time in enumerate(day_times):	# pass on night, day & evening
            for j, check_variable in enumerate(check_variables):	# pass on num_times & sum_times
                array_list[i][j].append(power_states_data_dic[date][day_time][check_variable])

    for i, day_time in enumerate(day_times):
        for j, check_variable in enumerate(check_variables):	# pass on num_times & sum_times
            avr_and_sd_list.append(np.array(array_list[i][j]).mean())
            power_state_titles_list.append('power_state_' + day_time + '_' + check_variable + '_avg')

            avr_and_sd_list.append(np.array(array_list[i][j]).std())
            power_state_titles_list.append('power_state_' + day_time + '_' + check_variable + '_std')

    #print(array_list)
    return power_state_titles_list, avr_and_sd_list


def organize_data(path_dir, power_state_file, last_on_power_state_date):
    file_date = str(power_state_file).split(" ")[0]
    if file_date not in power_states_data_dic:
        power_states_data_dic[file_date] = {'night':    {'num_times': 0, 'sum_time': 0},
                                            'day':      {'num_times': 0, 'sum_time': 0},
                                        'evening':  {'num_times': 0, 'sum_time': 0}}

    power_states_df = pd.read_csv(os.path.join(path_dir, power_state_file), usecols=['UTC time', 'event'])

    power_states_list = power_states_df['event']
    UTC_times_list = power_states_df['UTC time']

    for i, power_state in enumerate(power_states_list):
        if power_state == ON and last_on_power_state_date:  # error date from the app
            last_on_power_state_date = None
            continue
        elif power_state == OFF and last_on_power_state_date:
            on_time = get_date_time_from_UTC_time(last_on_power_state_date)
            off_time = get_date_time_from_UTC_time(UTC_times_list[i])
            last_on_power_state_date = None
        elif power_state == ON:
            on_time = get_date_time_from_UTC_time(UTC_times_list[i])
            if i + 1 < len(power_states_list):
                off_time = get_date_time_from_UTC_time(UTC_times_list[i+1])
            else:    # reached to the EOF
                last_on_power_state_date = UTC_times_list[i]
                return last_on_power_state_date
        else:
            continue
        durations_list = get_list_of_power_on_durations(on_time, off_time)
        update_durations_in_power_states_data_dic(on_time, durations_list)
    return None


def power_state_main(power_state_dir):
    if not os.path.isdir(power_state_dir):
        print("Directory '", power_state_dir, "' not exists")
        exit(1)
    returned_value = None
    for curr_power_state_file in os.listdir(power_state_dir):
        last_on_power_state_date = organize_data(power_state_dir, curr_power_state_file, returned_value)
        returned_value = last_on_power_state_date
    return calc_avr_and_sd_on_dic()




"""lines = open("C:/Users/yafitsn/Downloads/data/1q9fj13m/power_state/1/sum.csv", "r").readlines()
sum = 0
for i,line in enumerate(lines):
    if i == 22:
        break
    if i%2 == 0:
        on_time = datetime.datetime.strptime(line.split("S")[0], '%Y-%m-%dT%H:%M:%S.%f')
    else:
        off_time = datetime.datetime.strptime(line.split("S")[0], '%Y-%m-%dT%H:%M:%S.%f')
        sum += (off_time - on_time).total_seconds() / 60
print(sum)"""
