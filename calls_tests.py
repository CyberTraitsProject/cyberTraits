import unittest
from global_tests_functions import *
from calls import *


def count_num_outgoing_0_calls(string, combined_file):
    """
    :param string: the string to find
    :return: the number of the outgoing calls with durations 0
    """
    texts_df = pd.read_csv(combined_file, usecols=['call type', 'duration in seconds'])
    return texts_df[(texts_df['call type'] == string) & (texts_df['duration in seconds'] == 0)].shape[0]


def collect_all_durations_list(calls_data):
    """
    :return: the durations list from the sensor data
    """
    durations_list = []
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            durations_list += hour_data[DURATION_MEDIAN]
    return durations_list


def collect_all_durations_from_file(combined_file):
    """
    :return: the durations list from the combined file (test data)
    """
    calls_df = pd.read_csv(combined_file, usecols=['duration in seconds'])
    return list(calls_df['duration in seconds'])


def collect_all_contacts(calls_data):
    """
    :return: the sorted list of the contacts numbers, from the sensor data
    """
    contacts_list = []
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            contacts_list += list(hour_data[PHONE_NUMBERS_DURATIONS].keys())
    return sorted(list(np.unique(contacts_list)))


def collect_all_contacts_from_file(combined_file):
    """
    :return: the sorted list of the contacts numbers, from the combine file (test data)
    """
    calls_df = pd.read_csv(combined_file, usecols=['hashed phone number'])
    return sorted(list(np.unique(calls_df['hashed phone number'])))


def sum_durations_for_contacts(calls_data):
    """
    :return: the sum of the calls durations from the sensor data
    """
    sum_dur = 0
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            sum_dur += sum(hour_data[PHONE_NUMBERS_DURATIONS].values())
    return sum_dur


def do_calculations_on_file(day_times, combined_file):
    """
    :param day_times: the day times to do the calculations on it
    :param combined_file: the file with all of the data
    :return: the analyzed data in a list
    """
    calls_df = pd.read_csv(combined_file, usecols=['UTC time', 'hashed phone number', 'call type', 'duration in seconds'])
    UTC_time_list = calls_df['UTC time']
    phones_list = calls_df['hashed phone number']
    calls_types_list = calls_df['call type']
    durations_list = calls_df['duration in seconds']

    # list of lists that will contain the data of every day time, data on every date
    data_list_for_all_day_times = [[[], [], [], [], [], [], []] for c_day_time in day_times]

    counter_data_for_cur_date = [[0, 0, 0, 0, [], collections.Counter()] for c_day_time in day_times]

    p_date = ''
    for i, UTC_time in enumerate(UTC_time_list):
        cur_date = UTC_time.split('T')[0]
        cur_hour = (UTC_time.split('T')[1]).split(':')[0]

        if cur_date != p_date and p_date:
            # update the previous date data in the all data list
            for j, c_day_time in enumerate(day_times):
                num_in_calls_in_dt = counter_data_for_cur_date[j][0]
                data_list_for_all_day_times[j][0].append(num_in_calls_in_dt)  # num_in_calls
                num_out_calls_in_dt = counter_data_for_cur_date[j][1]
                data_list_for_all_day_times[j][1].append(num_out_calls_in_dt)  # num_out_calls
                num_missed_calls_in_dt = counter_data_for_cur_date[j][2]
                data_list_for_all_day_times[j][2].append(num_missed_calls_in_dt)  # num_missed_calls
                data_list_for_all_day_times[j][3].append(counter_data_for_cur_date[j][3])  # num_out0_calls
                data_list_for_all_day_times[j][4].append(
                    do_median_on_list(counter_data_for_cur_date[j][4]))  # median of the durations list
                all_calls_in_dt = num_out_calls_in_dt + num_in_calls_in_dt + num_missed_calls_in_dt
                all_calls_in_dt = 1 if all_calls_in_dt == 0 else all_calls_in_dt
                data_list_for_all_day_times[j][5].append(
                    num_out_calls_in_dt / all_calls_in_dt)  # percent outgoing calls
                data_list_for_all_day_times[j][6].append(
                    do_S_on_dic(counter_data_for_cur_date[j][5] + collections.Counter(),
                                len(day_times[c_day_time])))  # S of phones calls durations

            counter_data_for_cur_date = [[0, 0, 0, 0, [], collections.Counter()] for c_day_time in day_times]
        p_date = cur_date

        # update the num_in_calls
        if calls_types_list[i] == 'Incoming Call':
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][0] += 1
        # update the num_out_calls
        if calls_types_list[i] == 'Outgoing Call':
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][1] += 1
        # update the num_missed_calls
        if calls_types_list[i] == 'Missed Call':
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][2] += 1
        # update the num_out_0_calls
        if calls_types_list[i] == 'Outgoing Call' and durations_list[i] == 0:
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][3] += 1
        # add the duration to the durations list
        counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][4].append(durations_list[i])
        # update the dictionary of the durations calls with every contact
        counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][5][phones_list[i]] += durations_list[i]

    # update the last date data
    for j, c_day_time in enumerate(day_times):
        num_in_calls_in_dt = counter_data_for_cur_date[j][0]
        data_list_for_all_day_times[j][0].append(num_in_calls_in_dt)  # num_in_calls
        num_out_calls_in_dt = counter_data_for_cur_date[j][1]
        data_list_for_all_day_times[j][1].append(num_out_calls_in_dt)  # num_out_calls
        num_missed_calls_in_dt = counter_data_for_cur_date[j][2]
        data_list_for_all_day_times[j][2].append(num_missed_calls_in_dt)  # num_missed_calls
        data_list_for_all_day_times[j][3].append(counter_data_for_cur_date[j][3])  # num_out0_calls
        data_list_for_all_day_times[j][4].append(
            do_median_on_list(counter_data_for_cur_date[j][4]))  # median of the durations list
        all_calls_in_dt = num_out_calls_in_dt + num_in_calls_in_dt + num_missed_calls_in_dt
        all_calls_in_dt = 1 if all_calls_in_dt == 0 else all_calls_in_dt
        data_list_for_all_day_times[j][5].append(num_out_calls_in_dt / all_calls_in_dt)  # percent outgoing calls
        data_list_for_all_day_times[j][6].append(
            do_S_on_dic(counter_data_for_cur_date[j][5] + collections.Counter(),
                        len(day_times[c_day_time])))  # S of phones calls durations

    avg_and_std_list = []
    # calculate the calculations on num_in_calls
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][0]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i][0]))
        avg_and_std_list.append(do_median_on_list(data_list_for_all_day_times[i][0]))
        avg_and_std_list.append(do_common_on_list(data_list_for_all_day_times[i][0]))
    # calculate the calculations on num_out_calls
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][1]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i][1]))
        avg_and_std_list.append(do_median_on_list(data_list_for_all_day_times[i][1]))
        avg_and_std_list.append(do_common_on_list(data_list_for_all_day_times[i][1]))
    # calculate the avg on num_missed_calls, num_out_0_calls, durations_median_list, percent outgoing calls, S
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][2]))
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][3]))
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][4]))
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][5]))
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][6]))

    return avg_and_std_list


