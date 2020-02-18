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
from geopy.distance import distance # https://janakiev.com/blog/gps-points-distance-python/
import pandas as pd
import os
from date_time import *
import numpy as np

gps_data_dic = {}

def calc_avr_and_sd_on_dic():
    array_list = [[], [], []]  # [[night_distances], [day_distances], [evening_distances]]
    avr_and_sd_list = []
    titles_list = []

    # create 3 arrays, that every one includes all the distances in its day time
    for date in gps_data_dic:
        for i, day_time in enumerate(day_times):
            array_list[i].append(gps_data_dic[date][day_time])

    for i, day_time in enumerate(day_times):
        avr_and_sd_list.append(np.array(array_list[i]).mean())
        titles_list.append(f'distances_{day_time}_avg')

        avr_and_sd_list.append(np.array(array_list[i]).std())
        titles_list.append(f'distances_{day_time}_std')

    # print(array_list)
    # print(avr_and_sd_dic)
    return titles_list, avr_and_sd_list

def calc_distance_between_2_gps_points(coord1, coord2):
    return distance(coord1, coord2).m

def organize_data(path_dir, gps_file, prev_coord):

    gps_df = pd.read_csv(os.path.join(path_dir, gps_file), usecols=['UTC time', 'latitude', 'longitude', 'UTC time'])

    latitude_list   = gps_df['latitude']
    longitude_list  = gps_df['longitude']
    #altitude_list  = gps_df['altitude']
    UTC_times_list  = gps_df['UTC time']

    x_y_z_list_for_hour = []    # will contain 60*60 values, that every value is [x,y,z]
    file_date = str(gps_file).split(" ")[0]
    if file_date not in gps_data_dic:
        gps_data_dic[file_date] = {day_times[NIGHT]:   0,   # the distance in meters he passed in day time night
                                   day_times[DAY]:     0,   # the distance in meters he passed in day time day
                                   day_times[EVENING]: 0}   # the distance in meters he passed in day time evening

    for i, UTC_time in enumerate(UTC_times_list):

        if prev_coord:
            coord1 = prev_coord
            coord2 = (latitude_list[i], longitude_list[i])
            distance = calc_distance_between_2_gps_points(coord1, coord2)  # the distance in meters
            day_time = get_part_of_day(get_date_time_from_UTC_time(UTC_time))   # if the day time change, the distance will add to the next day time
            prev_coord = None

            gps_data_dic[file_date][day_time] += distance

        if i == len(UTC_times_list) - 1:    # last row
            return (latitude_list[i], longitude_list[i])

        coord1 = (latitude_list[i], longitude_list[i])
        coord2 = (latitude_list[i + 1], longitude_list[i + 1])
        distance = calc_distance_between_2_gps_points(coord1, coord2)   # the distance in meters
        day_time = get_part_of_day(get_date_time_from_UTC_time(UTC_time))
        gps_data_dic[file_date][day_time] += distance


def gps_main(gps_dir):

    # for cleaning the previous data
    global gps_data_dic
    gps_data_dic = {}
    print('----------gps dic-----------', gps_data_dic)
    if not os.path.isdir(gps_dir):
        print("Directory", gps_dir, "not exists")
        return calc_avr_and_sd_on_dic()
    returned_value = None
    for curr_gps_file in os.listdir(gps_dir):
        last_coord = organize_data(gps_dir, curr_gps_file, returned_value)
        returned_value = last_coord
    # print(gps_data_dic)
    return calc_avr_and_sd_on_dic()
