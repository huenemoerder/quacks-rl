import random

# Generating the bag of ingredients for each player.
# Each player starts with 1x [white,3], 2x [white,2], 4x [white,1], 1x [orange,1] and 1x [green,1]

class Bag(object):
    def __init__(self):
        # fill the bag
        self._content = [
            ['white', 3],
            ['green', 1],
            ['orange', 1]]
        
        for _ in range(4):
            self._content.append(['white', 1])
        for _ in range(2):
            self._content.append(['white', 2])

        # shuffle it
        self.reset()

    # After each turn, everything is shuffled back into the bag and all lists are reset.
    def reset(self):
        self.pick_counter = 0
        self.explosion_counter = 0
        self.sampled_content = random.sample(self._content, k=len(self._content))
        self.drawn = []
        self._current_content = self._content[:]
        
    # Pick a ingredient randomly out of the bag. If it was a white one, the counter for exploding is increased and the
    # player might explode.
    def pick(self):
        draw = self.sampled_content[self.pick_counter]
        self._current_content.remove(draw)
        self.drawn.append(draw)
        if draw[0] == 'white':
            self.explosion_counter += draw[1]
            if self.explosion_counter > 7:
                return draw, True, self.explosion_counter
        self.pick_counter += 1
        return draw, False, self.explosion_counter

    # In the course of the game the player will buy more ingredients and add them to the bag.
    def add(self, ingredient):
        #print(ingredient, "was added to the bag")
        self._content.append(ingredient)

    # Returns the current content (left) in the bag
    @property
    def content(self):
        return self._current_content