def calls_organize_all_data(calls_dir):
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(calls_dir)
    calls_data = Sensor_Data('calls')
    # pass on every file and send it to the organize_data function
    for curr_calls_file in os.listdir(calls_dir):
        organize_data(calls_dir, curr_calls_file, calls_data)

    return calls_data


class CallsTests(unittest.TestCase):

    def setUp(self):
        """
        kind of initialization function. run before every test/tests runs
        """
        # the path to the accelerometer data directory
        self.calls_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data_edited\2pe2t6si\calls'
        # the collected data, just like the code do it
        self.calls_data = calls_organize_all_data(self.calls_dir)
        # the combined file for tests
        self.combined_file = combine_all_files_to_one_file(self.calls_dir)

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        calls_num_dates = len(self.calls_data.data_dic)
        test_num_dates = count_num_dates(self.calls_dir)

        self.assertEqual(calls_num_dates, NUM_TESTED_DATES)
        self.assertEqual(calls_num_dates, test_num_dates)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        calls_num_hours = sum([len(self.calls_data.data_dic[date]) for date in self.calls_data.data_dic])
        test_num_hours = count_num_hours(self.calls_dir)

        self.assertEqual(calls_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_out_calls and the num_in_calls and num_missed_calls
         and num_out_0_calls the calls durations list and the contacts list
        and the sum durations calls time are collected well"""
        combined_file = combine_all_files_to_one_file(self.calls_dir)

        calls_num_out_calls = count_num_data(self.calls_data, OUT)
        test_num_out_calls = count_num_strings_in_file(combined_file, 'Outgoing Call', 'call type')

        calls_num_in_calls = count_num_data(self.calls_data, IN)
        test_num_in_calls = count_num_strings_in_file(combined_file, 'Incoming Call', 'call type')

        calls_num_missed_calls = count_num_data(self.calls_data, MISSED)
        test_num_missed_calls = count_num_strings_in_file(combined_file, 'Missed Call', 'call type')

        calls_num_out_0_calls = count_num_data(self.calls_data, OUT_0)
        test_num_out_0_calls = count_num_outgoing_0_calls('Outgoing Call', self.combined_file)

        calls_durations_list = collect_all_durations_list(self.calls_data)
        test_durations_list = collect_all_durations_from_file(self.combined_file)

        calls_contacts_list = collect_all_contacts(self.calls_data)
        test_contacts_list = collect_all_contacts_from_file(self.combined_file)

        calls_sum_durations = sum_durations_for_contacts(self.calls_data)
        test_sum_durations = sum(test_durations_list)

        self.assertEqual(calls_num_out_calls, test_num_out_calls)
        self.assertEqual(calls_num_in_calls, test_num_in_calls)
        self.assertEqual(calls_num_missed_calls, test_num_missed_calls)
        self.assertEqual(calls_num_out_0_calls, test_num_out_0_calls)
        self.assertEqual(calls_durations_list, test_durations_list)
        self.assertEqual(calls_contacts_list, test_contacts_list)
        self.assertEqual(calls_sum_durations, test_sum_durations)

    def test_data_calculated_well(self):
        """Checks if the avg and std of num_out_calls and the num_in_calls calculated well for every day time"""
        # avr_and_sd_list order is: [avg_in_dt1, std_in_dt1, median_in_dt1, common_in_dt1, ...,
        #                            avg_in_dtN, std_in_dtN, median_in_dtN, common_in_dtN,
        #                            avg_out_dt1, std_out_dt1, median_out_dt1, common_out_dt1, ...,
        #                            avg_out_dtN, std_out_dtN, median_out_dtN, common_out_dtN,
        #                            avg_missed_dt1, avg_out_0_dt1, avg_median_duration_dt1,
        #                            avg_percent_out_dt1, avg_S_dt1, ...,
        #                            avg_missed_dtN, avg_out_0_dtN, avg_median_duration_dtN,
        #                            avg_percent_out_dtN, avg_S_dtN]
        titles_list, avr_and_sd_list = self.calls_data.calc_calculations_on_dic(day_times, num_times=2, calc_median=True,
                                                                           calc_common=True)
        test_calculations_list = do_calculations_on_file(day_times, self.combined_file)

        calls_avg_and_std_num_in_calls = avr_and_sd_list[:4 * len(day_times)]
        test_avg_and_std_num_in_calls = test_calculations_list[:4 * len(day_times)]

        calls_avg_and_std_num_out_calls = avr_and_sd_list[4 * len(day_times):8 * len(day_times)]
        test_avg_and_std_num_out_calls = test_calculations_list[4 * len(day_times):8 * len(day_times)]

        calls_avg_num_missed_num_out0_median_duratin_S_calls = avr_and_sd_list[8 * len(day_times):]
        test_avg_num_missed_num_out0_median_duratin_S_calls = test_calculations_list[8 * len(day_times):]

        self.assertEqual(len(calls_avg_and_std_num_in_calls), len(test_avg_and_std_num_in_calls))
        self.assertEqual(len(calls_avg_and_std_num_out_calls), len(test_avg_and_std_num_out_calls))
        self.assertEqual(len(calls_avg_num_missed_num_out0_median_duratin_S_calls),
                         len(test_avg_num_missed_num_out0_median_duratin_S_calls))

        print('calls_avg_and_std_num_in_calls:', calls_avg_and_std_num_in_calls)
        print('test_avg_and_std_num_in_calls:', test_avg_and_std_num_in_calls)

        print('calls_avg_and_std_num_out_calls:', calls_avg_and_std_num_out_calls)
        print('test_avg_and_std_num_out_calls:', test_avg_and_std_num_out_calls)

        print('calls_avg_num_missed_num_out0_median_duratin_S_calls:', calls_avg_num_missed_num_out0_median_duratin_S_calls)
        print('test_avg_num_missed_num_out0_median_duratin_S_calls:', test_avg_num_missed_num_out0_median_duratin_S_calls)

        self.assertEqual(list(np.round(np.array(calls_avg_and_std_num_in_calls), 4)),
                         list(np.round(np.array(test_avg_and_std_num_in_calls), 4)))
        self.assertEqual(list(np.round(np.array(calls_avg_and_std_num_out_calls), 4)),
                         list(np.round(np.array(test_avg_and_std_num_out_calls), 4)))
        self.assertEqual(list(np.round(np.array(calls_avg_num_missed_num_out0_median_duratin_S_calls), 4)),
                         list(np.round(np.array(test_avg_num_missed_num_out0_median_duratin_S_calls), 4)))


if __name__ == '__main__':
    unittest.main()
