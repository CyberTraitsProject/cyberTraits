import numpy as np
import collections
import math
from useful_functions import *
from date_time import check_day_time_structure

# num seconds in a hour
N = 60 * 60

# lists indexes of the sensors data
IN = NUM_TIMES = 0
OUT = SUM_TIMES = 1
MISSED = SHORT_ON_TIME = 2
OUT_0 = 3
DURATION_MEDIAN = 4
PHONE_NUMBERS_DURATIONS = 5

# macros for calls sensor
NUM_MIN_IN_HOUR = 60
NUM_SEC_IN_MIN = 60


def get_ri(x_y_z_arr):
    """
    the accelerometer result in time i.
    :param x_y_z_arr: x, y, z values
    :return: (x^2 + y^2 + z^2)^-2
    """
    return pow((pow(x_y_z_arr[0], 2) + pow(x_y_z_arr[1], 2) + pow(x_y_z_arr[2], 2)), -2)


def calculate_average(x_y_z_list, num_hours):
    """
    calculate the average of the ri.
    the ri list contains only the [x,y,z]!=[0,0,0],
    so the average will divide by N * num_hours, and not by the length og the ri list.
    :param x_y_z_list: list of lists of x, y, z values
    :param num_hours: on how much hours we are calculating the average
    :return: the ri array, and the average
    """
    ri_arr = [get_ri(x_y_z) for x_y_z in x_y_z_list]
    r_avg = (1 / (N * num_hours)) * sum(ri_arr)
    return ri_arr, r_avg


def calculate_MAD(x_y_z_list, num_hours):
    """
    calculate MAD for every day time.
    the ri list contains only the [x,y,z]!=[0,0,0],
    so the MAD will divide by N * num_hours, and not by the length og the ri list (= dis_arr length).
    :param x_y_z_list: list of lists of x, y, z values
    :param num_hours: on how much hours we are calculating the average
    :return: the MAD value
    """
    # calculate MAD for every day time.
    # if there is no information on specific second, calculate it as [0,0,0]
    ri_arr, r_avg = calculate_average(x_y_z_list, num_hours)
    dis_arr = [np.abs(ri - r_avg) for ri in ri_arr]
    # MAD = 1/n * ∑ | ri - r' |
    MAD = (1 / (N * num_hours)) * sum(dis_arr)
    return MAD


