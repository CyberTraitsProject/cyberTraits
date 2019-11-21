import os
from accelerometer import accelerometer_main
from power_state import power_state_main
from bluetooth import bluetooth_main
from wifi import wifi_main
from questionnaires import questionnaires_main

if __name__ == "__main__":
    path = "C:/Users/orana/PycharmProjects/project"
    questionnaires_info = questionnaires_main(os.path.join(path, "questionnaires"))
    traits_list = [*questionnaires_info['1q9fj13m']]
    data_fields_list_for_machine_learning = ['Candidate ID'] + traits_list + ['avg_num_times_night_accelerometer', 'avg_num_times_day_accelerometer', 'avg_num_times_evening_accelerometer',
                                                                              'avg_sum_times_night_accelerometer', 'avg_sum_times_day_accelerometer', 'avg_sum_times_evening_accelerometer',
                                                                              'std_num_times_night_accelerometer', 'std_num_times_day_accelerometer', 'std_num_times_evening_accelerometer',
                                                                              'std_sum_times_night_accelerometer', 'std_sum_times_day_accelerometer', 'std_sum_times_evening_accelerometer']

    print(data_fields_list_for_machine_learning)
    data_list_for_machine_learning = []
    app_data_dir = os.join(path, "data")

    for candidate_dir in os.path.listdir(app_data_dir):
        avr_and_sd_dic_accelerometer = accelerometer_main(os.join(app_data_dir, 'accelerometer'))
        avr_and_sd_dic_power_state = power_state_main(os.join(app_data_dir, 'power_state'))
        avr_and_sd_dic_bluetooth = bluetooth_main(os.join(app_data_dir, 'bluetooth'))
        avr_and_sd_dic_wifi = wifi_main(os.join(app_data_dir, 'wifi'))


        pass