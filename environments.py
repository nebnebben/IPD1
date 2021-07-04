import math
import numpy as np
import random

class Enviroment_Effect:

    def __init__(self, location, affected_groups, effect, strength, grid_size):
        self.location = location
        self.affected_groups = affected_groups
        self.effect = effect
        self.strength = strength

        # Calculates distance modifier based on location + grid_size
        furthest_point = self.get_furthest_point(grid_size)
        self.distance_value = (strength - 1)/furthest_point

    # calculates the euclidean distance between 2 points, p1 = [x1, y1], p2 = [x2, y2]
    def euclidean_distance(self, point1, point2):
        return math.sqrt(((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))

    # Calculates furthest point on a grid from given point, by checking all points at edges
    def get_furthest_point(self, grid_size):
        furthest_point = 0
        furthest_index = grid_size - 1
        for ind in range(grid_size):
            dist = self.euclidean_distance([0, ind], self.location)
            furthest_point = max(furthest_point, dist)
            dist = self.euclidean_distance([ind, 0], self.location)
            furthest_point = max(furthest_point, dist)
            dist = self.euclidean_distance([ind, furthest_index], self.location)
            furthest_point = max(furthest_point, dist)
            dist = self.euclidean_distance([furthest_index, ind], self.location)
            furthest_point = max(furthest_point, dist)
        return furthest_point

    # Strength of the effect at location, returns value between 1 and strength, depending on distance
    def effect_strength(self, cur_location):
        # work out dist to point
        dist_to_point = self.euclidean_distance(self.location, cur_location)
        modifier = self.strength - dist_to_point*self.distance_value
        modifier = max(1, modifier)
        return modifier


class Environment:

    def __init__(self, size):
        # (x,y): Automaton
        self.automata_locations = {}
        self.size = size
        self.board = [[0]*size]*size
        # between 0 and 1, 0 - only consider past diff, 1 - only current diff
        self.discount_factor = 0.8
        # gaussian variance
        self.gaussian_var = 1
        # enviromental effects
        self.effects = []

    # location, affected_groups, effect, strength, grid_size
    """
    Adds enviromental effect
    """
    def add_effect(self, location, affected_groups, effect, strength):
        effect = Enviroment_Effect(location, affected_groups, effect, strength, self.size)
        self.effects.append(effect)

    """
    Gets modifier to score based on enviroment
    """
    def get_modifiers(self, automata):
        modifier = 1
        for effect in self.effects:
            # checks whether modifier applies
            if automata.group in effect.affected_groups:
                # gets the effect strength based on the automata location, applies to modifier
                modifier *= effect.effect_strength(automata.location)

        return modifier

    """
    Adds new automaton to the board
    """
    def add_automaton(self, automaton):
        # get random board position
        empty_space = False
        while(not empty_space):
            x = random.randint(0, self.size-1)
            y = random.randint(0, self.size-1)
            if (x, y) not in self.automata_locations:
                empty_space = True

        self.automata_locations[(x, y)] = automaton
        automaton.set_location(np.array([x, y]))

    # calculates the euclidean distance between 2 points, p1 = [x1, y1], p2 = [x2, y2]
    def euclidean_distance(self, point1, point2):
        return math.sqrt(((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2))

    """
    Returns list of N nearest automata
    """
    def get_nearest_automata(self, target_automata, nearest_number):
        location = target_automata.location

        nearest_automata = []
        # cycles through all possible automata locations
        for automata_dist in self.automata_locations.keys():
            dist = self.euclidean_distance(location, automata_dist)
            # if not self
            if dist > 0:
                nearest_automata.append([automata_dist, self.automata_locations[automata_dist]])

        # sort by distance and then just return closest automata
        nearest_automata.sort(key=lambda kv: kv[0])
        return [bot[1] for bot in nearest_automata][:nearest_number]

    # normalise vector, sets to a certain magnitude
    # if cond, then only sets vector to magnitude if larger than magnitude
    def normalise_vector(self, vector, magnitude, cond):
        vector_size = np.linalg.norm(vector)
        if cond:
            # get to correct size
            if vector_size > magnitude:
                vector /= vector_size
                return vector * magnitude
            else:
                return vector
        else:
            vector /= vector_size
            return vector * magnitude

    # Moves current
    def move_automaton(self, automata):
        # agent = self.automata_locations[tuple(location)]

        noise = np.random.normal(0, self.gaussian_var, 2)
        old_momentum = self.discount_factor * automata.momentum
        score_diff = (automata.cur_score - automata.prev_score) * 100

        new_momentum = automata.location - automata.old_location
        adjusted_momentum = (1 - self.discount_factor) * score_diff * new_momentum
        total_momentum = (old_momentum + adjusted_momentum)

        # restrain magnitude of vector to 4 max
        limit = 4
        total_momentum = self.normalise_vector(total_momentum, limit, True)

        new_location = automata.location + total_momentum + noise
        new_location = np.maximum(new_location, [0, 0])
        new_location = np.minimum(new_location, [self.size, self.size])

        # round location to nearest 3 decimal places
        new_location = np.round(new_location, 3)

        # update agent
        automata.old_location = automata.location
        automata.location = new_location
        automata.location_list.append(new_location)
        automata.momentum = total_momentum

        del self.automata_locations[tuple(automata.old_location)]
        self.automata_locations[tuple(new_location)] = automata

        return new_location




    # Moves current
    def move_automaton_test(self, old_location, cur_location, momentum, new_score, old_score):
        # new location
        noise = np.random.normal(0, self.gaussian_var, 2)
        old_momentum = self.discount_factor * momentum
        score_diff = (new_score - old_score) * 100

        # adjust so score_diff is at least 1
        # if abs(score_diff) < 1:
        #     if score_diff > 0:
        #         score_diff = 1
        #     else:
        #         score_diff = -1

        new_momentum = cur_location - old_location
        adjusted_momentum = (1 - self.discount_factor) * score_diff * new_momentum
        total_momentum = (old_momentum + adjusted_momentum)

        limit = 4
        # restrain max plus min for momentum
        # total_momentum = np.minimum(total_momentum, [limit, limit])
        # total_momentum = np.maximum(total_momentum, [-limit, -limit])
        total_momentum = self.normalise_vector(total_momentum, limit, True)

        new_location = cur_location + total_momentum + noise
        new_location = np.maximum(new_location, [0, 0])
        new_location = np.minimum(new_location, [self.size, self.size])

        print(f'momentum is {np.round(total_momentum,4)}, noise is {np.round(noise,4)}')

        return new_location, total_momentum

    def movement_test(self, location, iterations, env_strength):

        ee = Enviroment_Effect([20, 30], 0, 0, env_strength, 100)
        old_score = 0
        new_score = 0
        momentum = 0
        prev_location = location[:]
        cur_location = location[:]
        for i in range(iterations):
            old_score = new_score
            new_score = ee.effect_strength(cur_location)
            temp = cur_location[:]
            cur_location, momentum = self.move_automaton2(prev_location, cur_location, momentum, new_score, old_score)
            prev_location = temp
            print(prev_location)
            print(f'score diff is {new_score - old_score}, new score is {new_score}')