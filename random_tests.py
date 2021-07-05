from environments import *
from Automata import *
import pprint
import numpy as np


size = 100
env = Environment(size)
env.add_effect([0, 0], [0], None, -1)
env.add_effect([99, 99], [0], None, -1)
env.add_effect([45, 45], [0], None, 5)


bot = Movable_Automaton(location=[49, 49])

board = np.zeros((size, size))

for i in range(size):
    for j in range(size):
        # print(env.effects[0].effect_strength([i*10,j*10]))
        bot.location = [i, j]
        # print(i, j)
        # print(env.effects[0].effect_strength([i, j]))
        # print(env.effects[1].effect_strength([i, j]))
        board[i][j] = env.get_modifiers(bot)
        # board[i][j] = env.effects[0].effect_strength([i*10, j*10])
# pprint.pprint(board)
print(np.max(board))
plt.imshow(board, cmap='hot', interpolation='nearest')