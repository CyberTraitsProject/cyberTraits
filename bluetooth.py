"""
1. pass on the bluetooth files and take the data for every day from the hours 9:00-18:00.
2. count the number of the different hashed MAC (into dictionary).

1. pass on the bluetooth files and take the data for every day from the hours 18:00-00:00.
2. count the number of the different hashed MAC (into dictionary).

1. pass on the bluetooth files and take the data for every day from the hours 00:00-9:00.
2. count the number of the different hashed MAC (into dictionary).

-------------------------------------------------------------------------------------------

to do average of the counts of days, nights and evenings - 3 values.
to take the SD's of the counts of days, nights and evenings - 3 values.

"""

from wifi_bluetooth import *
from sensor_data import Sensor_Data

bluetooth_data_dic = {}

def bluetooth_main(bluetooth_dir):

    '''# for cleaning the previous data
    global bluetooth_data_dic
    bluetooth_data_dic = {}'''

    bluetooth_data = Sensor_Data('bluetooth')

    if not os.path.isdir(bluetooth_dir):
        print("Directory", bluetooth_dir, "not exists")
        return bluetooth_data.calc_avr_and_sd_on_dic(day_times_3)
    for curr_bluetooth_file in os.listdir(bluetooth_dir):
        organize_data(bluetooth_dir, curr_bluetooth_file, bluetooth_data)
    return bluetooth_data.calc_avr_and_sd_on_dic(day_times_3)
    #print(wifi_data_dic)
