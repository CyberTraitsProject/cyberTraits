import math
import numpy as np
import pickle
from useful_functions import *
from questionnaires import questionnaires_main
from accelerometer import accelerometer_main
from power_state import power_state_main
from bluetooth import bluetooth_main
from wifi import wifi_main
from GPS import gps_main
from texts import texts_main
from calls import calls_main


def global_main(app_data_dir, candidate_dir_name, sensor):
	"""
	this is a global function, that call to the main of the sensor
	:param app_data_dir: the path the the app directory data
	:param candidate_dir_name: the path to the candidate directory data
	:param sensor: the sensor name we want to run on it
	:return: the returned data of the function its called to,
	in error state - returns 2 empty lists
	"""
	try:
		func_name = sensor + "_main"
		return globals()[func_name](os.path.join(app_data_dir, candidate_dir_name, sensor))
	except KeyError:
		print(f"No function name- {sensor}_main")
		return [], []


def create_csv_for_machine_learning(data_path, is_research=True):
	"""
	this method is main data processing method:
	it run of every candidate that has app & questionnaires data, and calls the main sensors functions,
	for getting its data for the machine learning.
	at the end, save all of the data (the X data), in a csv file (without the y data).
	:param is_research: if the current mode is "learn" or "predict"
	:param data_path: the path to the directory that in it we have all the data we need
	"""

	if is_research:
		# run the questionnaires code and read the questionnaires data it created
		questionnaires_main(os.path.join(data_path, "questionnaires"))
		questionnaires_info_file_path = 'questionnaires_info.pkl'
		check_if_file_exists(questionnaires_info_file_path)
		questionnaires_info_file = open(questionnaires_info_file_path, 'rb')
		questionnaires_info = pickle.load(questionnaires_info_file)
		questionnaires_info_file.close()

	# data_fields_list_for_machine_learning - will contain the titles of the data of the machine learning
	# the first title - candidate_id
	data_fields_list_for_machine_learning = ['candidate_id']

	# data_list_for_machine_learning - list of lists,
	# every list in it contains the data for the machine learning for every candidate
	data_list_for_machine_learning = []

	# the sensors we are taking to the machine learning
	sensors_names = ['power_state', 'calls', 'texts', 'accelerometer'] #, 'bluetooth', 'wifi', 'gps']

	if is_research:
		app_data_dir = os.path.join(data_path, "cyber_traits_data_edited")
	else:
		app_data_dir = data_path
	check_if_dir_exists(app_data_dir)

	# for adding the title (only in the first candidate)
	first_candidate = True

	# contains all of the candidates that have app data.
	# if the candidate has also questionnaires data, its value will be True, else False.
	candidates_dic = {}

	# pass on every candidate's directory
	# every directory contains number of directories, directory for every sensor
	# every sensor directory contains number of files, that contain data about this sensor, for every hour.
	for candidate_dir_name in os.listdir(app_data_dir):
		print(candidate_dir_name)

		if is_research:
			# calculate the data for the machine learning, only for the candidates that also have questionnaires info
			if candidate_dir_name not in questionnaires_info:
				print("The candidate", candidate_dir_name, "doesn't have questionnaires data")
				# the candidate doesn't have questionnaires data
				candidates_dic[candidate_dir_name] = False
				continue
			# this candidate have questionnaires data
			candidates_dic[candidate_dir_name] = True

		# the data for the machine learning for the current candidate
		curr_data_list_for_machine_learning = []

		# run on every sensor, and send to its main.
		# get two lists - sensor_titles_list:
		# the titles of the returned data,
		# analyzed_data_list: the analyzed data itself
		for sensor in sensors_names:
			sensor_titles_list, analyzed_data_list = global_main(app_data_dir, candidate_dir_name, sensor)
			# add the candidate's analyzed data, to all of the candidates data
			curr_data_list_for_machine_learning += analyzed_data_list
			# if it is the first candidates - add the sensor titles to the titles list
			if first_candidate:
				data_fields_list_for_machine_learning += sensor_titles_list

		# replace nan values to zeros
		# nan values returned when the candidate doesnt have one or more sensors data
		curr_data_list_for_machine_learning = [0 if math.isnan(x) else x for x in curr_data_list_for_machine_learning]

		# insert the candidate_id in the first cell (first column)
		curr_data_list_for_machine_learning.insert(0, candidate_dir_name)

		# add the data of this candidate to the big matrix
		data_list_for_machine_learning.append(curr_data_list_for_machine_learning)

		first_candidate = False

	# insert the titles of the data in the first line
	data_list_for_machine_learning.insert(0, data_fields_list_for_machine_learning)

	# convert to np array
	np_data_for_csv_file = np.array(data_list_for_machine_learning)

	# save the data in a csv file
	machine_learning_data_file = "machine_learning_data.csv"
	np.savetxt(machine_learning_data_file, np_data_for_csv_file, delimiter=',', fmt='%s')

	# save the list of the candidates in pickle file
	candidates_list_file = open('candidates_list.pkl', 'wb')
	pickle.dump(candidates_dic, candidates_list_file)
	candidates_list_file.close()


if __name__ == "__main__":
	create_csv_for_machine_learning(r"C:\Users\onaki\CyberTraits\cyberTraits")
