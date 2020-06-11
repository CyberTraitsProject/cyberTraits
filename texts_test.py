import unittest
from global_tests_functions import *
from texts import *

# the path to the accelerometer data directory
texts_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data\2ppn81sa\texts'

OUT = 1
IN = 0


def texts_organize_all_data():
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(texts_dir)
    texts_data = Sensor_Data('texts')
    # pass on every file and send it to the organize_data function
    for curr_texts_file in os.listdir(texts_dir):
        organize_data(texts_dir, curr_texts_file, texts_data)

    return texts_data


# the collected data, just like the code do it
texts_data = texts_organize_all_data()


class TextsTests(unittest.TestCase):

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        texts_num_dates = len(texts_data.data_dic)
        test_num_dates = count_num_dates(texts_dir)

        self.assertEqual(texts_num_dates, test_num_dates)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        texts_num_hours = sum([len(texts_data.data_dic[date]) for date in texts_data.data_dic])
        test_num_hours = count_num_hours(texts_dir)

        self.assertEqual(texts_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the num_out_texts and the num_in_texts collected well"""
        combined_file = combine_all_files_to_one_file(texts_dir)

        texts_num_out_texts = count_num_data(texts_data, OUT)
        test_num_out_texts = count_num_strings_in_file(combined_file, 'sent SMS', 'sent vs received')

        texts_num_in_texts = count_num_data(texts_data, IN)
        test_num_in_texts = count_num_strings_in_file(combined_file, 'received SMS', 'sent vs received')

        self.assertEqual(texts_num_out_texts, test_num_out_texts)
        self.assertEqual(texts_num_in_texts, test_num_in_texts)


if __name__ == '__main__':
    unittest.main()
