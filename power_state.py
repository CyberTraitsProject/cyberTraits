import pandas as pd
from date_time import *
from sensor_data import *

# the indexes of the kinds of the data
NUM_TIMES = 0
SUM_TIME = 1
SHORT_ON_TIME = 2

# the common time the phone is on
COMMON_ON_TIME = 5

# the max time it makes sense the phone is on
MAX_ON_TIME = 3

OFF_LIST = [OFF, SHUTDOWN]


def get_list_of_power_on_durations(on_time, off_time):
    """
    calculate the duration time of every hour the phone was on in it.
    e.g. the phone was on at "12/12/12 10:54:45" and off at "12/12/12 11:37:00",
    so, the list will contain two values: [5.25, 37].
    :param on_time: the time the event on was happened
    :param off_time: the time the event off was happened
    :return: the list of the durations times. if the on and off happened in the same hour and date,
             it will return list with one value.
    """

    # if the duration time is 3 hours or more -->
    # that says there is a bug in the data -->
    # we will send an array with single value 0
    # this time will add to the num_times, but will not add to the sum_times(it will be 0).
    if (off_time - on_time) >= datetime.timedelta(hours=MAX_ON_TIME):
        return [0]

    # the list of the durations
    durations_list = []

    # the on and the off time are in different dates or in different hours
    while on_time.hour != off_time.hour or on_time.date() != off_time.date():
        # the next hour date time
        next_on_date_time = on_time + datetime.timedelta(hours=1)
        # the next whole hour date time
        next_on_date_time = next_on_date_time.replace(microsecond=0, second=0, minute=0)
        duration = (next_on_date_time - on_time).total_seconds() / 60
        durations_list.append(duration)
        on_time = next_on_date_time

    # the on and the off dates and hours are the same -> calculate the durations (in minutes)
    duration = (off_time - on_time).total_seconds() / 60
    durations_list.append(duration)

    return durations_list


def update_durations_in_power_states_data_dic(start_date_time, durations_list, power_state_data_dic):
    """
    pass on every hour, from the hour of the date the phone was on, and update the durations.
    e.g. the start_date_time = "12/12/12 10:54:45", and durations_list = [5.25, 37],
    so it will update the dic:
    power_state_data_dic[12/12/12][10][sum_times] += 5.25, power_state_data_dic[12/12/12][11][sum_times] += 37.
    and also, will add only the hour of the date of the on event, to the num_times += 1.
    :param start_date_time: the date time the phone was on
    :param durations_list: contains data on every hour, how much time the power state was on
    :param power_state_data_dic: the data dic, to update the durations
    """

    # durations_list contains a list of every hour, how much time the power state was on
    cur_date = str(start_date_time.date())

    # pass on every duration
    for i in range(len(durations_list)):

        # if the current hour not found in the current date -> initialize it
        if start_date_time.hour not in power_state_data_dic[cur_date]:
            power_state_data_dic[cur_date][start_date_time.hour] = [0, 0, 0]  # = [num_times, sum_time, num_short_time]

        # update the num_times only for the first hour
        if i == 0:
            power_state_data_dic[cur_date][start_date_time.hour][NUM_TIMES] += 1

        # add the duration to the duration on this hour
        power_state_data_dic[cur_date][start_date_time.hour][SUM_TIME] += durations_list[i]

        # the next hour
        start_date_time += datetime.timedelta(hours=1)

        # the next date time
        cur_date = str(start_date_time.date())


def update_short_duration(on_time, off_time, power_state_data_dic):
    """
    update the short duration time in the dic, if the phone was on for time that short from AVG_ON_TIME.
    :param on_time: the time the event on was happened
    :param off_time: the time the event off was happened
    :param power_state_data_dic: the data dic
    """

    cur_date = str(on_time.date())
    # calculate if the duration was little than AVG_ON_TIME
    if (off_time - on_time) < datetime.timedelta(seconds=COMMON_ON_TIME):
        power_state_data_dic[cur_date][on_time.hour][SHORT_ON_TIME] += 1


