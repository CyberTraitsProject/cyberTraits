"""
1. pass on the wifi files and take the data for every day from the hours 9:00-18:00.
2. count the number of the different hashed MAC (into dictionary).

1. pass on the wifi files and take the data for every day from the hours 18:00-00:00.
2. count the number of the different hashed MAC (into dictionary).

1. pass on the wifi files and take the data for every day from the hours 00:00-9:00.
2. count the number of the different hashed MAC (into dictionary).

-------------------------------------------------------------------------------------------

to do average of the counts of days, nights and evenings - 3 values.
to take the SD's of the counts of days, nights and evenings - 3 values.

"""
from wifi_bluetooth import *
from sensor_data import Sensor_Data

#wifi_data_dic = {}


def wifi_main(wifi_dir):

    # for cleaning the previous data
    '''global wifi_data_dic
    wifi_data_dic = {}'''

    wifi_data = Sensor_Data('wifi')
    if not os.path.isdir(wifi_dir):
        print("Directory", wifi_dir, "not exists")
        return wifi_data.calc_avr_and_sd_on_dic(day_times_3)
    for curr_wifi_file in os.listdir(wifi_dir):
        organize_data(wifi_dir, curr_wifi_file, wifi_data)
    print(wifi_data)
    return wifi_data.calc_avr_and_sd_on_dic(day_times_3)
    #print(wifi_data_dic)

# print(wifi_main('abc'))