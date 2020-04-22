"""
1. pass on the calls files and take the data for every day.
2. count how many outgoing calls and how many incoming calls, in every day.
-------------------------------------------------------------------------------------------

do average of the number of the outgoing calls and incoming calls - 2 values.
do std of the number of the outgoing calls and incoming calls - 2 values.
do common of number of the outgoing calls and incoming calls - 2 values.
do median of number of the outgoing calls and incoming calls - 2 values.

TODO - if the calls file does not exists - there is a problem with the number of the columns (it returns 2 columns and not 4)
"""

from sensor_data import Sensor_Data
from date_time import *
import os
import pandas as pd


def organize_data(path_dir, sensor_file, sensor_data):
    sensor_df = pd.read_csv(os.path.join(path_dir, sensor_file), usecols=['hashed phone number',
                                                                          'call type', 'duration in seconds'])
    # first step:
    # to calc the avg, std, median, common on the number of outgoing and incoming calls
    sent_vs_received_list = sensor_df['call type']
    durations_list = sensor_df['duration in seconds']
    print(type(list(durations_list)))
    date = get_date_from_file_name(sensor_file)
    hour = get_date_time_from_file_name(sensor_file).hour
    if date not in sensor_data.data_dic:
        sensor_data.data_dic[date] = {}

    num_incoming_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Incoming Call'])
    num_outgoing_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Outgoing Call'])
    num_missed_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Missed Call'])
    num_outgoing_0_calls = len([1 for i, text_type in enumerate(sent_vs_received_list) if text_type == 'Outgoing Call' and durations_list[i] == 0])

    sensor_data.data_dic[date][hour] = [num_incoming_calls, num_outgoing_calls, num_missed_calls, num_outgoing_0_calls, list(durations_list)]
    print(num_outgoing_0_calls)

def calls_main(texts_dir):
    texts_data = Sensor_Data('calls')
    if not os.path.isdir(texts_dir):
        print("Directory", texts_dir, "not exists")
        return texts_data.calc_avr_and_sd_on_dic(day_times_1)
    for curr_texts_file in os.listdir(texts_dir):
        organize_data(texts_dir, curr_texts_file, texts_data)
    print(texts_data)
    return texts_data.calc_avr_and_sd_on_dic(day_times_1, num_times=2, calc_median=True, calc_common=True)


calls_main(r'C:\Users\onaki\Downloads\data\2yct4nu4\calls')