class Sensor_Data():
    """
    this is a general sensor class.
    """
    def __init__(self, sensor_name):
        """
        init function - init the sensor name and initialize the dic_data
        :param sensor_name: the name of the sensor
        """

        self.name = sensor_name

        # this dictionary will contain the data of every date and every hour.
        # its format:
        # data_dic = { date1: {0: [data on this hour], 1: [data on this hour], ..., 23: [data on this hour] },
        #              date2: {0: [data on this hour], 1: [data on this hour], ..., 23: [data on this hour] },
        #              ...
        #              dateN: {0: [data on this hour], 1: [data on this hour], ..., 23: [data on this hour] }
        #           }
        self.data_dic = {}

    def calc_calculations_on_dic(self, day_times, num_times=1,
                                 calc_avg=True, calc_std=True, calc_median=False, calc_common=False):
        """
        this method pass on the data in the data_dic, collect it to day times data,
        and do calculations on every day time data.
        :param day_times: a dictionary of day times, contains the day hours, divided to day times
        :param num_times: how much data arrays there are in every day time data
        :param calc_avg: boolean value - to calculate the average or not
        :param calc_std: boolean value - to calculate the std or not
        :param calc_median: boolean value - to calculate the median or not
        :param calc_common: boolean value - to calculate the common or not
        :return: two lists - titles data list, calculated data list

        for wifi & bluetooth:
        1. for every day time, pass on every hour in it, and collect all the MACs of these hours.
        2. for every MACs list of day time in date, takes the unique MACs.
        3. count how many unique MACs there are in every day time in date, and insert it to the day_times_data list.
        4. do avg and std on this list, on every day time.
        ---> number of columns : num_day_times * 2

        for accelerometer:
        1. for every day time, pass on every hour in it, and collect all the x_y_z lists.
        2. for every x_y_z list of day time in date, calculate the MAD of it, and insert it to the day_times_data list.
           (calculate the MAD in this way: if there is no info of some time, calculate it as 0.
           the average calculate like there is 60*60*num_hours data info.)
        4. do avg and std on this list, on every day time.
        ---> number of columns : num_day_times * 2

        for texts:
        1. for every day time, pass on every hour in it, and collect the number of the sent texts,
           and the number of the received texts.
        2. do avg and std on every list (num received texts vs num sent texts), on every day time.
        ---> number of columns : num_day_times * (2 + 2) = num_day_times * 4

        for calls:
        1. for every day time, pass on every hour in it, and collect:
           a. the number of the out calls.
           b. the number of the in calls.
           c. the number of the missed calls.
           d. the number of the out calls with duration 0.
           e. the median of the duration time in this part of day (for every date).
           f. the S value on the phones numbers durations time.
        2. do avg, std, common and median on a, b, on every day time.
        3. do avg of on c, d, e, f, on every day time.
        4. do avg on the percent of the out calls, on every day time.
        ---> number of columns : num_day_times * (4 + 4 + 1 + 1 + 1 + 1 + 1) = num_day_times * 9

        for power state:
        1. for every day time, pass on every hour in it, and collect:
           a. the number of the times the phone was on.
           b. the duration of the time the phone was on.
           c. the number of the times the phone was on for short time.
           d. TODO - the number of the times the phone was off for short time.
        2. do avg and std on a, b, on every day time.
        3. do avg on the number of the short on duration times.
        4. do avg on the percent of the short on duration times.
        5. TODO - do avg on the percent of the short off duration times.
        ---> number of columns : num_day_times * (2 + 2 + 1 + 1) = num_day_times * 6
        TODO - to add the 5th value.
        """

        # check that the day times include max 24 hours
        check_day_time_structure(day_times)

        # create a list with n lists. every list contains the data of its day time.
        day_times_data = [[] for i in range(len(day_times))]

        # pass on every date in the data_dic
        for date, hours_data_dic in self.data_dic.items():
            # pass on every day time in the day_times array
            for day_time_index, (day_time, hours_in_day_time) in enumerate(day_times.items()):

                # for wifi & bluetooth:
                if self.name == 'wifi' or self.name == 'bluetooth':
                    MACs_list = np.array([])
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            MACs_list = np.append(MACs_list, hours_data_dic[hour])
                    num_unique_MACs = len(np.unique(MACs_list))
                    day_times_data[day_time_index].append(num_unique_MACs)

                # for accelerometer:
                if self.name == 'accelerometer':
                    X_Y_Zs_list = []
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            X_Y_Zs_list += hours_data_dic[hour]
                    day_times_data[day_time_index].append(calculate_MAD(X_Y_Zs_list, len(hours_in_day_time)))

                # for texts:
                if self.name == 'texts':
                    out_in = np.array([0, 0])   # [num_in_texts, num_out_texts]

                    # pass on every hour in the date time, and collect the data in its cell in the out_in array
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            out_in += np.array(hours_data_dic[hour])

                    # if the lists are not initialized yet
                    if len(day_times_data[day_time_index]) == 0:
                        day_times_data[day_time_index] = [[], []]

                    day_times_data[day_time_index][IN].append(out_in[IN])
                    day_times_data[day_time_index][OUT].append(out_in[OUT])

                # for calls:
                if self.name == 'calls':
                    # calls_types = [num_in_calls, num_out_calls,
                    #                num_missed_calls, num_out_calls_with_duration_0,
                    #                duration_times_list, phone_numbers_durations_dic]
                    calls_types = np.array([0, 0, 0, 0, [], collections.Counter()])

                    # pass on every hour in the date time, and collect the data in its cell in the calls_types array
                    # NOTE that the addition between the counters cause to ignore from the keys that have value 0,
                    # and this is good for us for calculating the S (log(0) is invalid)
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            calls_types += np.array(hours_data_dic[hour])

                    # if the lists are not initialized yet
                    if len(day_times_data[day_time_index]) == 0:
                        day_times_data[day_time_index] = [[], [], [], [], [], []]

                    day_times_data[day_time_index][IN].append(calls_types[IN])
                    day_times_data[day_time_index][OUT].append(calls_types[OUT])
                    day_times_data[day_time_index][MISSED].append(calls_types[MISSED])
                    day_times_data[day_time_index][OUT_0].append(calls_types[OUT_0])
                    day_times_data[day_time_index][DURATION_MEDIAN].append(self.calc_median(calls_types[DURATION_MEDIAN], 0)[1])
                    day_times_data[day_time_index][PHONE_NUMBERS_DURATIONS].append(self.calc_S_for_calls(calls_types[PHONE_NUMBERS_DURATIONS], len(hours_in_day_time)))

                # for power state:
                if self.name == 'power_state':
                    power_state_data = np.array([0, 0.0, 0])     # [num_times, sum_time, num_short_time]
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            power_state_data += np.array(hours_data_dic[hour])

                    # if the lists are not initialized yet
                    if len(day_times_data[day_time_index]) == 0:
                        day_times_data[day_time_index] = [[], [], []]

                    # a list that contains the num on times of every day time, for all of the dates
                    day_times_data[day_time_index][NUM_TIMES].append(power_state_data[NUM_TIMES])
                    # a list that contains the sum on times of every day time, for all of the dates
                    day_times_data[day_time_index][SUM_TIMES].append(power_state_data[SUM_TIMES])
                    # a list that contains the num of the_short on times duration of every day time, for all of
                    # the dates
                    day_times_data[day_time_index][SHORT_ON_TIME].append(power_state_data[SHORT_ON_TIME])

        # this list will contain all the titles of the calculated data
        titles_list = []
        # this list will contain the calculate data itself
        avr_and_sd_list = []

        # run on every data list, and calculates the avg & std & median & common
        for run in range(num_times):
            titles_list_tmp, avr_and_sd_list_tmp = self.calc_calculations_on_list(day_times, day_times_data, run,
                                                                                  num_times, calc_avg, calc_std,
                                                                                  calc_median, calc_common)
            titles_list += titles_list_tmp
            avr_and_sd_list += avr_and_sd_list_tmp

        # the calls has more data to calculate
        if self.name == 'calls':
            for day_time_index, day_time in enumerate(day_times):

                # calculate the average of the missed calls
                title, avg = self.calc_avg(day_times_data[day_time_index][MISSED],
                                           day_time, additional_name='2_')
                titles_list.append(title), avr_and_sd_list.append(avg)

                # calculate the average of the outgoing calls with duration 0
                title, avg = self.calc_avg(day_times_data[day_time_index][OUT_0], day_time,
                                           additional_name='1_duration_0_')
                titles_list.append(title), avr_and_sd_list.append(avg)

                # calculate the average of the median of the duration calls
                title, avg = self.calc_avg(day_times_data[day_time_index][DURATION_MEDIAN], day_time,
                                           additional_name='duration_median_')
                titles_list.append(title), avr_and_sd_list.append(avg)

                # calculate the average of the percent of the outgoing calls
                all_calls = np.array(day_times_data[day_time_index][IN]) + np.array(day_times_data[day_time_index][OUT]) + np.array(day_times_data[day_time_index][MISSED])
                percent_outgoing_calls_arr = safe_arr_divide(np.array(day_times_data[day_time_index][OUT]), all_calls)
                title, avg = self.calc_avg(percent_outgoing_calls_arr, day_time, additional_name='percent_outgoing_')
                titles_list.append(title), avr_and_sd_list.append(avg)

                # calculate the avg of S (S = Different hardening of the user with the different contacts)
                title, avg = self.calc_avg(day_times_data[day_time_index][PHONE_NUMBERS_DURATIONS], day_time, additional_name='S')
                titles_list.append(title), avr_and_sd_list.append(avg)

        # the power state has more data to calculate
        if self.name == 'power_state':
            for day_time_index, day_time in enumerate(day_times):

                # calculate the average of the short on duration time
                title, avg = self.calc_avg(day_times_data[day_time_index][SHORT_ON_TIME],
                                           day_time, additional_name='2_')
                titles_list.append(title), avr_and_sd_list.append(avg)

                # calculate the average of the percent of the num short on duration time
                sum_short_on_time_duration_arr = np.array(day_times_data[day_time_index][SHORT_ON_TIME])
                sum_num_on_time_arr = np.array(day_times_data[day_time_index][NUM_TIMES])
                percent_short_on_duration_time = safe_arr_divide(sum_short_on_time_duration_arr, sum_num_on_time_arr)
                title, avg = self.calc_avg(percent_short_on_duration_time,
                                           day_time, additional_name='3_')
                titles_list.append(title), avr_and_sd_list.append(avg)

        return titles_list, avr_and_sd_list

    def calc_calculations_on_list(self, day_times, day_times_data, run, num_times,
                                  calc_avg, calc_std, calc_median, calc_common):
        """
        :param day_times: the day times structure
        :param day_times_data: the data lists for every day time
        :param run: which run it is - which list to calculate (relevant only if they are number of data)
        :param num_times: how much lists there are in every day time
        :param calc_avg: boolean value - if to calculate avg or not
        :param calc_std: boolean value - if to calculate std or not
        :param calc_median: boolean value - if to calculate median or not
        :param calc_common: boolean value - if to calculate common or not
        :return: two lists - the calculated values and its titles
        """

        calculations_list = []
        titles_list = []

        # the run is relevant to the texts, calls, power_states codes.
        # (because we need to find the avg of number of data)
        for i, day_time in enumerate(day_times):

            if calc_avg:
                if num_times == 1:
                    title, avg = self.calc_avg(day_times_data[i], day_time)
                else:
                    title, avg = self.calc_avg(day_times_data[i][run], day_time, additional_name=str(run)+'_')
                titles_list.append(title), calculations_list.append(avg)

            if calc_std:
                if num_times == 1:
                    title, std = self.calc_std(day_times_data[i], day_time)
                else:
                    title, std = self.calc_std(day_times_data[i][run], day_time, additional_name=str(run) + '_')
                titles_list.append(title), calculations_list.append(std)

            if calc_median:
                if num_times == 1:
                    title, median = self.calc_median(day_times_data[i], day_time)
                else:
                    title, median = self.calc_median(day_times_data[i][run], day_time, additional_name=str(run) + '_')
                titles_list.append(title), calculations_list.append(median)

            if calc_common:
                if num_times == 1:
                    title, common = self.calc_common(day_times_data[i], day_time)
                else:
                    title, common = self.calc_common(day_times_data[i][run], day_time, additional_name=str(run) + '_')
                titles_list.append(title), calculations_list.append(common)

        return titles_list, calculations_list

    def calc_avg(self, arr, day_time, additional_name=''):
        """
        :param arr: the array to calculate average on it
        :param day_time: the day time name - for the title
        :param additional_name: additional name - for the title
        :return: the title and the calculated avg
        """
        avg = np.array(arr).mean()
        title = self.name + '_' + additional_name + str(day_time) + '_avg'
        return title, avg

    def calc_std(self, arr, day_time, additional_name=''):
        """
        :param arr: the array to calculate standard division on it
        :param day_time: the day time name - for the title
        :param additional_name: additional name - for the title
        :return: the title and the calculated std
        """
        std = np.array(arr).std()
        title = self.name + '_' + additional_name + str(day_time) + '_std'
        return title, std

    def calc_median(self, arr, day_time, additional_name=''):
        """
        :param arr: the array to calculate median on it
        :param day_time: the day time name - for the title
        :param additional_name: additional name - for the title
        :return: the title and the calculated median
        """
        if not len(arr):
            median = 0
        else:
            median = np.median(np.array(arr))
        title = self.name + '_' + additional_name + str(day_time) + '_median'
        return title, median

    def calc_common(self, arr, day_time, additional_name=''):
        """
        :param arr: the array to calculate common on it
        :param day_time: the day time name - for the title
        :param additional_name: additional name - for the title
        :return: the title and the calculated common
        """
        common = np.bincount(np.array(arr)).argmax()
        title = self.name + '_' + additional_name + str(day_time) + '_common'
        return title, common

    def calc_F_list_for_calls(self, phone_numbers_durations_ctr, day_time_duration_in_hour):
        """
        calculate the Fi of every phone number (contact)
        :param phone_numbers_durations_ctr: dictionary of phone numbers and the durations time
        :param day_time_duration_in_hour: the number of the hours in the day time
        :return: the list of the F values of every contact
        """
        duration_time_in_sec = day_time_duration_in_hour * NUM_MIN_IN_HOUR * NUM_SEC_IN_MIN
        # Fi = 1/T * ti
        Fi_list = [duration / duration_time_in_sec for phone_number, duration in phone_numbers_durations_ctr.items()]
        return Fi_list

    def calc_S_for_calls(self, phone_numbers_durations_ctr, day_time_duration_in_hour):
        """
        calculate the S value, S = - ∑ Fi * log(Fi)
        :param phone_numbers_durations_ctr: dictionary of phone numbers and the durations time
        :param day_time_duration_in_hour: the number of the hours in the day time
        :return: the S value
        """
        Fi_list = self.calc_F_list_for_calls(phone_numbers_durations_ctr, day_time_duration_in_hour)
        return -1 * sum([Fi * math.log10(Fi) for Fi in Fi_list])
