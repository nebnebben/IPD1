from tournament_adv import *
import matplotlib.pyplot as plt
import matplotlib.cm as cm



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    c_percent, scores = repeated_tournament_evolutionary(no_rounds=400, pop_size=100, percentage_kept=0.95)
    # plt.plot(scores)
    # plt.show()
    # print('complete')
    cmap = cm.jet
    c = np.linspace(0, 100, len(c_percent))

    marker_size = 5000 / len(scores)
    plt.scatter(c_percent, scores, c=c, cmap=cmap, s=marker_size)
    plt.title('Populations over time')
    plt.xlabel('% of Cooperative States')
    plt.ylabel('Average Population Score')
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
