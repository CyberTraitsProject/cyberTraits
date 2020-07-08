import unittest
from global_tests_functions import *
from power_state import *

ON = "Screen turned on"
OFF = "Screen turned off"


def file_finish_with_on(ps_file):
    """
    :param ps_file: the power state file
    :return: True if the file finished with ON wo OFF after then, and False if not
    """
    power_states_df = pd.read_csv(ps_file, usecols=['event'])
    power_states_list = list(power_states_df['event'])
    for i in range(len(power_states_list) - 1, -1, -1):
        if power_states_list[i] == ON:
            return True
        if power_states_list[i] == OFF or power_states_list[i] == SHUTDOWN:
            return False


def count_num_empty_files(power_state_dir):
    """
    :return: how many empty files there are. i.e. - how much file not include events of ON or OFF
    """
    count = 0
    prev_file = None
    for curr_power_state_file in os.listdir(power_state_dir):
        power_states_df = pd.read_csv(os.path.join(power_state_dir, curr_power_state_file), usecols=['event'])
        power_states_list = list(power_states_df['event'])
        # if the file doesnt contain ON dtat
        if ON not in power_states_list:
            # if the file also doesnt contain OFF data
            if OFF not in power_states_list and SHUTDOWN not in power_states_list:
                count += 1
            # the file contains OFF data --> check if it OFF after ON or OFF after OFF
            else:
                # OFF after OFF -> count it
                if prev_file and not file_finish_with_on(os.path.join(power_state_dir, prev_file)):
                    count += 1
        prev_file = curr_power_state_file
    return count


def count_num_not_full_hours(power_state_data):
    """
    :return: how many hours there are that the phone wasn't on all this time.
    """
    count = 0
    for date, hours in power_state_data.data_dic.items():
        for hour, data_on_hour in hours.items():
            if data_on_hour[1] != 60.0:  # the sum_times
                count += 1
    return count


def sum_and_list_on_screen_events_in_file(combined_file):
    """
    pass on every event, and if it ON event:
    1. if the next event is off, and the duration is less than 3 hours, sum it.
    2. if it is the last line, calculate the duration until end of this hour.
    3. the next event is not off - sum it as duration 0.
    :return: the sum on time and the list of the on times durations
    """
    power_state_df = pd.read_csv(combined_file, usecols=['UTC time', 'event'])
    power_state_list = power_state_df['event']
    UTC_times_list = power_state_df['UTC time']

    sum_on_time = 0
    on_time_durations_list = []
    last_on = None
    for i in range(len(UTC_times_list)):
        if power_state_list[i] == ON:
            if last_on:
                on_time_durations_list.append(0)
                last_on = None
            on_time = datetime.datetime.strptime(UTC_times_list[i], '%Y-%m-%dT%H:%M:%S.%f')
            if i + 1 != len(UTC_times_list) and power_state_list[i + 1] in OFF_LIST:
                off_time = datetime.datetime.strptime(UTC_times_list[i + 1], '%Y-%m-%dT%H:%M:%S.%f')
                if off_time - on_time < datetime.timedelta(hours=3):
                    duration_time = (off_time - on_time).total_seconds() / 60
                    sum_on_time += duration_time
                    on_time_durations_list.append(duration_time)
            elif i + 1 == len(UTC_times_list):
                off_time = on_time.replace(microsecond=999999, second=59, minute=59)
                duration_time = (off_time - on_time).total_seconds() / 60
                sum_on_time += duration_time
                on_time_durations_list.append(duration_time)
            elif power_state_list[i + 1] == ON:
                off_time = on_time
                duration_time = 0
                sum_on_time += duration_time
                on_time_durations_list.append(duration_time)
            else:   # not on and off, something else
                last_on = on_time
        elif power_state_list[i] in OFF_LIST and last_on:
            on_time = last_on
            last_on = None
            off_time = datetime.datetime.strptime(UTC_times_list[i], '%Y-%m-%dT%H:%M:%S.%f')
            if off_time - on_time < datetime.timedelta(hours=3):
                duration_time = (off_time - on_time).total_seconds() / 60
                sum_on_time += duration_time
                on_time_durations_list.append(duration_time)
    if last_on:
        off_time = last_on.replace(microsecond=999999, second=59, minute=59)
        duration_time = (off_time - last_on).total_seconds() / 60
        sum_on_time += duration_time
        on_time_durations_list.append(duration_time)

    return sum_on_time, on_time_durations_list


