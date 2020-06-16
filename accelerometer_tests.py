import unittest
from global_tests_functions import *
from accelerometer import *

# the path to the accelerometer data directory
accelerometer_dir = r'C:\Users\onaki\CyberTraits\cyberTraits\cyber_traits_data\2ppn81sa\accelerometer'
# the combined file for tests
combined_file = combine_all_files_to_one_file(accelerometer_dir)


def collect_all_xyz_lists():
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


def collect_xyz_from_file():
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


def accelerometer_organize_all_data():
    """
    :return: the sensor data, just like the code do it
    """
    check_if_dir_exists(accelerometer_dir)
    accelerometer_data = Sensor_Data('accelerometer')
    # pass on every file and send it to the organize_data function
    for curr_accelerometer_file in os.listdir(accelerometer_dir):
        organize_data(accelerometer_dir, curr_accelerometer_file, accelerometer_data)

    return accelerometer_data


# the collected data, just like the code do it
accelerometer_data = accelerometer_organize_all_data()


class AccelerometerTests(unittest.TestCase):

    def test_number_of_dates(self):
        """Checks if the number of the dates we collected is true"""
        accelerometer_num_dates = len(accelerometer_data.data_dic)
        test_num_dates = count_num_dates(accelerometer_dir)

        self.assertEqual(accelerometer_num_dates, test_num_dates)

    def test_number_of_hours(self):
        """Checks if the number of the hours we collected is true"""
        accelerometer_num_hours = sum([len(accelerometer_data.data_dic[date]) for date in accelerometer_data.data_dic])
        test_num_hours = count_num_hours(accelerometer_dir)

        self.assertEqual(accelerometer_num_hours, test_num_hours)

    def test_data_collected_well(self):
        """Checks if the xyz data collected well"""
        accelerometer_x_y_z_list = collect_all_xyz_lists()
        test_x_y_z_list = collect_xyz_from_file()

        self.assertEqual(len(accelerometer_x_y_z_list), len(test_x_y_z_list))
        self.assertEqual(round_list(accelerometer_x_y_z_list), round_list(test_x_y_z_list))


if __name__ == '__main__':
    unittest.main()
