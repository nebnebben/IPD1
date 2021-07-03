
class tournament:

    def __init__(self, no_rounds=100, pop_size=100, percent_kept=0.8):
        # stores history of all automata
        self.automata_history = []

        self.