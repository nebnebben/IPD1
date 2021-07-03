import math
import numpy as np

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
    def move_automaton(self, location):
        agent = self.automata_locations[tuple(location)]

        noise = np.random.normal(0, self.gaussian_var, 2)
        old_momentum = self.discount_factor * agent.momentum
        score_diff = (agent.cur_score - agent.prev_score) * 100

        new_momentum = agent.location - agent.old_location
        adjusted_momentum = (1 - self.discount_factor) * score_diff * new_momentum
        total_momentum = (old_momentum + adjusted_momentum)

        # restrain magnitude of vector to 4 max
        limit = 4
        total_momentum = self.normalise_vector(total_momentum, limit, True)

        new_location = agent.location + total_momentum + noise
        new_location = np.maximum(new_location, [0, 0])
        new_location = np.minimum(new_location, [self.size, self.size])

        # update agent
        agent.old_location = agent.location
        agent.location = new_location
        agent.momentum = total_momentum

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