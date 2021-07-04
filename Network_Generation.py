import random
import numpy as np
from Automata import *

"""
This generates a random strategy for a node based on a percentage chance for cooperation
and it returns whether the node will cooperate 'C' or defect 'D'
"""


def get_nodestrat(p_coop):
    strat = {0: 'C', 1: 'D'}
    res = random.choices([0, 1], weights=[p_coop, 1-p_coop])
    return strat[res[0]]


"""
This is an algorithm to generate a random graph of nodes that 
can be used for the basis of an automata. You can specify the number
of nodes, or that can be generated randomly
"""


def gen_random_network(no_nodes=None):
    # Chance of getting a co_op vs. defect node
    p_coop = 0.5
    p_defect = 1 - p_coop

    # Chance of moving to a co-op vs. defect node
    p_move = 0.5

    if not no_nodes:
        no_nodes = random.randint(1, 10)

    # Generates all nodes
    nodes = [Node() for i in range(no_nodes)]

    # Connects each node to random other nodes
    # Gives a random strategy
    for i in range(no_nodes):
        nodes[i].coop = random.randint(0, no_nodes - 1)
        nodes[i].defect = random.randint(0, no_nodes - 1)
        nodes[i].strat = get_nodestrat(p_coop)

    return nodes


"""
This gets an existing automaton and mutates the network

"""


def mutate_network(nodes, mutate_rate=0.05):
    # nodes = automaton.nodes
    no_nodes = len(nodes)

    # Chance to add or remove a node
    p = np.random.uniform()
    if p < mutate_rate/2 and no_nodes > 1:
        nodes.pop()
        no_nodes -= 1
    elif p < mutate_rate:
        no_nodes += 1
        new_node = Node()
        new_node.coop = random.randint(0, no_nodes - 1)
        new_node.defect = random.randint(0, no_nodes - 1)
        new_node.strat = get_nodestrat(0.5)
        nodes.append(new_node)

    # Chance to change existing connections or states
    # Two latter p = ... commented out, changes whether entire node is mutated or just individual parts of a node
    for i in range(no_nodes):
        # Random node, C or D
        p = np.random.uniform()
        if p < mutate_rate:
            nodes[i].strat = get_nodestrat(0.5)

        # New connection if out of bounds or if randomly mutated
        # p = np.random.uniform()
        if p < mutate_rate or nodes[i].coop >= no_nodes:
            nodes[i].coop = random.randint(0, no_nodes - 1)

        # New connection if out of bounds or if randomly mutated
        # p = np.random.uniform()
        if p < mutate_rate or nodes[i].defect >= no_nodes:
            nodes[i].defect = random.randint(0, no_nodes - 1)

    return nodes
