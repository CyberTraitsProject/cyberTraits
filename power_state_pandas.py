import pandas as pd
import os, datetime

#class DAY_TIMES(Enum):
START_DAY = datetime.datetime(1, 1, 1, 9, 0, 0, 0)          # calculate by UTC. TODO - to match it to the real time in Israel - 09:00
START_EVENING = datetime.datetime(1, 1, 1, 18, 0, 0, 0)     # calculate by UTC. TODO - to match it to the real time in Israel - 16:00
START_NIGHT = datetime.datetime(1, 1, 1, 0, 0, 0, 0)        # calculate by UTC. TODO - to match it to the real time in Israel - 22:00

#class POWER_STATE(Enum):
ON = "Screen turned on"
OFF = "Screen turned off"
DOZE_NOT_IN_IDLE = "Device Idle (Doze) state change signal received; device not in idle state"
DOZE_IN_IDLE = "Device Idle (Doze) state change signal received; device in idle state"

POWER_STATE_DATE_COLUMN = 1
POWER_STATE_NAME_COLUMN = 2

power_states_data_dic = {}


def get_date_time_from_str(str):
    return datetime.datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%f')

def get_part_of_day(date_time):
    if START_NIGHT.time() <= date_time.time() < START_DAY.time():      # night time
        return 'night'
    elif START_DAY.time() <= date_time.time() < START_EVENING.time():  # day time
        return 'day'
    else:                                                       # evening time
        return 'evening'


def get_next_day_time(date_time):
    if get_part_of_day(date_time) == 'day':         # night time
        return 'evening'
    elif get_part_of_day(date_time) == 'evening':   # day time
        return 'night'
    else:                                           # evening time
        return 'morning'


def get_next_part_of_day_start_time(date_time):
    if get_next_day_time(date_time) == 'day':
        return START_DAY.time()
    elif get_next_day_time(date_time) == 'evening':
        return START_EVENING.time()
    else:
        return START_NIGHT.time()


def get_next_date(date_time, next_time):
    if next_time.hour == 0:     # passing between 2 days
        date_time += datetime.timedelta(days=1)
    new_date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, next_time.hour, next_time.minute, next_time.second, next_time.microsecond)
    return new_date_time


def get_list_of_power_on_durations(on_time, off_time):
    durations_list = []
    while get_part_of_day(on_time) != get_part_of_day(off_time) or on_time.date() != off_time.date():   # the on and the off time are in different dates or in different parts of days
        next_time = get_next_part_of_day_start_time(on_time)
        next_on_date_time = get_next_date(on_time, next_time)
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
        part_of_day = get_next_day_time(start_date_time)
        if part_of_day == 'night':
            start_date_time += datetime.timedelta(days=1)
            cur_date = str(start_date_time.date())
        i += 1


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
        if power_state == OFF and last_on_power_state_date:
            on_time = get_date_time_from_str(last_on_power_state_date)
            off_time = get_date_time_from_str(UTC_times_list[i])
            last_on_power_state_date = None
        elif power_state == ON:
            on_time = get_date_time_from_str(UTC_times_list[i])
            if i + 1 < len(power_states_list):
                off_time = get_date_time_from_str(UTC_times_list[i+1])
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
        print("Directory not exists")
        exit(1)
    returned_value = None
    for curr_power_state_file in os.listdir(power_state_dir):
        last_on_power_state_date = organize_data(power_state_dir, curr_power_state_file, returned_value)
        returned_value = last_on_power_state_date

    print(power_states_data_dic)


if __name__ == "__main__":
    power_state_main("C:/Users/yafitsn/PycharmProjects/Project/data/1q9fj13m/power_state")
















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
