import copy
from collections import namedtuple
import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from utility_and_viz import *



# Node = namedtuple('Node', ['strategy','cooperate','defect'])

"""
This class represents the individual nodes constructing the automata
strat = whether they will cooperate/defect if their opponent cooperates 
coop = the node they will go to if their opponent cooperates
defect = the node they will go to if their opponent defects
"""


class Node:
    def __init__(self, strat=None, coop=None, defect=None):
        self.strat = strat
        self.coop = coop
        self.defect = defect


"""
The main class, this represents an automaton. It consists of the nodes and how they are connected.
It also updates the state of the automaton if it's playing against another automaton

"""


class Automaton:

    # Takes in whether given a graph structure or not
    # If not generates a default one
    def __init__(self, own_nodes=None, diff_nodes=None, group=0):
        # integer to represent group
        self.group = group

        # The start node is the first
        self.start_node = 0

        # Starts at 0 points
        self.current_points = 0

        # Points values for different moves
        self.own_moves = {('C', 'C'): 3,
                          ('C', 'D'): 0,
                          ('D', 'C'): 5,
                          ('D', 'D'): 1}

        self.diff_moves = {('C', 'C'): 3,
                          ('C', 'D'): 0,
                          ('D', 'C'): 5,
                          ('D', 'D'): 1}

        default_nodes = [Node('C', 0, 1),
                         Node('D', 0, 1)]

        if not own_nodes:
            own_nodes = copy.deepcopy(default_nodes)
        if not diff_nodes:
            diff_nodes = copy.deepcopy(default_nodes)
        self.own_nodes = own_nodes
        self.diff_nodes = diff_nodes

        # The current node is the first node
        self.current_node = self.own_nodes[self.start_node]

        # Current node index
        self.current_node_index = self.start_node

    # Updates the automata depending on the moves
    # Returns the points that move led to
    # can deal with moves in or out of group
    def move(self, own_move, opp_move, same_group=True, record=False):
        # points are based on same or separate group
        if same_group:
            points = self.own_moves[(own_move, opp_move)]
        else:
            points = self.diff_moves[(own_move, opp_move)]

        # if the points should be recorded in the automata
        if record:
            self.current_points += points

        # choose new node based on opponent move
        if opp_move == 'C':
            new_node = self.current_node.coop
        else:
            new_node = self.current_node.defect

        # Accounts for same or different group
        if same_group:
            self.current_node = self.own_nodes[new_node]
        else:
            self.current_node = self.diff_nodes[new_node]

        self.current_node_index = new_node

        return points

    # Resets to 0 points and starts at the inital node again
    # same group, means starts at own_nodes, diff group - diff_nodes
    def reset_states(self, same_group):
        if same_group:
            self.current_node = self.own_nodes[self.start_node]
        else:
            self.current_node = self.diff_nodes[self.start_node]

    def reset_scores(self):
        self.current_points = 0

    # Gets a hash of the automata
    # Very useful
    def __hash__(self):
        nodes1 = tuple([(x.strat, x.coop, x.defect) for x in self.own_nodes])
        nodes2 = tuple([(x.strat, x.coop, x.defect) for x in self.diff_nodes])
        return hash((self.group, nodes1, nodes2))


"""
automata specifically for using in environments
"""

class Movable_Automaton(Automaton):

    def __init__(self, own_nodes=None, diff_nodes=None, location=None, group=0, id=0):
        super(Movable_Automaton, self).__init__(own_nodes, diff_nodes, group)
        # [x,y]
        self.location = location
        self.old_location = location
        self.location_list = []
        # [x, y] direction + magnitude
        self.momentum = np.array([0, 0])
        self.prev_score = 0
        self.cur_score = 0

        # Starts at 0 points
        self.current_points = 0

        # id
        self.id = id


    def set_location(self, location):
        self.location = location
        self.old_location = location

    def unique_hash(self):
        return (self.group, self.id)