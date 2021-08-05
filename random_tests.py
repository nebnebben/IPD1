import matplotlib.pyplot as plt

from environments import *
from Automata import *
import pprint
import numpy as np

def semi_variance(environment, interval,  type='score', absolute=False, normalised=False, group=0):
    if absolute:
        modifier_func = env.get_modifiers_absolute
    else:
        modifier_func = env.get_modifiers

    bot = Movable_Automaton()
    size = environment.size
    horizontal_differences = []
    i = 0
    j = 0
    while(i < size - 1):
        while(j < size - 1):
            if (j + interval) > (size - 1):
                break
            bot.location = [i, j]
            init_height = modifier_func(bot, type)
            bot.location = [i, j+interval]
            next_height = modifier_func(bot, type)
            diff = ((init_height - next_height)*size)**2
            horizontal_differences.append(diff)
            j += interval
        i += interval
    return np.mean(horizontal_differences)


size = 100
env = Environment(size)
# env.add_effect([0, 0], [0], None, 0.01)
# env.add_effect([99, 99], [0], None, 0.01)
# env.add_effect([0, 99], [0], None, 0.1)
# env.add_effect([99, 0], [0], None, 0.1)
# env.add_effect([50, 50], [0], None, 2)
# env.add_effect([20, 20], [0], 'score', 2)
env.add_effect([80, 80], [0], 'score', 5)

# env.add_effect([70, 70], [0], None, 0.1)
# for ind in [i*10 for i in range(10)]:
#     env.add_effect([ind, ind], [0], None, 0.8)



bot = Movable_Automaton(location=[49, 49])

board = np.zeros((size, size))

for i in range(size):
    for j in range(size):
        # print(env.effects[0].effect_strength([i*10,j*10]))
        bot.location = [i, j]
        # print(i, j)
        # print(env.effects[0].effect_strength([i, j]))
        # print(env.effects[1].effect_strength([i, j]))
        board[i][j] = env.get_modifiers_absolute(bot, 'score')
        # board[i][j] = env.effects[0].effect_strength([i*10, j*10])
# pprint.pprint(board)
print(np.max(board), np.min(board))
plt.title('Score multiplier (2x) at 20,20')
plt.xlabel('X')
plt.ylabel('Y')
plt.imshow(board, cmap='hot', interpolation='nearest', origin='lower')