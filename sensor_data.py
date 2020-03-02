import numpy as np
import date_time

# num seconds in a hour
N = 60 * 60


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

    def calc_avr_and_sd_on_dic(self, day_times):

        num_hours = len([len(hours) for day_time, hours in day_times.items()])

        if num_hours > 24:
            raise Exception('ERROR: You have hours more that 24 hours. Please choose hours between 0-23.')

        # create a list with n lists. every list contains the data of its day time.
        day_times_data = [[] for i in range(len(day_times))]

        avr_and_sd_list = []
        titles_list = []

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
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(self.data_dic)

        for i, day_time in enumerate(day_times):
            avr_and_sd_list.append(np.array(day_times_data[i]).mean())
            titles_list.append(self.name + '_' + str(day_time) + '_avg')

            avr_and_sd_list.append(np.array(day_times_data[i]).std())
            titles_list.append(self.name + '_' + str(day_time) + '_std')

        return titles_list, avr_and_sd_list
