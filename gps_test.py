from geopy.distance import distance # https://janakiev.com/blog/gps-points-distance-python/
import pandas as pd
import os
from date_time import *
from statistics import mean, stdev
import numpy as np

gps_data_dic = {}

def calc_distance_between_2_gps_points(coord1, coord2):
    return distance(coord1, coord2).m

if __name__ == "__main__":
    f = open("C:/Users/yafits/PycharmProjects/cyberTraits/data/1q9fj13m/gps_test/sum.csv")
    f.readline()
    prev_UTC_time = prev_lat = prev_lon = None
    for line in f.readlines():
        if not prev_UTC_time:
            prev_UTC_time = line.split(",")[1]
            prev_lat = line.split(",")[2]
            prev_lon = line.split(",")[3]
            continue
        cur_UTC_time = line.split(",")[1]
        cur_lat = line.split(",")[2]
        cur_lon = line.split(",")[3]

        prev_day_time = get_part_of_day(get_date_time_from_UTC_time(prev_UTC_time))
        cur_day_time = get_part_of_day(get_date_time_from_UTC_time(cur_UTC_time))

        dis = calc_distance_between_2_gps_points((prev_lat, prev_lon), (cur_lat, cur_lon))

        print(dis, cur_day_time)

        cur_date = cur_UTC_time.split("T")[0]

        if cur_date not in gps_data_dic:
            gps_data_dic[cur_date] = {  day_times[NIGHT]: 0,  # the distance in meters he passed in day time night
                                        day_times[DAY]: 0,  # the distance in meters he passed in day time day
                                        day_times[EVENING]: 0}  # the distance in meters he passed in day time evening

        gps_data_dic[cur_date][cur_day_time] += dis

        prev_UTC_time = cur_UTC_time
        prev_lat = cur_lat
        prev_lon = cur_lon

    print(gps_data_dic)

    for day_time in day_times:
        arr = []
        for date in gps_data_dic:
            arr.append(gps_data_dic[date][day_time])
        print("std_", day_time, ":", np.array(arr).std())
        print("average_", day_time, ":", np.array(arr).mean())

