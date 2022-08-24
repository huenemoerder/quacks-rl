import tensorflow 
import numpy as np

from flaskr.util import *
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts

TURN = 0
RUBIES_OWNED = 1
DROPLET_POSITION = 2
CURRENT_POSITION = 3
RUBY_ON_CURRENT_POSITION = 4
STEPS_UNTIL_NEXT_RUBY = 5
VP_ON_CURRENT_POSITION = 6
MONEY_ON_CURRENT_POSITION = 7
NUMBER_WHITE_CHIPS_IN_CAULDRON = 8
IS_LAST_CHIP_IN_CAULDRON_GREEN = 9
IS_SECOND_TO_LAST_CHIP_IN_CAULDRON_GREEN = 10
POT_HAS_1_OR_2_ORANGE_CHIPS = 11
POT_HAS_MORE_THAN_2_ORANGE_CHIPS = 12
NUM_WHITE_1_CHIPS_IN_BAG = 13
NUM_WHITE_2_CHIPS_IN_BAG = 14
NUM_WHITE_3_CHIPS_IN_BAG = 15
NUM_GREEN_1_CHIPS_IN_BAG = 16
NUM_GREEN_2_CHIPS_IN_BAG = 17
NUM_GREEN_4_CHIPS_IN_BAG = 18
NUM_RED_1_CHIPS_IN_BAG = 19
NUM_RED_2_CHIPS_IN_BAG = 20
NUM_RED_4_CHIPS_IN_BAG = 21
NUM_BLUE_1_CHIPS_IN_BAG = 22
NUM_BLUE_2_CHIPS_IN_BAG = 23
NUM_BLUE_4_CHIPS_IN_BAG = 24
NUM_YELLOW_1_CHIPS_IN_BAG = 25
NUM_YELLOW_2_CHIPS_IN_BAG = 26
NUM_YELLOW_4_CHIPS_IN_BAG = 27
NUM_PURPLE_1_CHIPS_IN_BAG = 28
NUM_ORANGE_1_CHIPS_IN_BAG = 29
TOTAL_CHIPS_IN_BAG =  30
BOUGHT_CHIP_GREEN = 31
BOUGHT_CHIP_RED = 32
BOUGHT_CHIP_BLUE = 33
BOUGHT_CHIP_YELLOW = 34
BOUGHT_CHIP_PURPLE = 35
BOUGHT_CHIP_ORANGE = 36
MONEY_TO_BUY = 37
IN_DRAWING = 38
IN_DECISION_AFTER_EXPLODE = 39
IN_BUYING = 40
IN_BUYING_DROPLET = 41

RESET_STATE = [1, 1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 4, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 9, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]

NUM_ACTIONS = 20

