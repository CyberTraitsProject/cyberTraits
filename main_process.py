import os
import math
from accelerometer import accelerometer_main
from power_state import power_state_main
from bluetooth import bluetooth_main
from wifi import wifi_main
from GPS import gps_main
from questionnaires import questionnaires_main
import numpy as np
from machine_learning_model import machine_learning_model_main


def global_main(app_data_dir, candidate_dir_name, sensor):
	try:
		func_name = sensor + "_main"
		return globals()[func_name](os.path.join(app_data_dir, candidate_dir_name, sensor))
	except KeyError:
		print(f"No function name- {sensor}_main")
		return [], []
	#func_name(os.path.join(app_data_dir, candidate_dir_name, sensor))

def create_csv_for_machine_learning(data_path, trait_name):

	questionnaires_info = questionnaires_main(os.path.join(data_path, "questionnaires"))
	traits_list = [*questionnaires_info['1q9fj13m']]

	if trait_name not in traits_list:
		print("The trait", trait_name, 'not found in the trait list')
		exit(1)
		
	data_fields_list_for_machine_learning = ['candidate_id']

	sensors_names = ['accelerometer', 'power_state', 'bluetooth', 'wifi', 'gps']

	# print(data_fields_list_for_machine_learning)
	data_list_for_machine_learning = []
	app_data_dir = os.path.join(data_path, "data")

	first_candidate = True

	for candidate_dir_name in os.listdir(app_data_dir):
		print(candidate_dir_name)
		curr_data_list_for_machine_learning = []

		for sensor in sensors_names:
			sensor_titles_list, analayzed_data_list = global_main(app_data_dir, candidate_dir_name, sensor)
			curr_data_list_for_machine_learning += analayzed_data_list
			if first_candidate:
				data_fields_list_for_machine_learning += sensor_titles_list
		if first_candidate:
			# the data from the questionnaires
			data_fields_list_for_machine_learning.append(trait_name)
		curr_data_list_for_machine_learning += [questionnaires_info[candidate_dir_name][trait_name]]

		# replace nan values to zeros
		# nan values returned when the candidate doesnt have one or more sensors data
		curr_data_list_for_machine_learning = [0 if math.isnan(x) else x for x in curr_data_list_for_machine_learning]

		curr_data_list_for_machine_learning.insert(0, candidate_dir_name)

		data_list_for_machine_learning.append(curr_data_list_for_machine_learning)

		first_candidate = False
	print(data_list_for_machine_learning)
	print(data_fields_list_for_machine_learning)

	data_list_for_machine_learning.insert(0, data_fields_list_for_machine_learning)
	# print(len(data_fields_list_for_machine_learning), len(data_list_for_machine_learning[0]))
	np_data_for_csv_file = np.array(data_list_for_machine_learning)

	# np_data_for_csv_file = np.nan_to_num(np_data_for_csv_file)
	print('-----------------------------------------------------------------------------------------')
	print(np_data_for_csv_file)

	machine_learning_data_path = os.path.join(data_path, "machine_learning_data.csv")
	np.savetxt(machine_learning_data_path, np_data_for_csv_file, delimiter=',', fmt='%s')

	#machine_learning_model_main(machine_learning_data_path, trait_name)

if __name__ == "__main__":
	create_csv_for_machine_learning(r"C:\Users\onaki\CyberTraits\cyberTraits", "Secure")
	#print(global_main(r"C:\Users\onaki\CyberTraits\cyberTraits", "123", 'wifi'))
