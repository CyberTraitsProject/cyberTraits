import unittest
from global_tests_functions import *
from texts import *

OUT = 1
IN = 0


def calc_avg_and_std_on_file(day_time, col_type, combined_file):
    """
    :param day_time: the day times to do the calculations on it
    :param col_type: the type of the col we wants to do calculations on it
    :param combined_file: the file with all of the data
    :return: the analyzed data in a list
    """
    texts_df = pd.read_csv(combined_file, usecols=['UTC time', 'sent vs received'])
    UTC_time_list = texts_df['UTC time']
    text_type_list = texts_df['sent vs received']

    # list of lists that will contain the data of every day time, data on every date
    data_list_for_all_day_times = [[] for c_day_time in day_time]

    counter_data_for_cur_date = [0 for c_day_time in day_time]
    p_date = ''
    for i, UTC_time in enumerate(UTC_time_list):
        cur_date = UTC_time.split('T')[0]
        cur_hour = (UTC_time.split('T')[1]).split(':')[0]

        if cur_date != p_date and p_date:
            # update the sum times the kind of the data appeared in this date
            for j, c_day_time in enumerate(day_time):
                data_list_for_all_day_times[j].append(counter_data_for_cur_date[j])
            counter_data_for_cur_date = [0 for c_day_time in day_time]
        p_date = cur_date

        if text_type_list[i] == col_type:
            counter_data_for_cur_date[get_day_time_index(cur_hour, day_time)] += 1

    # update the last date data
    for i, c_day_time in enumerate(day_time):
        data_list_for_all_day_times[i].append(counter_data_for_cur_date[i])

    avg_and_std_list = []
    for i, c_day_time in enumerate(day_time):
        avg_and_std_list.append(do_avg_on_list(data_list_for_all_day_times[i]))
        avg_and_std_list.append(do_std_on_list(data_list_for_all_day_times[i]))

    return avg_and_std_list


def texts_organize_all_data(texts_dir):
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(texts_dir)
    texts_data = Sensor_Data('texts')
    # pass on every file and send it to the organize_data function
    for curr_texts_file in os.listdir(texts_dir):
        organize_data(texts_dir, curr_texts_file, texts_data)

    return texts_data


class TextsTests(unittest.TestCase):

    def setUp(self):
        """
        kind of initialization function. run before every test/tests runs
        """
        # the path to the accelerometer data directory
        self.texts_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data_edited\ygpxrisr\texts'
        # the collected data, just like the code do it
        self.texts_data = texts_organize_all_data(self.texts_dir)
        # the combined file for tests
        self.combined_file = combine_all_files_to_one_file(self.texts_dir)

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        texts_num_dates = len(self.texts_data.data_dic)
        test_num_dates = count_num_dates(self.texts_dir)

        self.assertEqual(texts_num_dates, test_num_dates)
        self.assertEqual(texts_num_dates, NUM_TESTED_DATES)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        texts_num_hours = sum([len(self.texts_data.data_dic[date]) for date in self.texts_data.data_dic])
        test_num_hours = count_num_hours(self.texts_dir)

        self.assertEqual(texts_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_out_texts and the num_in_texts collected well"""
        texts_num_out_texts = count_num_data(self.texts_data, OUT)
        test_num_out_texts = count_num_strings_in_file(self.combined_file, 'sent SMS', 'sent vs received')

        texts_num_in_texts = count_num_data(self.texts_data, IN)
        test_num_in_texts = count_num_strings_in_file(self.combined_file, 'received SMS', 'sent vs received')

        self.assertEqual(texts_num_out_texts, test_num_out_texts)
        self.assertEqual(texts_num_in_texts, test_num_in_texts)

    def test_data_calculated_well(self):
        """Checks if the avg and std of num_out_texts and the num_in_texts calculated well for every day time"""
        # avr_and_sd_list order is: [avg_in_dt1, std_in_dt1, ..., avg_in_dtN, std_in_dtN,
        #                            avg_out_dt1, std_out_dt1, ..., avg_out_dtN, std_out_dtN]
        titles_list, avr_and_sd_list = self.texts_data.calc_calculations_on_dic(day_times, num_times=2)

        texts_avg_and_std_num_in_texts = avr_and_sd_list[:len(avr_and_sd_list)//2]
        test_avg_and_std_num_in_texts = calc_avg_and_std_on_file(day_times, 'received SMS', self.combined_file)

        texts_avg_and_std_num_out_texts = avr_and_sd_list[len(avr_and_sd_list)//2:]
        test_avg_and_std_num_out_texts = calc_avg_and_std_on_file(day_times, 'sent SMS', self.combined_file)

        print(np.round(np.array(texts_avg_and_std_num_in_texts), 4))
        print(np.round(np.array(test_avg_and_std_num_in_texts), 4))

        self.assertEqual(len(texts_avg_and_std_num_in_texts), len(test_avg_and_std_num_in_texts))
        self.assertEqual(len(texts_avg_and_std_num_out_texts), len(test_avg_and_std_num_out_texts))
        self.assertEqual(list(np.round(np.array(texts_avg_and_std_num_in_texts), 4)),
                         list(np.round(np.array(test_avg_and_std_num_in_texts), 4)))
        self.assertEqual(list(np.round(np.array(texts_avg_and_std_num_out_texts), 4)),
                         list(np.round(np.array(test_avg_and_std_num_out_texts), 4)))


if __name__ == '__main__':
    unittest.main()
