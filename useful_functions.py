import os


def check_if_file_exists(file):
    """
    :param file: the file we want to open
    :return: exit(1) if the file doesn't exist
    """
    if not os.path.isfile(file):
        print("File '", file, "' does not exist")
        exit(1)


def check_if_dir_exists(dir):
    """
    :param dir: the directory we want to read a file from
    :return: exit(1) if the directory doesn't exist
    """
    if not os.path.isdir(dir):
        print("Directory '", dir, "' does not exist")
        exit(1)


def safe_arr_divide(arr1, arr2):
    """
    return the safe derivation of the array - if the second value is 0, change it to 1
    :param arr1: the first array
    :param arr2: the second array
    :return: arr1 / arr2
    """
    # the arrays must have the same length
    if len(arr1) != len(arr2):
        exit(1)
    for i, num in enumerate(arr2):
        # if the second value is 0 --> the first value must be 0 (it is percent, so the second must be bigger
        # than the first)
        if num == 0:
            if arr1[i] != 0:
                exit(1)
            # put 1 in the second value (the result will be 0, because the first value is 0)
            arr2[i] = 1
    return arr1 / arr2
