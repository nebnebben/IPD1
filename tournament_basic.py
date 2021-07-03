from Automata import *
from Network_Generation import *

"""
Plays out a competition between two automata,
and returns their final scores. Optional arguments are
the number of rounds, whether the score is reset before starting
and whether there is a printout of the results.
"""


def compete(fsm1, fsm2, no_rounds=100, reset=True, printout=True):
    # Reset points and states if reset

    fsm1.reset_states()
    fsm2.reset_states()

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

        fsm1_score += fsm1.move(fsm1_move, fsm2_move, record=False)
        fsm2_score += fsm2.move(fsm2_move, fsm1_move, record=False)

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


def hash_score(scores, fsa1, fsa2, no_rounds=100):
    h1 = hash(fsa1)
    h2 = hash(fsa2)
    if (h1, h2) in scores:
        fsm1_score, fsm2_score, coop_percent = scores[(h1, h2)]
    else:
        fsm1_score, fsm2_score, coop_percent = compete(fsa1, fsa2, no_rounds=no_rounds, reset=False, printout=False)
        scores[(h1, h2)] = fsm1_score, fsm2_score, coop_percent
        scores[(h2, h1)] = fsm2_score, fsm1_score, coop_percent

    return fsm1_score, fsm2_score, coop_percent


"""
This runs a tournmanet between multiple automata acting as contestants
and returns the bots sorted along with their final scores. Each bot plays 
against each other bot to see the most successful overall within that population

competitors = whether existing competitors are used, or whether new ones should be generated (None)
saved = whether there is hashed scores of existing competitors (if there are multiple tournaments) 

"""


def tournament_test(no_contestants=200, competitors=None, saved=False):
    # If new bots need to be generated
    if not competitors:
        graphs = [gen_random_network() for i in range(no_contestants)]
        competitors = [Automaton(graphs[i]) for i in range(no_contestants)]

    # If hashed scores have not been saved, start saving them
    # Should be not saved? Ambiguous
    if saved == True:
        saved = {}

    # Saved scores of individual automatons
    saved_scores = [0] * no_contestants
    # Amount of interactions that are purely cooperative
    coop_total = 0

    # Play every bot off against each other
    for i in range(no_contestants):
        for j in range(i + 1, no_contestants):
            if i != j:
                fsm1_score, fsm2_score, coop_percent = hash_score(saved, competitors[i], competitors[j])
                saved_scores[i] += fsm1_score
                saved_scores[j] += fsm2_score
                competitors[i].current_points += fsm1_score
                competitors[j].current_points += fsm2_score
                coop_total += coop_percent

                if saved_scores[i] != competitors[i].current_points or saved_scores[j] != competitors[j].current_points:
                    print('ARGHHH')

    # saves all the automatas and calculates their average scores
    # before sorting them and returning them
    bots = []
    for i, x in enumerate(competitors):
        h_score = saved_scores[i] / (no_contestants - 1)
        avg_score = x.current_points / (no_contestants - 1)
        if h_score >= 5 or h_score != avg_score:
            print('huhjj')
            z = 'abasdjask'
        x.current_points = 0
        bots.append([h_score, x]) # changed from avg_score

    bots = sorted(bots, key=lambda kv: kv[0])

    # Get total coop percentage
    coop_total /= (no_contestants*(no_contestants-1))/2
    return bots, coop_total