def update_data_on_date(on_time, off_time, day_times, counter_data_for_cur_date):
    """
    pass on every day time, and add it the time the screen was on
    :param on_time: the on screen time
    :param off_time: the off screen time
    :param day_times: the day times
    :param counter_data_for_cur_date: the counter data of the current date
    :return: the updated counter_data_for_cur_date
    """
    # the same date but not the same day time
    on_day_time_index = get_day_time_index(on_time.hour, day_times)
    off_day_time_index = get_day_time_index(off_time.hour, day_times)
    for i in range(on_day_time_index, off_day_time_index + 1):
        if i == off_day_time_index:
            duration_time = (off_time - on_time).total_seconds() / 60
            counter_data_for_cur_date[i][1] += duration_time
        else:
            end_day_time = get_key_from_hour(on_time.hour, day_times)
            end_hour = day_times[end_day_time][-1]
            end_date_time = on_time.replace(hour=end_hour, minute=59, second=59, microsecond=999999)
            duration_time = (end_date_time - on_time).total_seconds() / 60
            counter_data_for_cur_date[i][1] += duration_time
            on_time = on_time.replace(hour=end_hour + 1, minute=0, second=0, microsecond=0)
    return counter_data_for_cur_date


def update_data(on_time, off_time, day_times, counter_data_for_cur_date, data_list_for_all_day_times):
    """
    pass on every day time in every date between on_time to off_time, and add it the time the screen was on.
    :param on_time: the on screen time
    :param off_time: the off screen time
    :param day_times: the day times
    :param counter_data_for_cur_date: the counter data of the current date
    :param data_list_for_all_day_times: the counter data of all of the dates
    :return: the updated counter_data_for_cur_date, data_list_for_all_day_times
    """
    on_date = on_time.date()
    off_date = off_time.date()
    if on_date == off_date:
        counter_data_for_cur_date = update_data_on_date(on_time, off_time, day_times, counter_data_for_cur_date)
    # the max on time is no more than 24 hours
    else:
        cur_off_time = on_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        counter_data_for_cur_date = update_data_on_date(on_time, cur_off_time, day_times, counter_data_for_cur_date)

        for j, c_day_time in enumerate(day_times):
            data_list_for_all_day_times[j][0].append(counter_data_for_cur_date[j][0])  # num_on_times
            data_list_for_all_day_times[j][1].append(counter_data_for_cur_date[j][1])  # sum_on_times
            data_list_for_all_day_times[j][2].append(counter_data_for_cur_date[j][2])  # num_short_on_times
        counter_data_for_cur_date = [[0, 0, 0] for c_day_time in day_times]

        cur_on_time = off_time.replace(hour=0, minute=0, second=0, microsecond=0)
        counter_data_for_cur_date = update_data_on_date(cur_on_time, off_time, day_times, counter_data_for_cur_date)
    return counter_data_for_cur_date, data_list_for_all_day_times


