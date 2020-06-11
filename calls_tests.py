import unittest
from global_tests_functions import *
from calls import *

# the path to the accelerometer data directory
calls_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data\2ppn81sa\calls'


def count_num_outgoing_0_calls(file, string):
    """
    :param file: the file to read the data from (the test combined file)
    :param string: the string to find
    :return: the number of the outgoing calls with durations 0
    """
    texts_df = pd.read_csv(file, usecols=['call type', 'duration in seconds'])
    return texts_df[(texts_df['call type'] == string) & (texts_df['duration in seconds'] == 0)].shape[0]


def collect_all_durations_list():
    """
    :return: the durations list from the sensor data
    """
    durations_list = []
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            durations_list += hour_data[DURATION_MEDIAN]
    return durations_list


def collect_all_durations_from_file(file):
    """
    :param file: the file to read the data from (the test combined file)
    :return: the durations list from the combined file (test data)
    """
    calls_df = pd.read_csv(file, usecols=['duration in seconds'])
    return list(calls_df['duration in seconds'])


def collect_all_contacts():
    """
    :return: the sorted list of the contacts numbers, from the sensor data
    """
    contacts_list = []
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            contacts_list += list(hour_data[PHONE_NUMBERS_DURATIONS].keys())
    return sorted(list(np.unique(contacts_list)))


def collect_all_contacts_from_file(file):
    """
    :param file: the file to read the data from (the test combined file)
    :return: the sorted list of the contacts numbers, from the combine file (test data)
    """
    calls_df = pd.read_csv(file, usecols=['hashed phone number'])
    return sorted(list(np.unique(calls_df['hashed phone number'])))


def sum_durations_for_contacts():
    """
    :return: the sum of the calls durations from the sensor data
    """
    sum_dur = 0
    for date, hours_data in calls_data.data_dic.items():
        for hour, hour_data in hours_data.items():
            sum_dur += sum(hour_data[PHONE_NUMBERS_DURATIONS].values())
    return sum_dur


def calls_organize_all_data():
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(calls_dir)
    calls_data = Sensor_Data('calls')
    # pass on every file and send it to the organize_data function
    for curr_calls_file in os.listdir(calls_dir):
        organize_data(calls_dir, curr_calls_file, calls_data)

    return calls_data


# the collected data, just like the code do it
calls_data = calls_organize_all_data()


class CallsTests(unittest.TestCase):

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        calls_num_dates = len(calls_data.data_dic)
        test_num_dates = count_num_dates(calls_dir)

        self.assertEqual(calls_num_dates, test_num_dates)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        calls_num_hours = sum([len(calls_data.data_dic[date]) for date in calls_data.data_dic])
        test_num_hours = count_num_hours(calls_dir)

        self.assertEqual(calls_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_out_calls and the num_in_calls and num_missed_calls
         and num_out_0_calls the calls durations list and the contacts list
        and the sum durations calls time are collected well"""
        combined_file = combine_all_files_to_one_file(calls_dir)

        calls_num_out_calls = count_num_data(calls_data, OUT)
        test_num_out_calls = count_num_strings_in_file(combined_file, 'Outgoing Call', 'call type')

        calls_num_in_calls = count_num_data(calls_data, IN)
        test_num_in_calls = count_num_strings_in_file(combined_file, 'Incoming Call', 'call type')

        calls_num_missed_calls = count_num_data(calls_data, MISSED)
        test_num_missed_calls = count_num_strings_in_file(combined_file, 'Missed Call', 'call type')

        calls_num_out_0_calls = count_num_data(calls_data, OUT_0)
        test_num_out_0_calls = count_num_outgoing_0_calls(combined_file, 'Outgoing Call')

        calls_durations_list = collect_all_durations_list()
        test_durations_list = collect_all_durations_from_file(combined_file)

        calls_contacts_list = collect_all_contacts()
        test_contacts_list = collect_all_contacts_from_file(combined_file)

        calls_sum_durations = sum_durations_for_contacts()
        test_sum_durations = sum(test_durations_list)

        self.assertEqual(calls_num_out_calls, test_num_out_calls)
        self.assertEqual(calls_num_in_calls, test_num_in_calls)
        self.assertEqual(calls_num_missed_calls, test_num_missed_calls)
        self.assertEqual(calls_num_out_0_calls, test_num_out_0_calls)
        self.assertEqual(calls_durations_list, test_durations_list)
        self.assertEqual(calls_contacts_list, test_contacts_list)
        self.assertEqual(calls_sum_durations, test_sum_durations)


if __name__ == '__main__':
    unittest.main()
