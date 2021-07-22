import enviromental_tournament
from tournament_adv import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from enviromental_tournament import *
from utility_and_viz import *
import numpy as np
import datetime


def n_groups_basic(number_groups):
    print(f'basic {number_groups} test')

    with open("test_data/random_stuff/exp/group_tests/time_taken.txt", "a") as file_object:
        file_object.write(f'basic {number_groups}  \n')

    save_file = []
    for i in range(20):
        print(f'round {i}, groups {number_groups}')
        tournament = enviromental_tournament.tournament(100)
        for n in range(number_groups):
            tournament.add_group(100)

        c_percent, scores, coop_total, time_taken = tournament.basic_tournament(no_rounds=1000, pop_size=100, percentage_kept=0.9)
        to_be_saved = tournament
        save_file.append(to_be_saved)
        
        with open("test_data/random_stuff/exp/group_tests/time_taken.txt", "a") as file_object:
            # Append 'hello' at the end of file
            file_object.write(f'{time_taken} \n')

    d_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    name = f'groups_basic_{number_groups}'
    f_name = d_time + name

    np.save(f'test_data/random_stuff/exp/group_tests/{f_name}', save_file)

for i in range(2,7):
    n_groups_basic(i)