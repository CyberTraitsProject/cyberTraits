import os
from accelerometer import accelerometer_main
from power_state import power_state_main
from bluetooth import bluetooth_main
from wifi import wifi_main
from questionnaires import questionnaires_main
import numpy as np

def create_csv_for_machine_learning(data_path, trait_name):

	questionnaires_info = questionnaires_main(os.path.join(data_path, "questionnaires"))
	traits_list = [*questionnaires_info['1q9fj13m']]

	if trait_name not in traits_list:
		print("The trait", trait_name, 'not found in the trait list')
		exit(1)
		
	data_fields_list_for_machine_learning = ['candidate_id']
	
	#print(data_fields_list_for_machine_learning)
	data_list_for_machine_learning = []
	app_data_dir = os.path.join(data_path, "data")

	for candidate_dir in os.listdir(app_data_dir):

		curr_data_list_for_machine_learning = []
		
		curr_data_list_for_machine_learning.append(candidate_dir)
	
		accelerometer_titles_list, avr_MAD_list = accelerometer_main(os.path.join(app_data_dir, candidate_dir, 'accelerometer'))
		curr_data_list_for_machine_learning += avr_MAD_list
		data_fields_list_for_machine_learning += accelerometer_titles_list
		
		power_state_titles_list, power_state_avr_and_sd_list = power_state_main(os.path.join(app_data_dir, candidate_dir, 'power_state'))
		curr_data_list_for_machine_learning += power_state_avr_and_sd_list
		data_fields_list_for_machine_learning += power_state_titles_list
		
		"""bluetooth_titles_list, bluetooth_avr_and_sd_list = bluetooth_main(os.path.join(app_data_dir, candidate_dir, 'bluetooth'))
		curr_data_list_for_machine_learning += bluetooth_avr_and_sd_list
		data_fields_list_for_machine_learning += bluetooth_titles_list"""
		
		wifi_titles_list, wifi_avr_and_sd_list = wifi_main(os.path.join(app_data_dir, candidate_dir, 'wifi'))
		curr_data_list_for_machine_learning += wifi_avr_and_sd_list
		data_fields_list_for_machine_learning += wifi_titles_list
		
		
		# the data from the questionnaires
		data_fields_list_for_machine_learning.append(trait_name)
		curr_data_list_for_machine_learning += [questionnaires_info[candidate_dir][trait_name]]
		
		data_list_for_machine_learning.append(curr_data_list_for_machine_learning)

	print(len(data_fields_list_for_machine_learning), len(data_list_for_machine_learning[0]))
	nparray1 = np.array([data_fields_list_for_machine_learning, data_list_for_machine_learning[0]])
	print(nparray1)
	np.savetxt(os.path.join(data_path, "machine_learning_data.csv"), nparray1, delimiter=',', fmt='%s')


if __name__ == "__main__":
	create_csv_for_machine_learning("C:/Users/yafitsn/PycharmProjects/project", "Secure")
