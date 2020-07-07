from sensor_data import Sensor_Data
from date_time import *
import pandas as pd
from useful_functions import *


def organize_data(path_dir, texts_file, texts_data):
    """
    pass on the sensor_file - this file contains texts data on specific date on specific hour.
    the name of the file is the date and the hour.
    the file contains data in this shape: [timestamp, UTC time, hashed phone number, sent vs received, message length, time sent]
    the function add its data to the sensor dictionary-
    count how much sent texts and received texts there are in this hour.
    :param path_dir: the path to the directory the sensor data found there
    :param texts_file: the name of the file to organize
    :param texts_data: the global sensor data dictionary
    """

    full_path_texts_file = os.path.join(path_dir, texts_file)
    check_if_file_exists(full_path_texts_file)

    sensor_df = pd.read_csv(full_path_texts_file, usecols=['sent vs received'])
    sent_vs_received_list = sensor_df['sent vs received']
    date = get_date_from_file_name(texts_file)
    hour = get_date_time_from_file_name(texts_file).hour

    # if it is a new date -> add it to the dictionary
    if date not in texts_data.data_dic:
        texts_data.data_dic[date] = {}

    # count how much received texts there are
    num_received_texts = len([1 for text_type in sent_vs_received_list if text_type == 'received SMS'])

    # count how much sent texts there are
    num_sent_texts = len([1 for text_type in sent_vs_received_list if text_type == 'sent SMS'])

    # add the counts to the data on this date and this hour
    texts_data.data_dic[date][hour] = [num_received_texts, num_sent_texts]


def texts_main(texts_dir):
    """
    create an instance of Sensor_Data, pass on all of the texts data file,
    organize them and do the calculations of this data.
    :param texts_dir: the directory that the texts data files found there
    :return: the calculated data in 2 lists - the calculated data and its titles
    """

    check_if_dir_exists(texts_dir)

    texts_data = Sensor_Data('texts')

    # pass on every file and send it to the organize_data function
    for curr_texts_file in os.listdir(texts_dir):
        organize_data(texts_dir, curr_texts_file, texts_data)

    # send the data to the calculation function, and return the calculated data + its titles
    # num_times=2, because the data contains two inputs - num sent texts and num received texts
    return texts_data.calc_calculations_on_dic(day_times, num_times=2)


if __name__ == '__name__':
    texts_main(r'C:\Users\onaki\Downloads\data\75nqpmzi\texts')