def calc_avg_and_std_on_file(day_times, combined_file):
    """
    :param day_times: the day times to do the calculations on it
    :param combined_file: the file with all of the data
    :return: the analyzed data in a list
    """
    power_state_df = pd.read_csv(combined_file, usecols=['UTC time', 'event'])
    UTC_time_list = power_state_df['UTC time']
    event_type_list = power_state_df['event']

    # list of lists that will contain the data of every day time, data on every date
    data_list_for_all_day_times = [[[], [], []] for c_day_time in day_times]

    counter_data_for_cur_date = [[0, 0, 0] for c_day_time in day_times]
    p_date = ''
    last_on = None
    for i, UTC_time in enumerate(UTC_time_list):
        cur_date = UTC_time.split('T')[0]
        cur_hour = (UTC_time.split('T')[1]).split(':')[0]

        if cur_date != p_date and p_date:
            # update the sum times the kind of the data appeared in this date
            for j, c_day_time in enumerate(day_times):
                data_list_for_all_day_times[j][0].append(counter_data_for_cur_date[j][0])   # num_on_times
                data_list_for_all_day_times[j][1].append(counter_data_for_cur_date[j][1])   # sum_on_times
                data_list_for_all_day_times[j][2].append(counter_data_for_cur_date[j][2])   # num_short_on_times
            counter_data_for_cur_date = [[0, 0, 0] for c_day_time in day_times]
        p_date = cur_date

        if event_type_list[i] == ON:
            # update the num_on_times
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][0] += 1
            on_time = datetime.datetime.strptime(UTC_time_list[i], '%Y-%m-%dT%H:%M:%S.%f')
            if last_on:
                # update the num_short_on_times
                # if its related to another date, add it to the last data that added to data_list_for_all_day_times
                if last_on.date() != on_time.date():
                    data_list_for_all_day_times[get_day_time_index(last_on.hour, day_times)][2][-1] += 1
                else:
                    counter_data_for_cur_date[get_day_time_index(last_on.hour, day_times)][2] += 1
                last_on = None
            if i + 1 != len(UTC_time_list) and event_type_list[i + 1] in OFF_LIST:
                off_time = datetime.datetime.strptime(UTC_time_list[i + 1], '%Y-%m-%dT%H:%M:%S.%f')
                duration_time = (off_time - on_time).total_seconds() / 60
                # the same date and day time
                if on_time.date() == off_time.date() and get_day_time_index(on_time.hour,
                    day_times) == get_day_time_index(off_time.hour, day_times):
                    # if the duration is 3 or more -> ignore it
                    if off_time - on_time < datetime.timedelta(hours=MAX_ON_TIME):
                        # update the sum_on_times
                        counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][1] += duration_time
                        if off_time - on_time < datetime.timedelta(seconds=COMMON_ON_TIME):
                            # update the num_short_on_times
                            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][2] += 1
                else:
                    # if the duration is 3 or more -> ignore it
                    if off_time - on_time < datetime.timedelta(hours=MAX_ON_TIME):
                        counter_data_for_cur_date, data_list_for_all_day_times = update_data(on_time, off_time,
                                                                                             day_times,
                                                                                             counter_data_for_cur_date,
                                                                                             data_list_for_all_day_times)
                        if off_time.date() != on_time.date():
                            p_date = UTC_time_list[i + 1].split('T')[0]
            elif i + 1 == len(UTC_time_list):
                off_time = on_time.replace(microsecond=999999, second=59, minute=59)
                duration_time = (off_time - on_time).total_seconds() / 60
                # update the sum_on_times
                counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][1] += duration_time
                if off_time - on_time < datetime.timedelta(seconds=COMMON_ON_TIME):
                    # update the num_short_on_times
                    counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][2] += 1
            elif event_type_list[i + 1] not in OFF_LIST:
                last_on = on_time
        elif event_type_list[i] in OFF_LIST and last_on:
            on_time = last_on
            last_on = None
            off_time = datetime.datetime.strptime(UTC_time_list[i], '%Y-%m-%dT%H:%M:%S.%f')
            duration_time = (off_time - on_time).total_seconds() / 60
            # the same date and day time
            if on_time.date() == off_time.date() and get_day_time_index(on_time.hour,
                                                                        day_times) == get_day_time_index(off_time.hour,
                                                                                                         day_times):
                # update the sum_on_times
                counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][1] += duration_time
                if off_time - on_time < datetime.timedelta(seconds=COMMON_ON_TIME):
                    # update the num_short_on_times
                    counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][2] += 1
            else:
                # if the duration is 3 or more -> ignore it
                if off_time - on_time < datetime.timedelta(hours=MAX_ON_TIME):
                    counter_data_for_cur_date, data_list_for_all_day_times = update_data(on_time, off_time,
                                                                                         day_times,
                                                                                         counter_data_for_cur_date,
                                                                                         data_list_for_all_day_times)
                    if off_time.date() != on_time.date():
                        p_date = UTC_time_list[i + 1].split('T')[0]
        elif i + 1 == len(UTC_time_list) and last_on:
            on_time = last_on
            off_time = on_time.replace(microsecond=999999, second=59, minute=59)
            duration_time = (off_time - on_time).total_seconds() / 60
            # update the sum_on_times
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][1] += duration_time
            if off_time - on_time < datetime.timedelta(seconds=COMMON_ON_TIME):
                # update the num_short_on_times
                counter_data_for_cur_date[get_day_time_index(cur_hour, day_times)][2] += 1

    # update the last date data
    for i, c_day_time in enumerate(day_times):
        data_list_for_all_day_times[i][0].append(counter_data_for_cur_date[i][0])  # num_on_times
        data_list_for_all_day_times[i][1].append(counter_data_for_cur_date[i][1])  # sum_on_times
        data_list_for_all_day_times[i][2].append(counter_data_for_cur_date[i][2])  # num_short_on_times

    avg_and_std_list = []
    # do avg and std on num_on_times
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][0]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i][0]))
    # do avg and std on sum_on_times
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i][1]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i][1]))
    # do avg on num_short_on_times and percent_short_on_times
    for i, c_day_time in enumerate(day_times):
        avg_and_std_list.append(do_avg_on_list(
            data_list_for_all_day_times[i][2]))
        avg_and_std_list.append(do_avg_on_list(convert_nan_to_0(np.array(data_list_for_all_day_times[i][2]) /
                                               np.array(data_list_for_all_day_times[i][0]))))

    return avg_and_std_list


