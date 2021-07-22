from Automata import *
from Network_Generation import *

"""
Plays out a competition between two automata,
and returns their final scores. Optional arguments are
the number of rounds, whether the score is reset before starting
and whether there is a printout of the results.
"""


def compete(fsm1, fsm2, no_rounds=100, reset=True, printout=True):

    # check whether they are the same group
    if fsm1.group == fsm2.group:
        same_group = True
    else:
        same_group = False

    # Reset points and states if reset, switches nodes to right group
    fsm1.reset_states(same_group)
    fsm2.reset_states(same_group)

    if reset:
        fsm1.reset_scores()
        fsm2.reset_scores()

    fsm1_score = 0
    fsm2_score = 0
    coop_rounds = 0

    # Plays out the tournament and gets the scores
    for i in range(no_rounds):
        fsm1_move = fsm1.current_node.strat
        fsm2_move = fsm2.current_node.strat

        fsm1_score += fsm1.move(fsm1_move, fsm2_move, same_group, record=False)
        fsm2_score += fsm2.move(fsm2_move, fsm1_move, same_group, record=False)

        if fsm1_move == 'C' and fsm2_move == 'C':
            coop_rounds += 1

    fsm1_score /= no_rounds
    fsm2_score /= no_rounds
    coop_rounds /= no_rounds

    if printout:
        print(f'The final scores are FSM1:{fsm1_score} and FSM2:{fsm2_score}')

    return fsm1_score, fsm2_score, coop_rounds


"""
For populations over time, two automata may play off against each other multiple times
if that's the case then its inefficient to recompute tournament outcomes every time.
This stores the resulting score in a hash of those two automata to save time
"""


def hash_score(scores, fsa1, fsa2, no_rounds=120):
    h1 = hash(fsa1)
    h2 = hash(fsa2)
    if (h1, h2) in scores:
        fsm1_score, fsm2_score, coop_percent = scores[(h1, h2)]
    else:
        fsm1_score, fsm2_score, coop_percent = compete(fsa1, fsa2, no_rounds=no_rounds, reset=False, printout=False)
        scores[(h1, h2)] = fsm1_score, fsm2_score, coop_percent
        scores[(h2, h1)] = fsm2_score, fsm1_score, coop_percent

    return fsm1_score, fsm2_score, coop_percent


def face_off(bot1, bot2,  env, saved={}, noise=False):
    fsm1_score, fsm2_score, coop_percent = hash_score(saved, bot1, bot2)
    # Add modifiers to score
    fsm1_score *= env.get_modifiers(bot1)
    fsm2_score *= env.get_modifiers(bot2)
    # save score for bot
    bot1.current_points += fsm1_score
    bot2.current_points += fsm2_score

    return fsm1_score, fsm2_score, coop_percent

"""
This runs a tournmanet between multiple automata acting as contestants
and returns the bots sorted along with their final scores. Each bot plays 
against each other bot to see the most successful overall within that population

competitors = whether existing competitors are used, or whether new ones should be generated (None)
saved = whether there is hashed scores of existing competitors (if there are multiple tournaments) 

"""


