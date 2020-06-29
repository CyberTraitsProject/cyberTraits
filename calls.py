from sensor_data import *
from date_time import *
from useful_functions import *
import pandas as pd


def organize_data(path_dir, calls_file, calls_data):
    """
    pass on the sensor_file - this file contains texts data on specific date on specific hour.
    the name of the file is the date and the hour.
    the file contains data in this shape: [timestamp, UTC time, hashed phone number, call type, duration in seconds]
    the function add its data to the sensor dictionary-
    count how much outgoing calls, incoming calls, missed calls, outgoing calls with duration 0,
    duration time list, duration time he talked with each phone number - there are in this hour.
    :param path_dir: the path to the directory the sensor data found there
    :param calls_file: the name of the file to organize
    :param calls_data: the global sensor data dictionary
    """

    full_path_calls_file = os.path.join(path_dir, calls_file)
    check_if_file_exists(full_path_calls_file)

    sensor_df = pd.read_csv(full_path_calls_file, usecols=['hashed phone number',
                                                           'call type', 'duration in seconds'])
    hashed_phone_number_list = sensor_df['hashed phone number']
    sent_vs_received_list = sensor_df['call type']
    durations_list = sensor_df['duration in seconds']
    date = get_date_from_file_name(calls_file)
    hour = get_date_time_from_file_name(calls_file).hour

    # if it is a new date -> add it to the dictionary
    if date not in calls_data.data_dic:
        calls_data.data_dic[date] = {}

    # count how much incoming calls there are
    num_incoming_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Incoming Call'])

    # count how much outgoing calls there are
    num_outgoing_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Outgoing Call'])

    # count how much missed calls there are
    num_missed_calls = len([1 for text_type in sent_vs_received_list if text_type == 'Missed Call'])

    # count how much outgoing calls with duration 0 there are
    num_outgoing_0_calls = len([1 for i, text_type in enumerate(sent_vs_received_list) if text_type == 'Outgoing Call' and durations_list[i] == 0])

    # will contain for every phone number, how much time he talked with it.
    # {hashed_phone_number1 : calls_duration, hashed_phone_number2 : calls_duration, ...}
    phones_numbers_dic = collections.Counter()
    for i, phone_number in enumerate(hashed_phone_number_list):
        phones_numbers_dic[phone_number] += durations_list[i]

    # add the collected data to the dictionary on this date and this hour
    calls_data.data_dic[date][hour] = [num_incoming_calls, num_outgoing_calls, num_missed_calls, num_outgoing_0_calls, list(durations_list), collections.Counter(phones_numbers_dic)]


def calls_main(calls_dir):
    """
    create an instance of Sensor_Data, pass on all of the calls data file,
    organize them and do the calculations of this data.
    :param calls_dir: the directory that the calls data files found there
    :return: the calculated data in 2 lists - the calculated data and its titles
    """

    check_if_dir_exists(calls_dir)

    calls_data = Sensor_Data('calls')

    # pass on every file and send it to the organize_data function
    for curr_texts_file in os.listdir(calls_dir):
        organize_data(calls_dir, curr_texts_file, calls_data)

    # send the data to the calculation function, and return the calculated data + its titles
    # num_times=2, because the data contains two inputs that we need to calculate
    # avg, std, median and common on them- num incoming calls and num outgoing calls
    return calls_data.calc_calculations_on_dic(day_times, num_times=2, calc_median=True, calc_common=True)


if __name__ == '__main__':
    calls_main(r'C:\Users\onaki\CyberTraits\cyberTraits\data\1q9fj13m\calls')
