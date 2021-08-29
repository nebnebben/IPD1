import math
import numpy as np
import random
import heapq

class Enviroment_Effect:

    def __init__(self, location, affected_groups, effect_type, strength, grid_size, location_sequence=None):
        self.location_sequence = location_sequence
        self.ind = 0

        if location_sequence:
            self.location = self.location_sequence[self.ind]
        else:
            self.location = location

        self.affected_groups = affected_groups
        self.type = effect_type
        self.strength = strength
        self.grid_size = grid_size

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
        # adjusts for noise
        if self.type == 'noise':
            modifier -= 1

        return modifier

    def adjust_location(self):
        self.ind = (self.ind + 1) % len(self.location_sequence)
        self.location = self.location_sequence[self.ind]
        furthest_point = self.get_furthest_point(self.grid_size)
        self.distance_value = (self.strength - 1)/furthest_point


class Environment:

    def __init__(self, size):
        # (x,y): Automaton
        self.automata_locations = {}
        self.size = size
        self.board = np.zeros((size, size))
        # between 0 and 1, 0 - only consider past diff, 1 - only current diff
        self.discount_factor = 0.8
        # gaussian variance
        self.gaussian_var = 1
        # enviromental effects
        self.effects = []

        self.noise = False

        # temp
        self.temp_automata = {}

    # location, affected_groups, effect, strength, grid_size
    """
    Adds enviromental effect
    """
    def add_effect(self, location, affected_groups, effect_type, strength):
        effect = Enviroment_Effect(location, affected_groups, effect_type, strength, self.size)
        if effect_type == 'noise':
            self.noise = True
        self.effects.append(effect)

    """
    Gets modifier to score based on enviroment
    """
    def get_modifiers(self, automata, effect_type):
        modifier = 1
        for effect in self.effects:
            # checks whether modifier applies
            if automata.group in effect.affected_groups and effect_type == effect.type:
                # gets the effect strength based on the automata location, applies to modifier
                modifier *= effect.effect_strength(automata.location)

        return modifier

    def get_modifiers_absolute(self, automata, effect_type):
        modifiers = [1]
        for effect in self.effects:
            # checks whether modifier applies
            if automata.group in effect.affected_groups and effect_type == effect.type:
                # gets the effect strength based on the automata location, applies to modifier
                modifiers.append(effect.effect_strength(automata.location))

        return np.max(modifiers)


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
        automaton.location_list.append([x, y])

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
                nearest_automata.append([dist, self.automata_locations[automata_dist]])

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

    # Fits current real location to integer, board location
    # use heap
    def fit_to_grid(self, location, cur_location):
        closest = np.round(location)
        # if can go to nearest location, then do that
        # if tuple(closest) not in self.automata_locations or np.array_equal(closest, cur_location):
        if tuple(closest) not in self.automata_locations:
            return closest
        # or if it's empty do bfs to find nearest open space
        directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        found_empty = False
        heap = []
        cur_spot = closest
        seen = set()
        seen.add(tuple(closest))
        while(not found_empty):
            for d in directions:
                # gets the dist to the potential spot
                temp = cur_spot + d
                # if not in bounds(
                if temp[0] < 0 or temp[1] < 0 or temp[0] > (self.size - 1) or temp[1] > (self.size - 1):
                    continue
                if tuple(temp) in seen:
                    continue
                seen.add(tuple(temp))
                dist = self.euclidean_distance(location, temp)
                # ensure uniqueness of key by adding random gaussian noise, otherwise multiple of the
                # same key type which causes error
                noise = np.random.normal(0, 0.0001)
                dist += noise
                # pushes to the heap
                keyval_pair = (dist, temp)
                heapq.heappush(heap, keyval_pair)

            cur_spot = heapq.heappop(heap)[1]
            # if tuple(cur_spot) not in self.automata_locations or np.array_equal(cur_spot, cur_location):
            if tuple(cur_spot) not in self.automata_locations:
                return temp

    # Moves current
    def move_automaton(self, automata, i, location_update_frequency, grid=False):
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
        new_location = np.minimum(new_location, [self.size - 1, self.size - 1])

        if grid:
            del self.automata_locations[tuple(automata.location)]
            new_location = self.fit_to_grid(new_location, automata.location)
        else:
            # make sure not exactly in same spot as existing automata
            if tuple(new_location) in self.automata_locations:
                new_location += np.random.normal(0, 0.5, 2)
            del self.automata_locations[tuple(automata.location)]

        # round location to nearest 3 decimal places
        new_location = np.round(new_location, 9)

        # update agent
        automata.old_location = automata.location
        automata.location = new_location
        # v. mem expensive to update location_list every time, so this instead
        if i % location_update_frequency == 0:
            automata.location_list.append(new_location)
        automata.momentum = total_momentum

        self.automata_locations[tuple(new_location)] = automata
        self.temp_automata[tuple(new_location)] = automata

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