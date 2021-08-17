import enviromental_tournament
from tournament_adv import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from enviromental_tournament import *
from utility_and_viz import *


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    tournament = enviromental_tournament.tournament(100)
    # tournament.add_effect([20, 20], [0], 'score', 2)
    # tournament.add_effect([80, 80], [1], None, 2)
    # tournament.add_effect([20, 20], [0], 'score', 2)
    # tournament.add_effect([0, 0], [0], 'noise', 1.1)
    # for i in range(5):
    tournament.add_group(100)

    c_percent, scores, coop_total, time_taken = tournament.basic_tournament(no_rounds=1000, percentage_kept=0.9)
    # c_percent, scores = repeated_tournament_evolutionary(no_rounds=1000, pop_size=100, percentage_kept=0.9)
    # plt.plot(scores)
    # plt.show()
    # print('complete')
    cmap = cm.jet
    c = np.linspace(0, 100, len(c_percent))

    marker_size = 5000 / len(scores)
    plt.scatter(c_percent, scores, c=c, cmap=cmap, s=marker_size)
    plt.title('Populations over time')
    plt.xlabel('% of Cooperative Interactions')
    plt.ylabel('Average Population Score')
    plt.show()

print('done')
print(np.mean(c_percent))
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