def organize_data(path_dir, power_state_file, power_state_data, last_on_power_state_date):
    """
    pass on the sensor_file - this file contains texts data on specific date on specific hour.
    the name of the file is the date and the hour.
    the file contains data in this shape: [timestamp, UTC time, event]
    the function add its data to the sensor dictionary-
    count how much outgoing calls, incoming calls, missed calls, outgoing calls with duration 0,
    duration time list, duration time he talked with each phone number - there are in this hour.
    :param path_dir: the path to the directory the sensor data found there
    :param power_state_file: the name of the file to organize
    :param power_state_data: the global sensor data dictionary
    :param last_on_power_state_date: the date of the last line, that the phone was on in it. if not found -> None.
    """

    full_path_texts_file = os.path.join(path_dir, power_state_file)
    check_if_file_exists(full_path_texts_file)

    power_states_df = pd.read_csv(full_path_texts_file, usecols=['UTC time', 'event'])
    power_states_list = power_states_df['event']
    UTC_times_list = power_states_df['UTC time']
    date = get_date_from_file_name(power_state_file)

    # if it is a new date -> add it to the dictionary
    if date not in power_state_data.data_dic:
        power_state_data.data_dic[date] = {}

    # pass on every power state event
    # there are 4 types, we are using only two of them - on, off
    for i, power_state in enumerate(power_states_list):

        # on after on - error date from the app
        if power_state == ON and last_on_power_state_date:
            # calculate the last_on_power_state_date as on time with duration 0
            on_time = last_on_power_state_date
            off_time = on_time
            durations_list = get_list_of_power_on_durations(on_time, off_time)
            # update the hour's durations in the data dic
            update_durations_in_power_states_data_dic(on_time, durations_list, power_state_data.data_dic)
            # update the number of the short duration times
            update_short_duration(on_time, off_time, power_state_data.data_dic)
            last_on_power_state_date = get_date_time_from_UTC_time(UTC_times_list[i])
            continue

        # the current event is off, and there was on event in the last time
        elif power_state in OFF_LIST and last_on_power_state_date:
            on_time = last_on_power_state_date
            off_time = get_date_time_from_UTC_time(UTC_times_list[i])
            # we handle the last power state --> None
            last_on_power_state_date = None

        # the current power state is on
        elif power_state == ON:
            last_on_power_state_date = get_date_time_from_UTC_time(UTC_times_list[i])
            continue

        # another power states never mind
        else:
            continue

        # send the on and the off time, to get the list of the durations.
        # (if the on and the off are not in the same hour, there is a need to divide it each duration to each hour)
        durations_list = get_list_of_power_on_durations(on_time, off_time)

        # update the hour's durations in the data dic
        update_durations_in_power_states_data_dic(on_time, durations_list, power_state_data.data_dic)

        # update the number of the short duration times
        update_short_duration(on_time, off_time, power_state_data.data_dic)

    # the file doest finish with on power state --> return None
    return last_on_power_state_date


def power_state_main(power_state_dir):
    """
    create an instance of Sensor_Data, pass on all of the power state data file,
    organize them and do the calculations of this data.
    :param power_state_dir: the directory that the power states data files found there
    :return: the calculated data in 2 lists - the calculated data and its titles
    """

    power_state_data = Sensor_Data('power_state')

    check_if_dir_exists(power_state_dir)

    # the date of the last time the phone was on, and it didnt handle
    returned_value = None

    # pass on every file and send it to the organize_data function
    for curr_power_state_file in os.listdir(power_state_dir):
        last_on_power_state_date = organize_data(power_state_dir, curr_power_state_file,
                                                 power_state_data, returned_value)
        returned_value = last_on_power_state_date

    # handle the last on time in the last file
    if returned_value:
        on_time = returned_value
        # the end of this hour
        off_time = on_time.replace(microsecond=999999, second=59, minute=59)
        durations_list = get_list_of_power_on_durations(on_time, off_time)
        update_durations_in_power_states_data_dic(on_time, durations_list, power_state_data.data_dic)
        update_short_duration(on_time, off_time, power_state_data.data_dic)

    # send the data to the calculation function, and return the calculated data + its titles
    # num_times=2, because the data contains two inputs that we need to calculate
    # avg, std on them - num on power state and sum on power state
    return power_state_data.calc_calculations_on_dic(day_times, num_times=2)


if __name__ == '__main__':
    power_state_main(r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data\ygpxrisr\power_state')
