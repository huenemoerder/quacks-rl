from flaskr.bag import Bag
import random

# The player class contains everything the player can see or knows.
# Each player has a pot and a bad with ingredients as well as many, many other values as usually seen on the board.

class Player(object):
    def __init__(self, rule_set):
        self.bag = Bag()
        self.pot = []
        self.drop_position = 0
        self.rats = 0
        self.current_position = self.drop_position
        self.money = 0
        self.tmp_vp = 0
        self.vp = 0
        self.rubies = 1
        self.exploded = False
        self.stopped = False
        self.bought = []
        self.bought_ = []
        self.rule_set = rule_set

    # Getter and Setter for the variables
    def setMoney(self, money):
        self.money += money

    def setVP(self, vp):
        self.vp += vp

    def setCount(self, value):
        self.current_position += value

    def setDrop(self, value):
        self.drop_position += value

    def setRuby(self, value):
        self.rubies += value

    def getMoney(self):
        return self.money
    
    def getVP(self):
        return self.vp

    def getTmpVP(self):
        return self.tmp_vp

    def getCurrentPosition(self):
        return self.current_position

    def getDropPosition(self):
        return self.drop_position

    def getCurrentScore(self):
        return self.board()

    def explode(self):
        self.exploded = True

    # This is a (not so pretty) representation of the player's pot-board. On every field (54 in total) you have a
    # different money-value, a vp-value and a bool if it is a ruby-field or not.
    def board(self):
        position = self.current_position + 1

        if position > 53:
            current_score = {
                'current_position': self.current_position,
                'cur_money': 35,
                'cur_vp': 15,
                'cur_ruby': False
            }
        else:
            ruby = self.rubyField(position)

            vp = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                  2, 2, 2, 2, 3, 3, 3, 3, 4, 4,
                  4, 4, 5, 5, 5, 5, 6, 6, 6, 7,
                  7, 7, 8, 8, 8, 9, 9, 9, 10, 10,
                  10, 11, 11, 11, 12, 12, 12, 12, 13, 13,
                  13, 14, 14, 15]

            money = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
                     10, 11, 12, 13, 14, 15, 15, 16, 16, 17,
                     17, 18, 18, 19, 19, 20, 20, 21, 21, 22,
                     22, 23, 23, 24, 24, 25, 25, 26, 26, 27,
                     27, 28, 28, 29, 29, 30, 30, 31, 31, 32,
                     32, 33, 33, 35]

            current_score = {
                'current_position' : self.current_position,
                'cur_money' : money[position],
                'cur_vp' : vp[position],
                'cur_ruby' : ruby
            }
        return current_score

    def rubyField(self, position):
        if position > 53:
            return False
        else:
            rubies = [False, False, False, False, False, True, False, False, False, True,
                      False, False, False, True, False, False, True, False, False, False,
                      True, False, False, False, True, False, False, False, True, False,
                      True, False, False, False, True, False, True, False, False, False,
                      True, False, True, False, False, False, True, False, False, False,
                      True, False, True, False]
        return rubies[position]

    def rules(self, color):
        if self.rule_set[color] == 0:
            if color == 'green':
                self.greenRule0()
            if color == 'red':
                self.redRule0()
            if color == 'blue':
                self.blueRule0()
            if color == 'yellow':
                self.yellowRule0()
            if color == 'purple':
                self.purpleRule0()
            if color == 'black':
                pass

    def getPrices(self):
        prices = [
            ['orange', 1, 3],
            ['red', 1, 6],
            ['red', 2, 10],
            ['red', 4, 16],
            ['blue', 1, 4],
            ['blue', 2, 8],
            ['blue', 4, 14],
            ['green', 1, 4],
            ['green', 2, 8],
            ['green', 4, 14],
            ['yellow', 1, 8],
            ['yellow', 2, 12],
            ['yellow', 4, 18],
            ['purple', 1, 9]
        ]
        return prices

    # This is the die usually rolled by the player who reaches the furthest. With one player that is to be ignored
    # for now but might come into play later.
    def rollDie(self):
        result = random.randrange(6)
        text = ''
        if result == 0 or result == 1:
            self.vp += 1
            text = 'Gain One Victory Point!'
        elif result == 2:
            self.vp += 2
            text = 'Gain Two Victory Points!'
        elif result == 3:
            self.rubies += 1
            text = 'Gain One Ruby!'
        elif result == 4:
            self.drop_position += 1
            text = 'Move your Starting Position!'
        elif result == 5:
            self.bag.add(['orange', 1])
            text = 'Gain one Pumpkin!'
        return text

    # Function to draw an ingredient from the bag and put it on the board (in the pot)
    def pick(self):
        if not self.exploded:
            draw, explosion, explosion_counter = self.bag.pick()
            self.setCount(draw[1])
            #print("You drew a ", draw)
            
            self.pot.append(draw)
            if draw[0] == 'red':
                self.rules('red')
            if draw[0] == 'blue':
                self.rules('blue')
            if draw[0] == 'yellow':
                self.rules('yellow')
            current_score = self.board()
            self.current_position = current_score['current_position']
            self.money = current_score['cur_money']
            self.tmp_vp = current_score['cur_vp']
            
            if explosion:
                self.explode()
            return draw, explosion, explosion_counter
        return None, None, None

    # if a player ends his turn everything he did is reset
    def endTurn(self):
        self.exploded = False
        self.stopped = False
        self.current_position = self.drop_position
        self.pot = []
        self.bag.reset()
        self.money = 0
        self.tmp_vp = 0
        self.bought = []
        self.bought_ = []

    # end your brewing step check for rules (green, ((black, purple)) )
    def stopBrewing(self, first):
        self.stopped = True
        #if first:
        #   roll die - NOT IMPLEMENTED
        self.rules('green')
        #self.rules('black')
        self.rules('purple')
        current_score = self.board()

        if current_score['cur_ruby']:
            self.rubies += 1

    # buy max 2 ingredients from different colors per round
    def buy(self, ingredient, cost):
        if (len(self.bought) < 2) and (self.money >= cost) and (ingredient[0] not in self.bought):
            self.bag.add(ingredient)
            self.bought.append(ingredient[0])
            self.bought_.append([ingredient[0], ingredient[1], cost])
            self.money -= cost
            #print("You bought", ingredient, "for", cost)

    # spend 2 rubies to move your starting drop one field
    def moveDrop(self):
        if self.rubies >= 2:
            self.drop_position += 1
            self.rubies -= 2

    # --- RULES ----

    # "If the last or second-to-last chip in your pot is a green chip, gain one ruby"
    # Cost: 4 | 8 | 14
    def greenRule0(self):
        if len(self.pot) > 1:
            if self.pot[-1][0] == 'green' or self.pot[-2][0] == 'green':
                self.rubies += 1
                #print("You got one Ruby from the Green Ingredients!")

    # "If the last or second-to-last chip in your pot is a green chip, gain one ingredient depending on the green's
    #  chip value - 1:orange 2:blue or red 4:yellow or purple (at random)"
    # Cost: 6 | 11 | 18
    def greenRule1(self):
        if len(self.pot) > 1:
            if self.pot[-1] == ['green', 1] or self.pot[-2] == ['green', 1]:
                self.bag.add(['orange', 1])
                #print("You got one orange chip from the Green Ingredients!")
            else:
                rand = random.randrange(2)
                if self.pot[-1] == ['green', 2] or self.pot[-2] == ['green', 2]:
                    if rand == 1:
                        self.bag.add(['red', 1])
                        #print("You got one red chip from the Green Ingredients!")
                    else:
                        self.bag.add(['blue', 1])
                        #print("You got one blue chip from the Green Ingredients!")
                if self.pot[-1] == ['green', 4] or self.pot[-2] == ['green', 4]:
                    if rand == 1:
                        self.bag.add(['yellow', 1])
                        #print("You got one yellow chip from the Green Ingredients!")
                    else:
                        self.bag.add(['purple', 1])
                        #print("You got one purple chip from the Green Ingredients!")

    # "If the last or second-to-last chip in your pot ts a green chip, you may roll the dice the number of times
    # you have green chips"
    # Cost: 4 | 8 | 14
    def greenRule2(self):
        if len(self.pot) < 1:
            if self.pot[-1][0] == 'green':
                self.rollDie()
            if self.pot[-2][0] == 'green':
                self.rollDie()

    # "If there are already orange chips in your pot the red chip moves up 1 or 2 places"
    # Cost: 6 | 10 | 16
    def redRule0(self):
        num_oranges = [chip for chip in self.pot if chip[0] == 'orange']
        if len(num_oranges) == 1 or len(num_oranges) == 2:
            self.current_position += 1
        if len(num_oranges) > 2:
            self.current_position += 2

    # "If the previous chip was white, this red chip moves up 1/2/3 spaces"
    # Cost: 5 | 9 | 15
    def redRule1(self):
        if len(self.pot) > 1:
            if self.pot[-1] == ['white', 1]:
                self.current_position += 1
            if self.pot[-1] == ['white', 2]:
                self.current_position += 2
            if self.pot[-1] == ['white', 3]:
                self.current_position += 3

    # "Every red chip is as value indicated or the highest red chip in the pot so far"
    # Cost: 6 | 11 | 18
    def redRule2(self):
        max_red = max([chip[1] for chip in self.pot if chip[0] == 'red'])
        if max_red == 1:
            self.current_position += 1
        if max_red == 2:
            self.current_position += 2
        if max_red == 4:
            self.current_position += 4

    # "If this chip is on a ruby space, you IMMEDIATELY receive 1 ruby."
    # Cost: 4 | 8 | 14
    def blueRule0(self):
        if self.rubyField(self.current_position):
            self.rubies += 1

    # "If this chip is on a ruby space, you IMMEDIATELY receive 1/2/4 victory points."
    # Cost: 5 | 10 | 19
    def blueRule1(self):
        if len(self.pot) > 1:
            if self.rubyField(self.current_position):
                if self.pot[-1] == ['blue', 1]:
                    self.vp += 1
                if self.pot[-1] == ['blue', 2]:
                    self.vp += 2
                if self.pot[-1] == ['blue', 4]:
                    self.vp += 4

    # "For every white 1-chip" within the last 1/2/4 chips places, you immediately receive 1 ruby."
    # Cost: 8 | 15 | 19
    def blueRule2(self):
        if len(self.pot) > 1:
            if self.pot[-1] == ['blue', 1]:
                if len(self.pot) > 1 and self.pot[-2] == ['white', 1]:
                    self.rubies += 1
            if self.pot[-1] == ['blue', 2]:
                if len(self.pot) > 1 and self.pot[-2] == ['white', 1]:
                    self.rubies += 1
                if len(self.pot) > 2 and self.pot[-3] == ['white', 1]:
                    self.rubies += 1
            if self.pot[-1] == ['blue', 4]:
                if len(self.pot) > 1 and self.pot[-2] == ['white', 1]:
                    self.rubies += 1
                if len(self.pot) > 2 and self.pot[-3] == ['white', 1]:
                    self.rubies += 1
                if len(self.pot) > 3 and self.pot[-4] == ['white', 1]:
                    self.rubies += 1
                if len(self.pot) > 4 and self.pot[-5] == ['white', 1]:
                    self.rubies += 1

    # "Your first placed yellow chip is moved 1 extra space, the 2nd yellow chip 2 extra spaces and the 3rd yellow chip 3 extra spaces"
    # Cost: 8 | 12 | 18
    def yellowRule0(self):
        num_yellow = len([chip for chip in self.pot if chip[0] == 'yellow']) - 1
        if self.pot[-1][0] == 'yellow':
            if num_yellow == 0:
               self.current_position += 1
            if num_yellow == 1:
               self.current_position += 2
            if num_yellow == 2:
               self.current_position += 3

    # "For 1, 2 or 3 purple chips you receive the indicated bonus. 1: 1VP, 2: 1VP+1Ruby 3: 2VP+1Drop"
    # Cost: 9
    def purpleRule0(self):
        num_purple = len([chip for chip in self.pot if chip[0] == 'purple'])
        if num_purple == 1:
            self.vp += 1
        if num_purple == 2:
            self.vp += 1
            self.rubies += 1
        if num_purple >= 3:
            self.vp += 2
            self.drop_position += 1

    # --- END ---

    # Converts the object into a JSON object for easier parsability
    def as_dict(self):
        result = {
            'bag' : self.bag.content,
            'pot' : self.pot, 
            'drop_pos' : self.drop_position,
            'current_pos' : self.current_position,
            'current_score' : self.board(),
            'rats' : self.rats,
            'money' : self.money,
            'tmp_vp' : self.tmp_vp,
            'vp' : self.vp,
            'rubies' : self.rubies,
            'stopped' :self.stopped,
            'exploded' : self.exploded,
            'bought' : self.bought,
            'bought_': self.bought_
            
        }
        return result

