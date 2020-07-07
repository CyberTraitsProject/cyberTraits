import unittest
from global_tests_functions import *
from accelerometer import *


def collect_all_xyz_lists(accelerometer_data):
    """
    run on the data in the dic, in collect the xyz_list of every date and every hour,
    to one list.
    :return: the xyz lists
    """
    x_y_z_list = []
    for date, hours_data in accelerometer_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            x_y_z_list += hour_data
    return x_y_z_list


def collect_xyz_from_file(combined_file):
    """
    run on the test combined file, and collect the xyz data of every second and
    every minute and every hour and every date.
    if there are numbers of data on the same date hour minute and second,
    takes the first data on it.
    :return: the xyz lists
    """
    accelerometer_df = pd.read_csv(combined_file, usecols=['UTC time', 'x', 'y', 'z'])
    x_list = accelerometer_df['x']
    y_list = accelerometer_df['y']
    z_list = accelerometer_df['z']
    UTC_times_list = accelerometer_df['UTC time']
    xyz_list = []
    p_date = p_hour = p_min = p_sec = 0
    for i in range(accelerometer_df.shape[0]):
        # UTC time format - "2020-04-17T08:12:53.267"
        c_date = UTC_times_list[i].split('T')[0]
        c_hour = (UTC_times_list[i].split('T')[1]).split(':')[0]
        c_min = (UTC_times_list[i].split('T')[1]).split(':')[1]
        c_sec = ((UTC_times_list[i].split('T')[1]).split(':')[2]).split('.')[0]

        if c_date != p_date or c_hour != p_hour or c_min != p_min or c_sec != p_sec:
            xyz_list.append([x_list[i], y_list[i], z_list[i]])
            p_date = c_date
            p_hour = c_hour
            p_min = c_min
            p_sec = c_sec

    return xyz_list


def calc_avg_and_std_on_file(day_times, combined_file):
    """
    :param day_times: the day times to do the calculations on it
    :param combined_file: the file with all of the data
    :return: the analyzed data in a list
    """
    accelerometer_df = pd.read_csv(combined_file, usecols=['UTC time', 'x', 'y', 'z'])
    UTC_time_list = accelerometer_df['UTC time']
    x_list = accelerometer_df['x']
    y_list = accelerometer_df['y']
    z_list = accelerometer_df['z']

    # list of lists that will contain the data of every day time, data on every date
    data_list_for_all_day_times = [[] for c_day_time in day_times]

    counter_data_for_cur_date = [[] for c_day_time in day_times]
    p_date = ''
    p_hour = ''
    p_min = ''
    p_sec = ''
    for i, UTC_time in enumerate(UTC_time_list):
        cur_date = UTC_time.split('T')[0]
        cur_hour = (UTC_time.split('T')[1]).split(':')[0]
        cur_min = (UTC_time.split('T')[1]).split(':')[1]
        cur_sec = ((UTC_time.split('T')[1]).split(':')[2]).split('.')[0]

        if cur_date != p_date and p_date:
            # update the sum times the kind of the data appeared in this date
            for j, c_day_time in enumerate(day_times):
                data_list_for_all_day_times[j].append(
                    do_MAD_on_xyz_lists(counter_data_for_cur_date[j], len(day_times[c_day_time])))
            counter_data_for_cur_date = [[] for c_day_time in day_times]

        if p_date != cur_date or p_hour != cur_hour or p_min != cur_min or p_sec != cur_sec:
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)].append([x_list[i], y_list[i], z_list[i]])
        p_date = cur_date
        p_hour = cur_hour
        p_min = cur_min
        p_sec = cur_sec

    # update the last date data
    for j, c_day_time in enumerate(day_times):
        data_list_for_all_day_times[j].append(
            do_MAD_on_xyz_lists(counter_data_for_cur_date[j], len(day_times[c_day_time])))

    avg_and_std_list = []
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i]))

    return avg_and_std_list


def accelerometer_organize_all_data(accelerometer_dir):
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(accelerometer_dir)
    accelerometer_data = Sensor_Data('accelerometer')
    # pass on every file and send it to the organize_data function
    for curr_accelerometer_file in os.listdir(accelerometer_dir):
        organize_data(accelerometer_dir, curr_accelerometer_file, accelerometer_data)

    return accelerometer_data


class AccelerometerTests(unittest.TestCase):

    def setUp(self):
        """
        kind of initialization function. run before every test/tests runs
        """
        # the path to the accelerometer data directory
        self.accelerometer_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data_edited\2pe2t6si\accelerometer'
        # the collected data, just like the code do it
        self.accelerometer_data = accelerometer_organize_all_data(self.accelerometer_dir)
        # the combined file for tests
        self.combined_file = combine_all_files_to_one_file(self.accelerometer_dir)

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        accelerometer_num_dates = len(self.accelerometer_data.data_dic)
        test_num_dates = count_num_dates(self.accelerometer_dir)

        self.assertEqual(accelerometer_num_dates, test_num_dates)
        self.assertEqual(accelerometer_num_dates, NUM_TESTED_DATES)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        accelerometer_num_hours = sum([len(self.accelerometer_data.data_dic[date]) for date in self.accelerometer_data.data_dic])
        test_num_hours = count_num_hours(self.accelerometer_dir)

        self.assertEqual(accelerometer_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the xyz data collected well"""
        accelerometer_x_y_z_list = collect_all_xyz_lists(self.accelerometer_data)
        test_x_y_z_list = collect_xyz_from_file(self.combined_file)

        self.assertEqual(len(accelerometer_x_y_z_list), len(test_x_y_z_list))
        self.assertEqual(round_list(accelerometer_x_y_z_list), round_list(test_x_y_z_list))

    def test_data_calculated_well(self):
        """Checks if the avg and std of the MADs lists_in_texts calculated well for every day time"""
        # avr_and_sd_list order is: [avg_MAD_dt1, std_MAD_dt1, ..., avg_MAD_dtN, std_MAD_dtN]
        titles_list, avr_and_sd_list = self.accelerometer_data.calc_calculations_on_dic(day_times)

        accelerometer_avg_and_std_MAD = avr_and_sd_list
        test_avg_and_std_MAD = calc_avg_and_std_on_file(day_times, self.combined_file)

        print('accelerometer_avg_and_std_MAD:', accelerometer_avg_and_std_MAD)
        print('test_avg_and_std_MAD:', test_avg_and_std_MAD)

        self.assertEqual(len(accelerometer_avg_and_std_MAD), len(test_avg_and_std_MAD))
        self.assertEqual(list(np.round(np.array(accelerometer_avg_and_std_MAD), 10)),
                         list(np.round(np.array(test_avg_and_std_MAD), 10)))


if __name__ == '__main__':
    unittest.main()