def tournament_test(enviroment, competitors=None, saved={}, neighbours=50, noise=False):
    # record group size
    group_sizes = [len(group) for group in competitors]

    # Will come in as list of groups, so need to flatten
    competitors = np.array(competitors).flatten()

    # Amount of interactions that are purely cooperative
    # record on a per group basis, set up initial
    coop_total = {}
    coop_total2 = 0
    groups = len(group_sizes) # number of groups
    for i in range(groups):
        # first number is total from every round, second is number of rounds
        # at end first will be divided by second to get avg.
        coop_total[(i, i)] = [0, 0]
        for j in range(i+1, groups):
            coop_total[(i, j)] = [0, 0]


    # each bot faces against the closest bots to them, equal to neighbours
    # keep track of which bots have already seen each other
    faced_off = set()
    # keep track of how many other bots each bot has interacted with
    # bot : [score, tally]
    game_tally = {}

    # Update automata scores
    for i in range(len(competitors)):
        competitors[i].prev_score = competitors[i].cur_score
        # game_tally[hash(competitors[i])] = [0, 0]
        game_tally[competitors[i].unique_hash()] = [0, 0]


    for bot1 in competitors:
        nearest = enviroment.get_nearest_automata(bot1, neighbours)
        for bot2 in nearest:
            bot1_hash = bot1.unique_hash()
            bot2_hash = bot2.unique_hash()
            # if (hash(bot1), hash(bot2)) in faced_off or (hash(bot2), hash(bot1)) in faced_off:
            #     continue
            # faced_off.add((hash(bot1), hash(bot2)))
            # faced_off.add((hash(bot2), hash(bot1)))
            # game_tally[hash(bot1)][1] += 1
            # game_tally[hash(bot2)][1] += 1

            if (bot1_hash, bot2_hash) in faced_off or (bot2_hash, bot1_hash) in faced_off:
                continue
            faced_off.add((bot1_hash, bot2_hash))
            faced_off.add((bot2_hash, bot1_hash))
            game_tally[bot1_hash][1] += 1
            game_tally[bot2_hash][1] += 1

            fsm1_score, fsm2_score, coop_percent = face_off(bot1, bot2, enviroment, saved, noise)

            # game_tally[hash(bot1)][0] += fsm1_score
            # game_tally[hash(bot2)][0] += fsm2_score

            game_tally[bot1_hash][0] += fsm1_score
            game_tally[bot2_hash][0] += fsm2_score

            # sort groups to get coop numbers
            group_nums = sorted([bot1.group, bot2.group])
            group_nums = tuple(group_nums)
            coop_total[group_nums][0] += coop_percent
            coop_total[group_nums][1] += 1

            coop_total2 += coop_percent


    bots = []
    ind = 0
    for size in group_sizes:
        cur_group = []
        for i in range(size):
            cur_bot = competitors[ind]
            # bot_hash = hash(cur_bot)
            bot_hash = cur_bot.unique_hash()
            # works out average number of points
            h_score = game_tally[bot_hash][0]/game_tally[bot_hash][1]

            competitors[ind].current_points = 0
            cur_group.append([h_score, cur_bot]) # changed from avg_score
            # update automata score
            competitors[ind].cur_score = h_score
            ind += 1
        cur_group = sorted(cur_group, key=lambda kv: kv[0])
        bots.append(cur_group)

    # Get total coop percentage by figuring out total number of interactions
    coop_total2 /= (sum([x[1] for x in game_tally.values()])/2)
    for kv in coop_total.items():
        key = kv[0]
        val = kv[1]
        # makes sure no divisions by zero
        val[1] = max(val[1], 1)
        coop_avg = val[0]/val[1]
        coop_total[key] = [round(coop_avg, 4), val]

    return bots, coop_total, coop_total2


def tournament2(enviroment, competitors=None, saved={}, neighbours=15, noise=False):
    # record group size
    group_sizes = [len(group) for group in competitors]

    # Will come in as list of groups, so need to flatten
    competitors = np.array(competitors).flatten()

    # Saved scores of individual automatons
    saved_scores = [0] * len(competitors)

    # Amount of interactions that are purely cooperative
    # record on a per group basis, set up initial
    coop_total = {}
    coop_total2 = 0
    groups = len(group_sizes) # number of groups
    for i in range(groups):
        # first number is total from every round, second is number of rounds
        # at end first will be divided by second to get avg.
        coop_total[(i, i)] = [0, 0]
        for j in range(i+1, groups):
            coop_total[(i, j)] = [0, 0]

    # Play every bot off against each other
    for i in range(len(competitors)):
        for j in range(i + 1, len(competitors)):
            if i != j:
                fsm1_score, fsm2_score, coop_percent = hash_score(saved, competitors[i], competitors[j])
                # Add modifiers to score
                fsm1_score *= enviroment.get_modifiers(competitors[i])
                fsm2_score *= enviroment.get_modifiers(competitors[j])
                # saves scores
                saved_scores[i] += fsm1_score
                saved_scores[j] += fsm2_score
                competitors[i].current_points += fsm1_score
                competitors[j].current_points += fsm2_score

                # sort groups to get coop numbers
                group_nums = sorted([competitors[i].grou, competitors[j].group])
                group_nums = tuple(group_nums)
                coop_total[group_nums][0] += coop_percent
                coop_total[group_nums][1] += 1

                coop_total2 += coop_percent

    # saves all the automatas and calculates their average scores
    # before sorting them and returning them

    bots = []
    ind = 0
    for size in group_sizes:
        cur_group = []
        for i in range(size):
            h_score = saved_scores[ind] / (len(competitors) - 1)
            competitors[ind].current_points = 0
            cur_group.append([h_score, competitors[ind]]) # changed from avg_score
            # update automata score
            competitors[ind].cur_score = h_score
            ind += 1
        cur_group = sorted(cur_group, key=lambda kv: kv[0])
        bots.append(cur_group)

    # Get total coop percentage
    coop_total2 /= (len(competitors)*(len(competitors)-1))/2
    for kv in coop_total.items():
        key = kv[0]
        val = kv[1]
        coop_avg = val[0]/ val[1]
        coop_total[key] = round(coop_avg, 4)

    return bots, coop_total, coop_total2
