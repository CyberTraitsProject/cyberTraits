import datetime

# kinds of day times:
# ===================
day_times_1 = {
    'all_day': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
}
day_times_3 = {
    'night':    [0, 1, 2, 3, 4, 5, 6, 7, 8],
    'day':      [9, 10, 11, 12, 13, 14, 15, 16, 17],
    'evening':  [18, 19, 20, 21, 22, 23]
}
day_time_4 = {  # TODO - to fill this value

}
day_times_24 = {
    '0':    [0],
    '1':    [1],
    '2':    [2],
    '3':    [3],
    '4':    [4],
    '5':    [5],
    '6':    [6],
    '7':    [7],
    '8':    [8],
    '9':    [9],
    '10':   [10],
    '11':   [11],
    '12':   [12],
    '13':   [13],
    '14':   [14],
    '15':   [15],
    '16':   [16],
    '17':   [17],
    '18':   [18],
    '19':   [19],
    '20':   [20],
    '21':   [21],
    '22':   [22],
    '23':   [23],
}

ON = "Screen turned on"
OFF = "Screen turned off"
POWER_ON = "Power connected"
POWER_OFF = "Power disconnected"
SHUTDOWN = "Device shut down signal received"
REBOOT = "Device reboot signal received"
POWER_SAVE = "Power Save Mode state change signal received; device in power save state."
POWER_UNSAVED = "Power Save Mode change signal received; device not in power save state."
IDLE = "Device Idle (Doze) state change signal received; device in idle state."
NOT_IDLE = "Device Idle (Doze) state change signal received; device not in idle state."

day_times = day_times_3

NUM_TESTED_DATES = 7


def get_date_time_from_UTC_time(str):
    """
    :param str: string that symbol UTC time
    :return: the time, in date time variable
    """
    return datetime.datetime.strptime(str, '%Y-%m-%dT%H:%M:%S.%f')


def get_date_time_from_file_name(str):
    """
    :param str: file name that contain UTC time
    :return: the time, in date time variable
    """
    return datetime.datetime.strptime(str, '%Y-%m-%d %H_%M_%S.csv')


def get_date_from_file_name(file_name):
    """
    :param file_name: file name, that contains UTC time
    :return: the date of the UTC time, in string variable
    """
    return file_name.split(' ')[0]


def get_hour_from_file_name(file_name):
    """
    :param file_name: file name, that contains UTC time. format for example - "2020-04-21 07_00_00.csv"
    :return: the date of the UTC time, in string variable
    """
    return int((file_name.split(' ')[1]).split('_')[0])


def check_day_time_structure(day_times):
    """
    :param day_times: the structure of te day_times
    :return: through exception if the day times include more that 24 hours
    """
    # how much hours we have in all of the day times
    num_hours = len([len(hours) for day_time, hours in day_times.items()])
    if num_hours > 24:
        raise Exception('ERROR: You have hours more that 24 hours. Please choose hours between 0-23.')
