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
    def __init__(self, nodes=None):

        # The start node is the first
        self.start_node = 0

        # Starts at 0 points
        self.current_points = 0

        # Points values for different moves
        self.moves = {('C', 'C'): 3,
                      ('C', 'D'): 0,
                      ('D', 'C'): 5,
                      ('D', 'D'): 1}

        # If not given a node structure to start, generates a default one
        if not nodes:
            node0 = Node('C', 0, 1)
            node1 = Node('D', 0, 1)
            self.nodes = [node0,
                          node1]
        else:
            self.nodes = nodes

        # The current node is the first node
        self.current_node = self.nodes[self.start_node]

        # Current node index
        self.current_node_index = self.start_node

    # Updates the automata depending on the moves
    # Returns the points that move led to
    def move(self, own_move, opp_move, record=True):
        points = self.moves[(own_move, opp_move)]
        if record:
            self.current_points += points

        if opp_move == 'C':
            new_node = self.current_node.coop
        else:
            new_node = self.current_node.defect

        # Actual code
        self.current_node = self.nodes[new_node]
        self.current_node_index = new_node

        return points

    # Resets to 0 points and starts at the inital node again
    def reset_states(self):
        self.current_node = self.nodes[self.start_node]

    def reset_scores(self):
        self.current_points = 0

    # Gets a hash of the automata
    # Very useful
    def __hash__(self):
        nodes = tuple([(x.strat, x.coop, x.defect) for x in self.nodes])
        return hash(nodes)


"""
automata specifically for using in environments
"""

class Movable_Automaton(Automaton):

    def __init__(self, nodes=None, location=None, group=0):
        super().__init__(nodes)
        # [x,y]
        self.location = location
        self.old_location = location
        # integer to represent group
        self.group = group
        # [x, y] direction + magnitude
        self.momentum = np.array([0, 0])
        self.prev_score = 0
        self.cur_score = 0

    def set_location(self, location):
        self.location = location
        self.old_location = location
