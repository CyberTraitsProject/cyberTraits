import numpy as np
import date_time

# num seconds in a hour
N = 60 * 60

IN = 0
OUT = 1
MISSED = 2
OUT_0 = 3
DURATION_MEDIAN = 4

def get_ri(x_y_z_arr):     # the accelerometer result in time i
    return pow((pow(x_y_z_arr[0], 2) + pow(x_y_z_arr[1], 2) + pow(x_y_z_arr[2], 2)), -2)   # (x^2 + y^2 + z^2)^-2


def calculate_average(x_y_z_list, num_hours):
    ri_arr = [get_ri(x_y_z) for x_y_z in x_y_z_list]
    r_avg = (1 / (N * num_hours)) * sum(ri_arr)
    return ri_arr, r_avg


def calculate_MAD(x_y_z_list, num_hours):
    # calculate MAD for every day time.
    # if there is no information on specific second, calculate it as [0,0,0]
    ri_arr, r_avg = calculate_average(x_y_z_list, num_hours)
    dis_arr = [np.abs(ri - r_avg) for ri in ri_arr]
    MAD = (1 / (N * num_hours)) * sum(dis_arr)
    return MAD

class Sensor_Data():
    def __init__(self, sensor_name):
        self.name = sensor_name
        '''self.data_dic = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [],
                         6: [], 7: [], 8: [], 9: [], 10: [], 11: [],
                         12: [], 13: [], 14: [], 15: [], 16: [], 17: [],
                         18: [], 19: [], 20: [], 21: [], 22: [], 23: []}'''

        # this dictionary will contain te data of every date and every hour.
        # its format:
        # data_dic = { date1: {hour1: [data on this hour], hour2: [data on this hour], ..., hourN: [data on this hour] },
        #              date1: {hour2: [data on this hour], hour2: [data on this hour], ..., hourN: [data on this hour] },
        #              ...
        #              date1: {hourM: [data on this hour], hour2: [data on this hour], ..., hourN: [data on this hour] }
        #           }

        self.data_dic = {}

    def calc_avr_and_sd_on_dic(self, day_times, num_times=1,
                               calc_avg=True, calc_std=True, calc_median=False, calc_common=False):

        num_hours = len([len(hours) for day_time, hours in day_times.items()])

        if num_hours > 24:
            raise Exception('ERROR: You have hours more that 24 hours. Please choose hours between 0-23.')

        # create a list with n lists. every list contains the data of its day time.
        day_times_data = [[] for i in range(len(day_times))]


        '''
        for wifi & bluetooth
        1. pass on every date
        2. for every date, pass on every day time in day_times
        3. for every day time, pass on every hour in it, and collect all the MACs of these hours. 
        4. for every MACs list of day time in date, takes the unique MACs.
        5. count how many unique MACs there are in every day time in date, and insert it to the day_times_data list.
        '''

        '''
        for accelerometer
        1. pass on every date
        2. for every date, pass on every day time in day_times
        3. for every day time, pass on every hour in it, and collect all the x_y_z lists. 
        4. for every x_y_z list of day time in date, calculate the MAD of it, and insert it to the day_times_data list.
           (calculate the MAD in this way: if there is no info of some time, calculate it as 0. 
           the average calculate like there is 60*60*num_hours data info.)
        '''

        for date, hours_data_dic in self.data_dic.items():
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
                    print(X_Y_Zs_list)
                    day_times_data[day_time_index].append(calculate_MAD(X_Y_Zs_list, len(hours_in_day_time)))
                if self.name == 'texts':
                    out_in = np.array([0, 0])
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            out_in += np.array(hours_data_dic[hour])
                    print(out_in)
                    try:
                        day_times_data[day_time_index][IN].append(out_in[IN])
                        day_times_data[day_time_index][OUT].append(out_in[OUT])
                    except IndexError:
                        day_times_data[day_time_index].insert(IN, [out_in[IN]])
                        day_times_data[day_time_index].insert(OUT, [out_in[OUT]])
                if self.name == 'calls':
                    calls_types = np.array([0, 0, 0, 0, []])
                    for hour in hours_in_day_time:
                        if hour in hours_data_dic:
                            calls_types += np.array(hours_data_dic[hour])
                    print(calls_types)
                    try:
                        day_times_data[day_time_index][IN].append(calls_types[IN])
                        day_times_data[day_time_index][OUT].append(calls_types[OUT])
                        day_times_data[day_time_index][MISSED].append(calls_types[MISSED])
                        day_times_data[day_time_index][OUT_0].append(calls_types[OUT_0])
                        day_times_data[day_time_index][DURATION_MEDIAN].append(self.calc_median(calls_types[DURATION_MEDIAN], 0)[1])
                    except IndexError:
                        day_times_data[day_time_index].insert(IN, [calls_types[IN]])
                        day_times_data[day_time_index].insert(OUT, [calls_types[OUT]])
                        day_times_data[day_time_index].insert(MISSED, [calls_types[MISSED]])
                        day_times_data[day_time_index].insert(OUT_0, [calls_types[OUT_0]])
                        day_times_data[day_time_index].insert(DURATION_MEDIAN, [self.calc_median(calls_types[DURATION_MEDIAN], 0)[1]])

        print(day_times_data)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(self.data_dic)
        titles_list = []
        avr_and_sd_list = []
        for run in range(num_times):
            titles_list_tmp, avr_and_sd_list_tmp = self.calc_avr_and_sd_on_list(day_times, day_times_data, run,
                                                                                calc_avg, calc_std, calc_median, calc_common)
            titles_list += titles_list_tmp
            avr_and_sd_list += avr_and_sd_list_tmp

        '''for i, day_time in enumerate(day_times):
            func()'''

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
                percent_outgoing_calls_arr = (np.array(day_times_data[day_time_index][OUT]) / all_calls)
                title, avg = self.calc_avg(percent_outgoing_calls_arr, day_time, additional_name='percent_outgoing_')
                titles_list.append(title), avr_and_sd_list.append(avg)
        print(titles_list)
        print(avr_and_sd_list)
        return titles_list, avr_and_sd_list


    def calc_avr_and_sd_on_list(self, day_times, day_times_data, run,
                                calc_avg, calc_std, calc_median, calc_common):
        avr_and_sd_list = []
        titles_list = []
        # currently, the run is relevant only to the texts code.
        # (because we need to find the avg of the sent and the received texts)
        for i, day_time in enumerate(day_times):
            if calc_avg:
                try:
                    avr_and_sd_list.append(np.array(day_times_data[i][run]).mean())
                    titles_list.append(self.name + '_' + str(run) + '_' + str(day_time) + '_avg')
                except IndexError:
                    avr_and_sd_list.append(np.array(day_times_data[i]).mean())
                    titles_list.append(self.name + '_' + str(day_time) + '_avg')

            if calc_std:
                try:
                    avr_and_sd_list.append(np.array(day_times_data[i][run]).std())
                    titles_list.append(self.name + '_' + str(run) + '_' + str(day_time) + '_std')
                except IndexError:
                    avr_and_sd_list.append(np.array(day_times_data[i]).std())
                    titles_list.append(self.name + '_' + str(day_time) + '_std')

            if calc_median:
                try:
                    avr_and_sd_list.append(np.median(np.array(day_times_data[i][run])))
                    titles_list.append(self.name + '_' + str(run) + '_' + str(day_time) + '_median')
                except IndexError:
                    avr_and_sd_list.append(np.median(np.array(day_times_data[i])))
                    titles_list.append(self.name + '_' + str(day_time) + '_median')

            if calc_common:
                try:
                    avr_and_sd_list.append(np.bincount(np.array(day_times_data[i][run])).argmax())
                    titles_list.append(self.name + '_' + str(run) + '_' + str(day_time) + '_common')
                except IndexError:
                    avr_and_sd_list.append(np.bincount(np.array(day_times_data[i])).argmax())
                    titles_list.append(self.name + '_' + str(day_time) + '_common')
        return titles_list, avr_and_sd_list

    def calc_avg(self, arr, day_time, additional_name=''):
        avg = np.array(arr).mean()
        title = self.name + '_' + additional_name + str(day_time) + '_avg'
        return title, avg

    def calc_std(self, arr, day_time, additional_name=''):
        std = np.array(arr).std()
        title = self.name + '_' + additional_name + str(day_time) + '_std'
        return title, std

    def calc_median(self, arr, day_time, additional_name=''):
        std = np.median(np.array(arr))
        title = self.name + '_' + additional_name + str(day_time) + '_median'
        return title, std

