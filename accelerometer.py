import pandas as pd
from date_time import *
from sensor_data import *


def organize_data(path_dir, accelerometer_file, accelerometer_data):
    """
    pass on the accelerometer_file - this file contains accelerometer data on specific date on specific hour.
    the name of the file is the date and the hour.
    the file contains data in this shape: [timestamp, UTC time, accuracy, x, y, z]
    the function add its data to the sensor dictionary-
    collect the x, y, z data of every second, and put this list in the dictionary, in this date and hour.
    :param path_dir: the path to the directory the sensor data found there
    :param accelerometer_file: the name of the file to organize
    :param accelerometer_data: the global sensor data dictionary
    """

    full_path_accelerometer_file = os.path.join(path_dir, accelerometer_file)
    check_if_file_exists(full_path_accelerometer_file)

    accelerometer_df = pd.read_csv(full_path_accelerometer_file, usecols=['UTC time', 'x', 'y', 'z'])
    x_list = accelerometer_df['x']
    y_list = accelerometer_df['y']
    z_list = accelerometer_df['z']
    UTC_times_list = accelerometer_df['UTC time']

    # will contain 60*60 values (for every second), that every value is [x,y,z]
    x_y_z_list_for_hour = []

    # the previous line data
    p_min = p_sec = curr_date_time = ""

    # pass on every x,y,z data, and if we still not added this time (minute + second) to the x,y,z lists,
    # we will add it
    for i in range(len(UTC_times_list)):
        curr_date_time = get_date_time_from_UTC_time(UTC_times_list[i])
        c_min = curr_date_time.minute
        c_sec = curr_date_time.second

        # this minute and second weren't found before --> add the x,y,z values to the list
        if c_min != p_min or c_sec != p_sec:
            x_y_z_list_for_hour.append([x_list[i], y_list[i], z_list[i]])
            # update the last minute and second that we added its x,y,z values
            p_min = c_min
            p_sec = c_sec

    # get the date and the hour
    date = get_date_from_file_name(accelerometer_file)
    hour = get_hour_from_file_name(accelerometer_file)

    # if it is a new date -> add it to the dictionary
    if date not in accelerometer_data.data_dic:
        accelerometer_data.data_dic[date] = {}

    # add the x_y_z_list to the dictionary in the specific date and hour
    accelerometer_data.data_dic[date][hour] = x_y_z_list_for_hour


def accelerometer_main(accelerometer_dir):
    """
    create an instance of Sensor_Data, pass on all of the accelerometer data file,
    organize them and do the calculations of this data.
    :param accelerometer_dir: the directory that the accelerometer data files found there
    :return: the calculated data in 2 lists - the calculated data and its titles
    """

    check_if_dir_exists(accelerometer_dir)

    accelerometer_data = Sensor_Data('accelerometer')

    # pass on every file and send it to the organize_data function
    for curr_accelerometer_file in os.listdir(accelerometer_dir):
        organize_data(accelerometer_dir, curr_accelerometer_file, accelerometer_data)

    # send the data to the calculation function, and return the calculated data + its titles
    return accelerometer_data.calc_calculations_on_dic(day_times)


if __name__ == '__main__':
    accelerometer_main(r'C:\Users\onaki\CyberTraits\cyberTraits\acc_dt')
