import copy

import environments
from Automata import *
from Network_Generation import *
from tournament_basic import *
from tournament_adv import *
from copy import deepcopy
from environments import *
import time
from lru import LRU

class tournament:

    def __init__(self, size):
        # stores history of all automata
        self.automata_history = []
        self.mutate_rate = 0.03
        self.no_nodes = 8
        self.env = environments.Environment(size)

        # list of lists
        # index corresponds to group number
        self.pop = []
        self.saved = LRU(100000)

        self.cooperate = []

    """
    Updates the population by replacing existing individuals with random copies and 
    then mutating them. classic=True only does this to a certain subset of the population
    classic=False does this to the whole population
    """

    def update_pop(self, pop, kept, results, classic=False):

        pop_size = len(pop)

        # mutates some of the bots
        if classic:
            # Mutates the other half
            mutate_size = pop_size - kept
            # list of [[own_nodes, diff_nodes], ...]
            new_nodes = roulette_select(mutate_size, results[pop_size - kept:])
        # mutates all of the bots
        else:
            new_nodes = roulette_select(pop_size, results)

        # Mutates own and diff nodes
        for i in range(len(new_nodes)):
            pop[i].own_nodes = mutate_network(new_nodes[i][0], self.mutate_rate, self.no_nodes)
            pop[i].diff_nodes = mutate_network(new_nodes[i][1], self.mutate_rate, self.no_nodes)

        # pop = kept_bots + new_bots
        return pop

    def move_pop(self, pop):
        for automaton in pop:
            self.env.move_automaton(automaton)

        # location_set = {}
        # for p in pop:
        #     temp = tuple(p.location)
        #     if temp not in location_set:
        #         location_set[temp] = 1
        #     else:
        #         location_set[temp] += 1
        #
        # for v in location_set.values():
        #     if v > 1:
        #         print('here')

    """
    Updates useful history stuff
    But removes redundant info, such as movement history for bots
    """
    def update_history(self):
        copied_pop = copy.deepcopy(self.pop)
        for group in copied_pop:
            for automaton in group:
                automaton.location_list = []
        self.automata_history.append(copied_pop)

    # def add_groups
    """
    
    """
    def add_group(self, number):
        own_nodes = [gen_random_network(self.no_nodes) for i in range(number)]
        diff_nodes = [gen_random_network(self.no_nodes) for i in range(number)]
        group = [Movable_Automaton(own_nodes[i], diff_nodes[i], group=len(self.pop), id=i) for i in range(number)]
        for automata in group:
            self.env.add_automaton(automata)

        self.pop.append(group)


    """
    Adds effect to the environment
    """
    def add_effect(self, location, affected_groups, type, strength):
        self.env.add_effect(location, affected_groups, type, strength)

    def basic_tournament(self, no_rounds=100, pop_size=50, percentage_kept=0.8):
        # flattens groups into single list
        # but is just a list of references so it doesn't matter
        overall_pop = np.array(self.pop).flatten()

        # How much of the population should be kept
        # kept = round(pop_size * percentage_kept)
        # list of numbers, according to individual population sizes
        kept = [round(len(group)*percentage_kept) for group in self.pop]

        # Stores average scores
        avg_scores = []
        # Stores the percentage of cooperative states at each generation
        c_percent = []

        # Saving the scores of automata that play against each other
        # So it doesn't need to recomputed for future generations
        self.saved = LRU(len(overall_pop)**2)

        # Saves the original population to see how much is left by the end
        original_pop = {hash(ind) for ind in overall_pop}

        # stores intial pop
        self.update_history()

        start_time = time.time()

        for i in range(no_rounds):
            # Updates history
            # print('')
            # start_time = time.time()
            # self.update_history()
            # print(time.time()-start_time)

            # Runs a tournament
            # start_time = time.time()
            # res, coop_total = tournament2(self.env, self.pop, self.saved)

            res, coop_total, coop_total2 = tournament_test(self.env, self.pop, self.saved)
            # print(time.time() - start_time)
            # print('')
            if len(self.saved) > (len(overall_pop)*3)**2:
                self.saved = {}
            # scores = [x[0] for x in res]
            # pop = [x[1] for x in res]
            # print(min(scores), max(scores), np.mean(scores), coop_total)

            scores = [[x[0] for x in group] for group in res]
            pop = [[x[1] for x in group] for group in res]
            print(np.min(scores), np.max(scores), np.mean(scores), coop_total, coop_total2)
            # print(np.mean([x.location for x in self.pop[0]]))

            # move pop
            for group in self.pop:
                self.move_pop(group)

            # Gets co-operation percentage
            c_percent.append(coop_total2)
            self.cooperate.append(coop_total)

            # Gets the average scores
            # avg_scores.append(sum(scores) / len(scores))
            avg_scores.append(np.sum(scores) / len(np.array(scores).flatten()))

            # Updates each group in the population, evolution and mutation
            # on per group basis
            # for i, group in enumerate(self.pop):
            #     self.pop[i] = self.update_pop(group, kept[i], res)
            # self.update_pop(pop, kept[0], res)
            # self.update_pop(pop[0], kept[0], res[0]) # works for some reason
            for i, group in enumerate(pop):
                self.update_pop(group, kept[i], res[i])

            # Updates history
            # self.update_history()

        # Determines what proportion of the orignal bots remain
        seen = 0
        overall_pop = np.array(self.pop).flatten()
        for x in overall_pop:
            if hash(x) in original_pop:
                seen += 1

        print(f'{seen / len(original_pop)} of the original bots remain')

        # How many hashed scores are there
        print(len(self.saved))
        self.saved = {}
        # final time
        time_taken = time.time()-start_time
        print(f'time {time_taken}')

        # Returns co-operation percentages and average scores of the generato
        return c_percent, avg_scores, coop_total, time_taken

