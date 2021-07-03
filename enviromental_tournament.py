from Automata import *
from Network_Generation import *
from tournament_basic import *
from tournament_adv import *
from copy import deepcopy

class tournament:

    def __init__(self):
        # stores history of all automata
        self.automata_history = []

    def update_pop(self, pop, kept, res):

        pop_size = len(pop)
        # Keeps the top performing half
        kept_bots = pop[pop_size - kept:]

        # Mutates the other half
        mutate_size = pop_size - kept
        new_bots = roulette_select(mutate_size, res[pop_size - kept:])

        for i in range(len(new_bots)):
            new_bots[i].nodes = mutate_network(new_bots[i])

        pop = kept_bots + new_bots
        return pop


    def basic_tournament(self, no_rounds=100, pop_size=50, percentage_kept=0.8):
        # Generates the initial population
        graphs = [gen_random_network() for i in range(pop_size)]
        pop = [Automaton(graphs[i]) for i in range(pop_size)]

        # How much of the population should be kept
        kept = round(pop_size * percentage_kept)

        # Stores average scores
        avg_scores = []
        # Stores the percentage of cooperative states at each generation
        c_percent = []

        # Saving the scores of automata that play against each other
        # So it doesn't need to recomputed for future generations
        saved = {}

        # Saves the original population to see how much is left by the end
        original_pop = {hash(ind) for ind in pop}


        for i in range(no_rounds):
            self.automata_history.append(pop)

            # Runs a tournament
            res, coop_total = tournament_test(pop_size, pop, saved)
            scores = [x[0] for x in res]
            pop = [x[1] for x in res]
            print(min(scores), max(scores), np.mean(scores))

            # Gets co-operation percentage
            # c_percent.append(cooperate_percent(pop))
            c_percent.append(coop_total)

            # Gets the average scores
            avg_scores.append(sum(scores) / len(scores))

            pop = self.update_pop(pop, kept, res)

        # Determines what proportion of the orignal bots remain
        seen = 0
        for x in pop:
            if hash(x) in original_pop:
                seen += 1

        print(f'{seen / pop_size} of the original bots remain')

        # How many hashed scores are there
        print(len(saved))
        # Returns co-operation percentages and average scores of the generato
        return c_percent, avg_scores

