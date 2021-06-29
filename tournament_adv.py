from Automata import *
from Network_Generation import *
from tournament_basic import *
from copy import deepcopy

# Gets the average number of co-operative states from a population
def cooperate_percent(pop):
    if type(pop) != list:
        pop = [pop]

    # Keeps track of the number of co-operative states
    # Then takes an average
    pop_coop_count = 0
    for x in pop:
        coop_count = 0
        for state in x.nodes:
            if state.strat == 'C':
                coop_count += 1
        coop_count /= len(x.nodes)
        pop_coop_count += coop_count

    coop_avg = pop_coop_count / len(pop)
    return coop_avg

# roulette wheel selection
# PASS BY FUCKING REFERENCE
# CHANGE THIS SO IT DEEPCoPIES OBJECTS
def roulette_select(size, population):
    out = []
    total = sum([x[0] for x in population])
    selection_probs = [x[0] / total for x in population] # Normalises probability
    for i in range(size):
        choice = population[np.random.choice(len(population), p=selection_probs)][1]
        out.append(deepcopy(choice)) # Deepcopy!
    return out



"""
This looks at how a population of automata and their strategies change over time, by having a
tournament each generation within them, discarding the lowest peforming 
automata, and replacing the gaps with randomly sampled automata

"""


def repeated_tournament_evolutionary(no_rounds=100, pop_size=50, percentage_kept=0.8):
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
        # clear_output(wait=True)
        # Gets co-operation percentage
        c_percent.append(cooperate_percent(pop))

        # Runs a tournament
        res = tournament(pop_size, pop, saved)
        scores = [x[0] for x in res]
        bots = [x[1] for x in res]
        print(min(scores), max(scores), np.mean(scores))

        # Gets the average scores
        avg_scores.append(sum(scores) / len(scores))

        # Keeps the top performing half
        kept_bots = bots[pop_size - kept:]

        # Mutates the other half
        mutate_size = pop_size - kept
        new_bots = roulette_select(mutate_size, res[pop_size - kept:])

        for i in range(len(new_bots)):
            new_bots[i].nodes = mutate_network(new_bots[i])

        pop = kept_bots + new_bots

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