class QuacksEnv(py_environment.PyEnvironment):

    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=19, name='action')
        self._observation_spec = {'observation': array_spec.BoundedArraySpec(
            shape=(42,), dtype=np.float32, 
            minimum=[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            maximum=[9, 20, 53, 53, 1, 4, 15, 35, 10, 1, 1, 1, 1, 4, 2, 1, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 30, 1, 1, 1, 1, 1, 1, 35, 1, 1, 1, 1],
            name='observation'),
            'legal_moves': array_spec.ArraySpec(shape=(NUM_ACTIONS,), dtype=np.bool_)}
        self._state = RESET_STATE
        self._episode_ended = False
        self._reward_this_turn = 0
        #print('Init here')

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self._state = RESET_STATE
        self._episode_ended = False
        
        start_game()
        
        obs = {}
        obs["observation"] = np.array(self._state).astype(np.float32)
        obs["legal_moves"] = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]).astype(np.bool_)
        return ts.restart(obs)

    def buy(self, ingredient, worth, cost):
        #print(get_state())
        buy_one(ingredient, worth, cost)
        #print(get_state())
        self._state = self.get_state_as_list(get_state())
        obs = {}
        obs["observation"] = np.array(self._state, dtype=np.float32)
        obs["legal_moves"] = np.asarray(self.get_buy_legal_moves(self._state[MONEY_TO_BUY], self._state[RUBIES_OWNED])).astype(np.bool_)
        #print(obs)
        return ts.transition(obs, reward=0, discount=1.0)

    def _step(self, action):
        
        if self._episode_ended:
            # The last action ended the episode. Ignore the current action and start
            # a new episode.
            return self.reset()

        if action == 0:
            turn = self.get_state_as_list(get_state())[TURN]
            intermediate = self.get_state_as_list(get_state())
            stop_brewing()
            reward = self._state[VP_ON_CURRENT_POSITION]
            self._state = self.get_state_as_list(get_state())
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            obs["legal_moves"] = np.array(self.get_buy_legal_moves(self._state[MONEY_TO_BUY], self._state[RUBIES_OWNED]), dtype=np.bool_)

            if turn >= 9:
                obs["legal_moves"] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
                self._episode_ended = True
                x = self._state[RUBIES_OWNED] // 2
                y = intermediate[MONEY_ON_CURRENT_POSITION] // 5
                reward += x + y
                reward = float(reward)
                return ts.termination(obs, reward=reward)
            else:
                reward = float(reward)
                return ts.transition(obs, reward=reward, discount=1.0)

        elif action == 1:
            draw()
            intermediate = self.get_state_as_list(get_state())
            if intermediate[NUMBER_WHITE_CHIPS_IN_CAULDRON] > 7 or intermediate[CURRENT_POSITION] > 52:
                stop_brewing()
            self._state = self.get_state_as_list(get_state())
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            obs["legal_moves"] = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
            if intermediate[NUMBER_WHITE_CHIPS_IN_CAULDRON] > 7 or intermediate[CURRENT_POSITION] > 52:
                obs["legal_moves"] = np.array([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
            if (intermediate[NUMBER_WHITE_CHIPS_IN_CAULDRON] > 7 or intermediate[CURRENT_POSITION] > 52) and self._state[TURN] >= 9:
                reward = intermediate[VP_ON_CURRENT_POSITION]
                reward += self._state[RUBIES_OWNED] // 2
                obs["legal_moves"] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
                self._episode_ended = True
                return ts.termination(obs, reward=reward)
            return ts.transition(obs, reward=0., discount=1.0)

        elif action == 2:
            decision("buy")
            self._state = self.get_state_as_list(get_state())
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            obs["legal_moves"] = np.asarray(self.get_buy_legal_moves(self._state[MONEY_TO_BUY], self._state[RUBIES_OWNED])).astype(np.bool_)
            return ts.transition(obs, reward=0., discount=1.0)

        elif action == 3:
            decision("vp")
            reward = self._state[VP_ON_CURRENT_POSITION]
            end_turn()
            self._state = self.get_state_as_list(get_state())
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            obs["legal_moves"] = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
            return ts.transition(obs, reward=reward, discount=1.0)

        elif action == 4:
            #print('here')
            return self.buy("orange", 1, 3)
        
        elif action == 5:
            return self.buy("green", 1, 4)

        elif action == 6:
            return self.buy("green", 2, 8)

        elif action == 7:
            return self.buy("green", 4, 14)
            
        elif action == 8:
            return self.buy("red", 1, 6)
        
        elif action == 9:
            return self.buy("red", 2, 10)

        elif action == 10:
            return self.buy("red", 4, 16)

        elif action == 11:
            return self.buy("blue", 1, 4)

        elif action == 12:
            return self.buy("blue", 2, 8)

        elif action == 13:
            return self.buy("blue", 4, 10)

        elif action == 14:
            #print('here')
            return self.buy("yellow", 1, 8)

        elif action == 15:
            return self.buy("yellow", 2, 12)

        elif action == 16:
            return self.buy("yellow", 4, 18)
        
        elif action == 17:
            return self.buy("purple", 1, 9)

        elif action == 18:
            use_rubies()
            self._state = self.get_state_as_list(get_state())
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            obs["legal_moves"] = self.get_rubies_legal_moves(self._state[RUBIES_OWNED])
            return ts.transition(obs, reward=0, discount=1.0)

        elif action == 19:
            self._state = self.get_state_as_list(get_state())
            ### added by Miri and Nanni 27.04
            turn = self._state[TURN]
            intermediate = self.get_state_as_list(get_state())
            reward = self._state[VP_ON_CURRENT_POSITION]
            ### 
            obs = {}
            obs["observation"] = np.array(self._state, dtype=np.float32)
            
            ### added by Miri and Nanni 27.04
            if turn >= 9:
                 obs["legal_moves"] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
                 self._episode_ended = True
                 x = self._state[RUBIES_OWNED] // 2
                 y = intermediate[MONEY_ON_CURRENT_POSITION] // 5
                 reward += x + y
                 reward = float(reward)
                 return ts.termination(obs, reward=reward)

            ###
            else:
                obs["legal_moves"] = np.array([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.bool_)
            
            end_turn()
            return ts.transition(obs, reward=0, discount=1.0)
           
    def get_buy_legal_moves(self, money, rubies):

        if len(get_state()["player_info"]["bought_"]) == 2:
            return self.get_rubies_legal_moves(rubies)

        if money < 3 or (self._state[BOUGHT_CHIP_ORANGE] == 1 and money < 4):
            return self.get_rubies_legal_moves(rubies) 

        legal_moves = [0 for i in range(NUM_ACTIONS)]
        legal_moves[4:18] = [1 for _ in range(14)]
        
        
        if self._state[TURN] < 2:
            legal_moves[14:17] = [0 for _ in range(3)]

        if self._state[TURN] < 3:
            legal_moves[17] = 0
        
        if self._state[BOUGHT_CHIP_ORANGE] == 1:
            legal_moves[4] = 0
        
        if self._state[BOUGHT_CHIP_GREEN] == 1:
            legal_moves[5:8] = [0 for _ in range(3)]

        if self._state[BOUGHT_CHIP_RED] == 1:
            legal_moves[8:11] = [0 for _ in range(3)]

        if self._state[BOUGHT_CHIP_BLUE] == 1:
            legal_moves[11:14] = [0 for _ in range(3)]

        if self._state[BOUGHT_CHIP_YELLOW] == 1:
            legal_moves[14:17] = [0 for _ in range(3)]

        if self._state[BOUGHT_CHIP_PURPLE] == 1:
            legal_moves[17] = 0

        if money < 18:
            legal_moves[16] = 0
        
        if money < 16:
            legal_moves[10] = 0

        if money < 14:
            legal_moves[7] = 0
        
        if money < 12:
            legal_moves[15] = 0

        if money < 10:
            legal_moves[9] = 0
            legal_moves[13] = 0

        if money < 9:
            legal_moves[17] = 0
        
        if money < 8:
            legal_moves[14] = 0
            legal_moves[12] = 0
            legal_moves[6] = 0

        if money < 6:
            legal_moves[8] = 0
        
        if money < 4:
            legal_moves[5] = 0
            legal_moves[11] = 0
                    
        if get_state()["player_info"]["rubies"] >= 2:
            legal_moves[18] = 1
        
        legal_moves[19] = 1
        return legal_moves

    def get_rubies_legal_moves(self, rubies):
        return np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, int(rubies >= 2), 1]).astype(np.bool_)
    

    def get_state_as_list(self, state):
        gamestate = state["player_info"]
        _round = state["state"]["turn_count"]
        rubies_owned = gamestate["rubies"]
        droplet_position = gamestate["drop_position"]
        current_position = gamestate["current_position"]
        ruby_on_current_position = int(gamestate["current_score"]["cur_ruby"])
        try:
            steps_until_next_ruby = rubies[current_position+1:].index(True)
        except ValueError:
            steps_until_next_ruby = 4
        vp_on_current_position = gamestate["current_vp"]
        money_current_position = int(gamestate["current_score"]["cur_money"])
        pot = gamestate["pot"]
        number_white_chips_in_cauldron = sum(list(map(lambda white: white[1], list(filter(lambda ingredient: ingredient[0] == "white", pot)))))
        is_last_chip_in_cauldron_green = 0 if len(pot) < 1 else int(pot[-1][0] == "green")
        is_second_to_last_chip_in_cauldron_green = 0 if len(pot) < 2 else int(pot[-2][0] == "green")
        pot_has_1_or_2_orange_chips = int(1 <= len(list(filter(lambda ingredient: ingredient == ["orange", 1], pot))) <= 2)
        pot_has_more_than_2_orange_chips = int(len(list(filter(lambda ingredient: ingredient == ["orange", 1], pot))) >= 2)
        bag = gamestate["bag"]
        num_white_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["white", 1], bag)))
        num_white_2_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["white", 2], bag)))
        num_white_3_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["white", 3], bag)))
        num_green_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["green", 1], bag)))
        num_green_2_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["green", 2], bag)))
        num_green_4_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["green", 4], bag)))
        num_red_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["red", 1], bag)))
        num_red_2_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["red", 2], bag)))
        num_red_4_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["red", 4], bag)))
        num_blue_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["blue", 1], bag)))
        num_blue_2_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["blue", 2], bag)))
        num_blue_4_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["blue", 4], bag)))
        num_yellow_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["yellow", 1], bag)))
        num_yellow_2_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["yellow", 2], bag)))
        num_yellow_4_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["yellow", 4], bag)))
        num_purple_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["purple", 1], bag)))
        num_orange_1_chips_in_bag = len(list(filter(lambda ingredient: ingredient == ["orange", 1], bag)))
        total_chips_in_bag = len(bag)
        bought = gamestate["bought"]
        bought_chip_green = int(len(bought) == 1  and bought[0] == "green")
        bought_chip_red = int(len(bought) == 1  and bought[0] == "red")
        bought_chip_blue = int(len(bought) == 1  and bought[0] == "blue")
        bought_chip_yellow = int(len(bought) == 1  and bought[0] == "yellow")
        bought_chip_purple = int(len(bought) == 1  and bought[0] == "purple")
        bought_chip_orange = int(len(bought) == 1  and bought[0] == "orange")
        money_to_buy = gamestate["money"]
        in_drawing = int(state["state"]["state"] == 0)
        in_decision_after_explode = int(state["state"]["state"] == 1 and gamestate['exploded'] and self._state[IN_DRAWING] == 1)
        in_buying = int( ((len(bought) < 2) and (money_to_buy >= 3 or (len(bought) != 0 and bought[0] == "orange" and money_to_buy >= 4))) and ((state["state"]["state"] == 1 and self._state[IN_DECISION_AFTER_EXPLODE] == 1) or (state["state"]["state"] == 1 and not gamestate["exploded"])))
        in_buying_droplet = int( (len(bought) == 2) or (money_to_buy < 3 or (len(bought) != 0 and bought[0] == "orange" and money_to_buy < 4)))
        
        
        return [_round, rubies_owned, droplet_position, current_position, ruby_on_current_position, steps_until_next_ruby, vp_on_current_position,
                money_current_position, number_white_chips_in_cauldron, is_last_chip_in_cauldron_green, is_second_to_last_chip_in_cauldron_green,
                pot_has_1_or_2_orange_chips, pot_has_more_than_2_orange_chips, num_white_1_chips_in_bag, num_white_2_chips_in_bag, num_white_3_chips_in_bag,
                num_green_1_chips_in_bag, num_green_2_chips_in_bag, num_green_4_chips_in_bag, num_red_1_chips_in_bag, num_red_2_chips_in_bag, num_red_4_chips_in_bag, 
                num_blue_1_chips_in_bag, num_blue_2_chips_in_bag, num_blue_4_chips_in_bag, num_yellow_1_chips_in_bag, num_yellow_2_chips_in_bag, num_yellow_4_chips_in_bag,
                num_purple_1_chips_in_bag, num_orange_1_chips_in_bag, total_chips_in_bag, bought_chip_green, bought_chip_red, bought_chip_blue, bought_chip_yellow, bought_chip_purple,
                bought_chip_orange, money_to_buy, in_drawing, in_decision_after_explode, in_buying, in_buying_droplet]
        