def power_state_organize_all_data(power_state_dir):
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
        on_time = returned_value
        # the end of this hour
        off_time = on_time.replace(microsecond=999999, second=59, minute=59)
        durations_list = get_list_of_power_on_durations(on_time, off_time)
        update_durations_in_power_states_data_dic(on_time, durations_list, power_state_data.data_dic)
        update_short_duration(on_time, off_time, power_state_data.data_dic)

    return power_state_data


class PowerStateTests(unittest.TestCase):

    def setUp(self):
        """
        kind of initialization function. run before every test/tests runs
        """
        # the path to the accelerometer data directory
        self.power_state_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data_edited\ygpxrisr\power_state'
        # the collected data, just like the code do it
        self.power_state_data = power_state_organize_all_data(self.power_state_dir)
        # the combined file for tests
        self.combined_file = combine_all_files_to_one_file(self.power_state_dir)

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        power_state_num_dates = len(self.power_state_data.data_dic)
        test_num_dates = count_num_dates(self.power_state_dir)

        self.assertEqual(power_state_num_dates, test_num_dates)
        self.assertEqual(power_state_num_dates, 7)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        power_state_num_hours = count_num_not_full_hours(self.power_state_data)   # without the hours that doesn't have file (i.e. all of this time was on)
        test_num_hours = count_num_hours(self.power_state_dir) - count_num_empty_files(self.power_state_dir)

        print('power_state_num_hours:', power_state_num_hours)
        print('test_num_hours:', test_num_hours)

        self.assertEqual(power_state_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_on_events and the sum_on_events_durations and the durations list collected well"""
        power_state_num_on_screen_event = count_num_data(self.power_state_data, NUM_TIMES)
        test_num_on_screen_event = count_num_strings_in_file(self.combined_file, 'Screen turned on', 'event')

        power_state_sum_on_screen_time = count_num_data(self.power_state_data, SUM_TIME)  # sum_on_screen_events()
        test_sum_on_screen_time, durations_list = sum_and_list_on_screen_events_in_file(self.combined_file)

        power_state_num_short_on_screen_time = count_num_data(self.power_state_data, SHORT_ON_TIME)
        test_num_short_on_screen_time = len([1 for duration in durations_list if datetime.timedelta(minutes=duration) < datetime.timedelta(seconds=COMMON_ON_TIME)])

        print('power_state_sum_on_screen_time: ', power_state_sum_on_screen_time)
        print('test_sum_on_screen_time:', test_sum_on_screen_time)

        self.assertEqual(power_state_num_on_screen_event, test_num_on_screen_event)
        self.assertEqual(round(power_state_sum_on_screen_time, 3), round(test_sum_on_screen_time, 3))
        self.assertEqual(power_state_num_short_on_screen_time, test_num_short_on_screen_time)

    def test_data_calculated_well(self):
        """Checks if the avg and std of num_out_texts and the num_in_texts calculated well for every day time"""
        # avr_and_sd_list order is: [avg_num_on_times_dt1, std_num_on_times_dt1, ...,
        #                            avg_num_on_times_dtN, std_num_on_times_dtN,
        #                            avg_sum_on_times_dt1, std_sum_on_times_dt1, ...,
        #                            avg_sum_on_times_dtN, std_sum_on_times_dtN,
        #                            avg_num_short_on_times_dt1, avg_percent_num_short_on_times_dt1, ...,
        #                            avg_num_short_on_times_dtN, avg_percent_num_short_on_times_dtN]
        titles_list, avr_and_sd_list = self.power_state_data.calc_calculations_on_dic(day_times, num_times=2)
        all_calculated_data_on_file = calc_avg_and_std_on_file(day_times, self.combined_file)

        power_state_avg_and_std_num_on_times = avr_and_sd_list[:len(avr_and_sd_list) // 3]
        test_avg_and_std_num_on_times = all_calculated_data_on_file[:len(all_calculated_data_on_file) // 3]

        power_state_avg_and_std_sum_on_times = avr_and_sd_list[len(avr_and_sd_list) // 3:2 * (len(avr_and_sd_list) // 3)]
        test_avg_and_std_sum_on_times = all_calculated_data_on_file[len(all_calculated_data_on_file) // 3:2 * (len(all_calculated_data_on_file) // 3)]

        print('power_state_avg_and_std_sum_on_times:', power_state_avg_and_std_sum_on_times)
        print('test_avg_and_std_sum_on_times:', test_avg_and_std_sum_on_times)

        power_state_avg_num_and_percent_short_on_times = avr_and_sd_list[2 * (len(avr_and_sd_list) // 3):]
        test_avg_num_and_percent_short_on_times = all_calculated_data_on_file[2 * (len(all_calculated_data_on_file) // 3):]

        print('power_state_avg_num_and_percent_short_on_times:', power_state_avg_num_and_percent_short_on_times)
        print('test_avg_num_and_percent_short_on_times:', test_avg_num_and_percent_short_on_times)

        self.assertEqual(len(power_state_avg_and_std_num_on_times), len(test_avg_and_std_num_on_times))
        self.assertEqual(len(power_state_avg_and_std_sum_on_times), len(test_avg_and_std_sum_on_times))
        self.assertEqual(len(power_state_avg_num_and_percent_short_on_times), len(test_avg_num_and_percent_short_on_times))
        self.assertEqual(list(np.round(np.array(power_state_avg_and_std_num_on_times), 3)),
                         list(np.round(np.array(test_avg_and_std_num_on_times), 3)))
        self.assertEqual(list(np.round(np.array(power_state_avg_and_std_sum_on_times), 2)),
                         list(np.round(np.array(test_avg_and_std_sum_on_times), 2)))
        self.assertEqual(list(np.round(np.array(power_state_avg_num_and_percent_short_on_times), 3)),
                         list(np.round(np.array(test_avg_num_and_percent_short_on_times), 3)))


if __name__ == '__main__':
    unittest.main()
