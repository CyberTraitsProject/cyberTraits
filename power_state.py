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
import csv, os
from enum import Enum
from pathlib import Path
import datetime
"""if __name__ == "__main__":
    dir = Path.argv[0]"""

#class DAY_TIMES(Enum):
START_DAY = "09:00:00"      # calculate by UTC. TODO - to match it to the real time in Israel - 09:00
START_EVENING = "18:00:00"  # calculate by UTC. TODO - to match it to the real time in Israel - 16:00
START_NIGHT = "00:00:00"    # calculate by UTC. TODO - to match it to the real time in Israel - 22:00

#class POWER_STATE(Enum):
ON = "Screen turned on"
OFF = "Screen turned off"
DOZE_NOT_IN_IDLE = "Device Idle (Doze) state change signal received; device not in idle state"
DOZE_IN_IDLE = "Device Idle (Doze) state change signal received; device in idle state"

POWER_STATE_DATE_COLUMN = 1
POWER_STATE_NAME_COLUMN = 2


power_states_data_dic = {}
#last_on_power_state_date = ""

def get_part_of_day(date_time):
    if START_NIGHT <= date_time.split("T")[1] < START_DAY:      # night time
        return 'night'
    elif START_DAY <= date_time.split("T")[1] < START_EVENING:  # day time
        return 'day'
    else:                                                       # evening time
        return 'evening'


def organize_data(path_dir, power_state_file, last_on_power_state_date):
    file_date = str(power_state_file).split(" ")[0]
    if file_date not in power_states_data_dic:
        power_states_data_dic[file_date] = {'day':      {'num_times': 0, 'sum_time': 0},
                                            'evening':  {'num_times': 0, 'sum_time': 0},
                                            'night':    {'num_times': 0, 'sum_time': 0}}
    power_state_f = open(os.path.join(path_dir, power_state_file), "r")
    power_state_f.readline()
    row_count = sum(1 for line in power_state_f) + 1
    print(row_count)
    power_state_f = open(os.path.join(path_dir, power_state_file), "r")
    for i, row in enumerate(power_state_f):
        if OFF in row.split(",")[POWER_STATE_NAME_COLUMN] and last_on_power_state_date:
            on_time = datetime.datetime.strptime(last_on_power_state_date, '%Y-%m-%dT%H:%M:%S.%f')
            off_time = datetime.datetime.strptime(row.split(",")[POWER_STATE_DATE_COLUMN], '%Y-%m-%dT%H:%M:%S.%f')
            difference_time = off_time - on_time
            difference_time_in_minutes = difference_time.total_seconds() / 60
            prev_file_date = last_on_power_state_date.split("T")[0]
            prev_part_of_day = get_part_of_day(last_on_power_state_date)
            power_states_data_dic[prev_file_date][prev_part_of_day]['num_times'] += 1
            power_states_data_dic[prev_file_date][prev_part_of_day]['sum_time'] += difference_time_in_minutes

        if ON in row.split(",")[POWER_STATE_NAME_COLUMN]:
            on_time = datetime.datetime.strptime(row.split(",")[POWER_STATE_DATE_COLUMN], '%Y-%m-%dT%H:%M:%S.%f')
            if i+1 < row_count:
                next_row = power_state_f.readline()
                off_time = datetime.datetime.strptime(next_row.split(",")[POWER_STATE_DATE_COLUMN], '%Y-%m-%dT%H:%M:%S.%f')
                difference_time = off_time - on_time
                difference_time_in_minutes = difference_time.total_seconds() / 60
            else:    # reached to the EOF
                return row.split(",")[POWER_STATE_DATE_COLUMN]
            part_of_day = get_part_of_day(row.split(",")[POWER_STATE_DATE_COLUMN])
            power_states_data_dic[file_date][part_of_day]['num_times'] += 1
            power_states_data_dic[file_date][part_of_day]['sum_time'] += difference_time_in_minutes

def power_state_main(power_state_dir):

    if not os.path.isdir(power_state_dir):
        print("Directory not exists")
        exit(1)
    returned_value = None
    for curr_power_state_file in os.listdir(power_state_dir):
        last_on_power_state_date = organize_data(power_state_dir, curr_power_state_file, returned_value)
        returned_value = last_on_power_state_date
    print(power_states_data_dic)

power_state_main("C:/Users/yafitsn/Downloads/data/1q9fj13m/power_state/o")

