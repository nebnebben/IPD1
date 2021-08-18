import enviromental_tournament
from tournament_adv import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from enviromental_tournament import *
from utility_and_viz import *
import numpy as np
import datetime


def n_groups_basic(number_groups, save_ind, group_size, exp_repeat=20, no_rounds=1000, env_size=100, file_path=None,
                   start_ind=0, location_update_frequency=10):
    print(f'basic groups_{number_groups} size_{group_size} no_rounds_{no_rounds}')

    if not file_path:
        file_path = 'test_data/random_stuff/exp/group_tests'

    with open(f"{file_path}/time_taken.txt", "a") as file_object:
        file_object.write(f'basic groups_{number_groups} size_{group_size}  no_rounds_{no_rounds} env_size{env_size} '
                          f'loc update {location_update_frequency}\n')

    save_file = []
    for i in range(start_ind, exp_repeat):
        print(f'round {i}, groups_{number_groups} size_{group_size} no_rounds_{no_rounds} env_size{env_size}')
        tournament = enviromental_tournament.tournament(env_size)
        tournament.location_update_frequency = location_update_frequency

        for n in range(number_groups):
            tournament.add_group(group_size)

        c_percent, scores, coop_total, time_taken = tournament.basic_tournament(no_rounds=no_rounds, percentage_kept=0.9)
        to_be_saved = tournament
        if not save_ind:
            save_file.append(to_be_saved)
        
        with open(f"{file_path}/time_taken.txt", "a") as file_object:
            file_object.write(f'{time_taken} \n')

        if save_ind:
            f_name = f'basic groups_{number_groups}_size_{group_size}_no_rounds_{no_rounds}_env_size{env_size}' \
                     f'_freq{location_update_frequency}_exp{i}'
            np.save(f'{file_path}/{f_name}', to_be_saved)

    if not save_ind:
        d_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        name = f'basic groups_{number_groups} size_{group_size} no_rounds_{no_rounds}_env_size{env_size}_' \
               f'freq{location_update_frequency}'
        f_name = d_time + name

        np.save(f'{file_path}/{f_name}', save_file)

    # environments = list of lists
    # effect is location, group_affected, None, strength
def one_group_environment(environments, save_ind, exp_repeat=20, file_path=None, no_rounds=1000,
                   start_ind=0, location_update_frequency=10):
    if not file_path:
        file_path = 'test_data/random_stuff/exp/environ_tests'

    total_id = ''
    for env in environments:
        total_id += '_'
        total_id += str(env)

    total_id += f'_no_rounds{no_rounds}'
    total_id += f'_freq{location_update_frequency}'

    print(f'environment test {total_id}')

    with open(f"{file_path}/time_taken.txt", "a") as file_object:
        file_object.write(f'one group env {total_id}  \n')

    save_file = []
    for i in range(start_ind, exp_repeat):
        print(f'round {i}, {total_id}')
        tournament = enviromental_tournament.tournament(100)
        tournament.location_update_frequency = location_update_frequency
        tournament.add_group(100)

        for env in environments:
            tournament.add_effect(env[0], env[1], env[2], env[3])

        c_percent, scores, coop_total, time_taken = tournament.basic_tournament(no_rounds=no_rounds,
                                                                                percentage_kept=0.9)
        to_be_saved = tournament
        if not save_ind:
            save_file.append(to_be_saved)

        with open(f"{file_path}/time_taken.txt", "a") as file_object:
            file_object.write(f'{time_taken} \n')

        if save_ind:
            f_name = f'one_group_environment{total_id}_exp{i}'
            np.save(f'{file_path}/{f_name}', to_be_saved)

    if not save_ind:
        f_name = f'one_group_environment{total_id}'

        np.save(f'{file_path}/{f_name}', save_file)



#
# for i in range(1, 4):
#     n_groups_basic(i, True, 100, exp_repeat=20, no_rounds=1000, file_path=r'test_data\random_stuff\exp\control_tests\no movement')

# n_groups_basic(2, False, 50, exp_repeat=50, no_rounds=1000, start_ind=1)

# for i in range(1, 5):
#     n_groups_basic(i, True, 50, exp_repeat=10, no_rounds=10000)

# for i in range(1, 5):
# n_groups_basic(4, True, group_size=100, exp_repeat=20, no_rounds=1000, env_size=1000, start_ind=2)
# n_groups_basic(5, True, group_size=100, exp_repeat=20, no_rounds=1000, env_size=1000, start_ind=0)


# for i in range(1, 5):
#     n_groups_basic(i, True, 50, exp_repeat=10, no_rounds=10000, env_size=1000)

# one_group_environment([[[20, 20], [0], 'score', 4.22222]], True, exp_repeat=1, no_rounds=400,
#                       location_update_frequency=20)

# n_groups_basic(3, True, 50, exp_repeat=50, no_rounds=1000)
# n_groups_basic(10, True, 50, exp_repeat=30, no_rounds=1000)
# n_groups_basic(15, True, 50, exp_repeat=1, no_rounds=1000)

# n_groups_basic(30, True, 50, exp_repeat=1, no_rounds=1000)


# n_groups_basic(5, True, 50, exp_repeat=50, no_rounds=1000)
# n_groups_basic(6, True, 50, exp_repeat=50, no_rounds=1000)



# power = [1.1, 3, 5, 10, 20]
# for p in power:
#     one_group_environment([[[20, 20], [0], None, p]], False)
#
# one_group_environment([[[10, 10], [0], None, 2], [[90, 90], [0], None, 2]], False)
# one_group_environment([[[10, 10], [0], None, 2], [[90, 90], [0], None, 3]], False)

# for i in range(6, 7):
#     n_groups_basic(i, True)

# number_groups, save_ind, group_size, exp_repeat=20, no_rounds=1000
# n_groups_basic(10, False, 100, 1, 1000)
# n_groups_basic(2, False, 100, 1, 15000)

# one_group_environment([[[50, 50], [0], None, 0.01]], False)
#
# one_group_environment([[[0, 99], [0], None, 0.1],
#                       [[99, 0], [0], None, 0.1],
#                       [[30, 30], [0], None, 0.1],
#                       [[70, 70], [0], None, 0.1]], False)
#
# env_list = []
# env_list.append([[0, 0], [0], None, 0.01])
# env_list.append([[99, 99], [0], None, 0.01])
# env_list.append([[0, 99], [0], None, 0.1])
# env_list.append([[99, 0], [0], None, 0.1])
# env_list.append([[45, 45], [0], None, 4])
# for ind in [i*10 for i in range(10)]:
#     env_list.append([[ind, ind], [0], None, 0.8])
# one_group_environment(env_list, False)

