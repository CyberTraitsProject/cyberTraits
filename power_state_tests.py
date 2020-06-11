import unittest
from global_tests_functions import *
from power_state import *

ON = "Screen turned on"
OFF = "Screen turned off"

# the path to the accelerometer data directory
power_state_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data\2ppn81sa\power_state'


def count_num_empty_files():
    """
    :return: how many empty files there are. i.e. - how much file not include events of ON or OFF
    """
    count = 0
    for curr_power_state_file in os.listdir(power_state_dir):
        power_states_df = pd.read_csv(os.path.join(power_state_dir, curr_power_state_file), usecols=['event'])
        power_states_list = list(power_states_df['event'])
        if ON not in power_states_list and OFF not in power_states_list:
            count += 1
    return count


def count_num_not_full_hours():
    """
    :return: how many hours there are that the phone wasn't on all this time.
    """
    count = 0
    for date, hours in power_state_data.data_dic.items():
        for hour, data_on_hour in hours.items():
            if data_on_hour[1] != 60.0:  # the sum_times
                count += 1
    return count


def sum_and_list_on_screen_events_in_file(file):
    """
    pass on every event, and if it ON event:
    1. if the next event is off, and the duration is less than 3 hours, sum it.
    2. if it is the last line, calculate the duration until end of this hour.
    3. the next event is not off - sum it as duration 0.
    :param file: the file to read the data from (the test combined file)
    :return: the sum on time and the list of the on times durations
    """
    power_state_df = pd.read_csv(file, usecols=['UTC time', 'event'])
    power_state_list = power_state_df['event']
    UTC_times_list = power_state_df['UTC time']

    sum_on_time = 0
    on_time_durations_list = []
    for i in range(len(UTC_times_list)):
        if power_state_list[i] == ON:
            on_time = datetime.datetime.strptime(UTC_times_list[i], '%Y-%m-%dT%H:%M:%S.%f')
            if i + 1 != len(UTC_times_list) and power_state_list[i + 1] == OFF:
                off_time = datetime.datetime.strptime(UTC_times_list[i + 1], '%Y-%m-%dT%H:%M:%S.%f')
                if off_time - on_time < datetime.timedelta(hours=3):
                    duration_time = (off_time - on_time).total_seconds() / 60
                    sum_on_time += duration_time
                    on_time_durations_list.append(duration_time)
            elif i + 1 == len(UTC_times_list):
                off_time = on_time.replace(microsecond=99, second=59, minute=59)
                duration_time = (off_time - on_time).total_seconds() / 60
                sum_on_time += duration_time
                on_time_durations_list.append(duration_time)
            elif power_state_list[i + 1] != OFF:
                off_time = on_time
                duration_time = (off_time - on_time).total_seconds() / 60
                sum_on_time += duration_time
                on_time_durations_list.append(duration_time)

    return sum_on_time, on_time_durations_list


def power_state_organize_all_data():
    """
    :return: the sensor data, just like the code do it
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
        on_time = get_date_time_from_UTC_time(returned_value)
        # the end of this hour
        off_time = on_time.replace(microsecond=99, second=59, minute=59)
        durations_list = get_list_of_power_on_durations(on_time, off_time)
        with open('duration_times.txt', 'a') as file:
            for duration in durations_list:
                file.write(str(duration) + '\n')
        update_durations_in_power_states_data_dic(on_time, durations_list, power_state_data.data_dic)
        update_short_duration(on_time, off_time, power_state_data.data_dic)

    return power_state_data


# the collected data, just like the code do it
power_state_data = power_state_organize_all_data()


class PowerStateTests(unittest.TestCase):

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        power_state_num_dates = len(power_state_data.data_dic)
        test_num_dates = count_num_dates(power_state_dir)

        self.assertEqual(power_state_num_dates, test_num_dates)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        power_state_num_hours = count_num_not_full_hours()   # without the hours that doesn't have file (i.e. all of this time was on)
        test_num_hours = count_num_hours(power_state_dir) - count_num_empty_files()

        self.assertEqual(power_state_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_on_events and the sum_on_events_durations and the durations list collected well"""
        combined_file = combine_all_files_to_one_file(power_state_dir)

        power_state_num_on_screen_event = count_num_data(power_state_data, NUM_TIMES)
        test_num_on_screen_event = count_num_strings_in_file(combined_file, 'Screen turned on', 'event')

        power_state_sum_on_screen_time = count_num_data(power_state_data, SUM_TIME)  # sum_on_screen_events()
        test_sum_on_screen_time, durations_list = sum_and_list_on_screen_events_in_file(combined_file)

        power_state_num_short_on_screen_time = count_num_data(power_state_data, SHORT_ON_TIME)
        test_num_short_on_screen_time = len([1 for duration in durations_list if datetime.timedelta(minutes=duration) < datetime.timedelta(seconds=COMMON_ON_TIME)])

        self.assertEqual(power_state_num_on_screen_event, test_num_on_screen_event)
        self.assertEqual(round(power_state_sum_on_screen_time, 4), round(test_sum_on_screen_time, 4))
        self.assertEqual(power_state_num_short_on_screen_time, test_num_short_on_screen_time)


if __name__ == '__main__':
    unittest.main()
