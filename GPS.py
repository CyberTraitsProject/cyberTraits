"""
1. pass on the gps files and take the data for every day from the hours 9:00-18:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation -  SD (סטיית תקן). n=9*12=108

1. pass on the gps files and take the data for every day from the hours 18:00-00:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation(סטיית תקן). n=6*12=72

1. pass on the gps files and take the data for every day from the hours 00:00-9:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation(סטיית תקן). n=9*12=108

-------------------------------------------------------------------------------------------

to do average of SD's for the days, nights and evenings - 3 values.

"""

MIN_DISTANCE = 0.0000000001


"""
1. pass on the accelerometer files and take the data for every hour.
2. take the data of every 1 second. if we dont have information on specific time, we need to take the values 0, 0, 0.
3. calculate the MAD. n=60*60=3600

----------------------------------------------------

what we get:
MAD of every hour.

to do an average of every hour in the tested days - 24 values.

"""


import pandas as pd
import os
from date_time import *
import numpy as np


def get_distance(point_a, point_b):     # the accelerometer result in time i
    return pow((pow(point_a[0] - point_b[0], 2) + pow(point_a[1] - point_b[1], 2)+ pow(point_a[2] - point_b[2], 2), -2))   # ((x1-x2)^2 + (y1-y2)^2)^-2


def organize_data(path_dir, gps_file):

    gps_df = pd.read_csv(os.path.join(path_dir, gps_file), usecols=['UTC time', 'x', 'y', 'z'])

    latitude_list   = gps_df['latitude']
    longitude_list  = gps_df['longitude']
    altitude_list   = gps_df['altitude']
    UTC_times_list  = gps_df['UTC time']

    x_y_z_list_for_hour = []    # will contain 60*60 values, that every value is [x,y,z]

    """curr_line_index = 0
    curr_date_time = get_date_time_from_UTC_time(UTC_times_list[curr_line_index])
    for i in range(60):
        for j in range(60):
            if (curr_date_time.minute != i or curr_date_time.second != j) or curr_line_index + 1 == len(UTC_times_list):    # the curr time is more or little then the wanted time, or we finished all the lines in the file --> there is a need to fulfill the values with 0,0,0
                continue
            else:
                x_y_z_list_for_hour.append([x_list[curr_line_index], y_list[curr_line_index], z_list[curr_line_index]])
                while curr_date_time.minute == i and curr_date_time.second <= j and curr_line_index + 1 != len(UTC_times_list):
                    curr_line_index += 1
                    curr_date_time = get_date_time_from_UTC_time(UTC_times_list[curr_line_index])
    MAD = calculate_MAD(x_y_z_list_for_hour)
    accelerometer_data_dic[curr_date_time.hour].append(MAD)"""


def gps_main(gps_dir):
    if not os.path.isdir(gps_dir):
        print("Directory", gps_dir, "not exists")
        exit(1)
    for curr_gps_file in os.listdir(gps_dir):
        organize_data(gps_dir, curr_gps_file)
    return #calc_MAD_avg_for_hour()
