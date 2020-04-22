"""
1. pass on the texts files and take the data for every day.
2. count how many texts sent and how many texts received, in every day.
-------------------------------------------------------------------------------------------

do average of the number of the received texts - 1 value.
do average of the number of the sent texts - 1 value.
do std of the number of the received texts - 1 value.
do std of the number of the sent texts - 1 value.

TODO - if the texts file not exists - there is a problem with the number of the columns (it returns 2 columns and not 4)
"""

from sensor_data import Sensor_Data
from date_time import *
import os
import pandas as pd


def organize_data(path_dir, sensor_file, sensor_data):

    sensor_df = pd.read_csv(os.path.join(path_dir, sensor_file), usecols=['sent vs received'])
    sent_vs_received_list = sensor_df['sent vs received']
    date = get_date_from_file_name(sensor_file)
    hour = get_date_time_from_file_name(sensor_file).hour
    if date not in sensor_data.data_dic:
        sensor_data.data_dic[date] = {}
    num_received_texts = len([1 for text_type in sent_vs_received_list if text_type == 'received SMS'])
    num_sent_texts = len([1 for text_type in sent_vs_received_list if text_type == 'sent SMS'])
    sensor_data.data_dic[date][hour] = [num_received_texts, num_sent_texts]


def texts_main(texts_dir):

    texts_data = Sensor_Data('texts')
    if not os.path.isdir(texts_dir):
        print("Directory", texts_dir, "not exists")
        return texts_data.calc_avr_and_sd_on_dic(day_times_1)
    for curr_texts_file in os.listdir(texts_dir):
        organize_data(texts_dir, curr_texts_file, texts_data)
    print(texts_data)
    return texts_data.calc_avr_and_sd_on_dic(day_times_1, num_times=2)



texts_main(r'C:\Users\onaki\Downloads\data\75nqpmzi\texts')