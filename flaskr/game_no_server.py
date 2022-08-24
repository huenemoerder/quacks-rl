import json
import random
#from fadb import get_db
from flaskr.game_state import GameState

# save the current gamestate in the database. You can use this to look it up later of read from the db.
# def save_gamestate_in_db():
#     t_c = int(gamestate.getTurncount())
#     s = str(gamestate.getState())
#     p = str(gamestate.getPlayers().as_dict())
#     db = get_db()
#     db.execute(
#         'INSERT INTO gamestate (turn, state, player)'
#         ' VALUES (?, ?, ?)',
#         (t_c, s, p)
#     )
#     db.commit()
#     print("Snapshot saved in db")

class game_server():

    def start(self, num_player):
       # print("Starting Game")
        self.gamestate = GameState(num_player)
        gs_dict = self.gamestate.as_dict()
        # save_gamestate_in_db()
        #print("Gamestate created")
        JSON_msg = {
            'state': gs_dict,
            'player_info': ''
        }
        return JSON_msg

    def brew(self):
        state = {
            'turn_count' : self.gamestate.getTurncount(),
            'state' : self.gamestate.getState(),
            #'player_info' : gamestate.getPlayers()
        }
        player = self.gamestate.getPlayers().as_dict()
        player_info = {
            'pot': player['pot'],
            'drop_position': player['drop_pos'],
            'current_position': player['current_pos'],
            'current_score': player['current_score'],
            'money': player['money'],
            'current_vp': player['tmp_vp'],
            'total_vp': player['vp'],
            'rubies': player['rubies'],
            'exploded': player['exploded'],
            'bag': player['bag'],
            'bought': player['bought'],
            'bought_': player['bought_']
        }

        JSON_msg = {
           'state': state,
            'player_info': player_info
        }
        return JSON_msg

    def draw_one(self):
        #print(self.gamestate.getState())
#         if self.gamestate.getState() != 0:
#             print('Illegal Action') 
#             return self.brew()
        player = self.gamestate.getPlayers()
        player.pick()
        return self.brew()

    def stop_brewing(self):
#         if self.gamestate.getState() !=  0:
#             #print('Illegal Action') 
#             player = self.gamestate.getPlayers()
#             playerDict = player.as_dict()
#             player_info = {
#             'money': playerDict['money'],
#             'ingredients_left': 2 - len(playerDict['bought']),
#             'rubies': playerDict['rubies']
#             }
#             JSON_msg = {
#                 'state': self.gamestate.getState(),
#                 'player_info': player_info
#             }
#             return JSON_msg
        player = self.gamestate.getPlayers()
        player.stopBrewing(first=False)
        self.gamestate.setState(1)
        state = self.gamestate.getState()
        turn = self.gamestate.getTurncount()
        # save_gamestate_in_db()
        #print("You stopped BREWING")

        playerDict = player.as_dict()
        player_info = {
            'money': playerDict['money'],
            'ingredients_left': 2 - len(playerDict['bought']),
            'rubies': playerDict['rubies']
        }
        if turn == 9:
            #print("Last Turn - No buying phase!")
            player.setVP(player.getTmpVP())
            self.gamestate.end_game()
            player = self.gamestate.getPlayers().as_dict()
            player_info = {
                'total_vp': player['vp']
            }
            # save_gamestate_in_db()
            JSON_msg = {
                'state': 'GAME OVER',
                'player_info': player_info
            }
            return JSON_msg
        elif len(playerDict['bought']) >= 1:
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg
        elif player.exploded:
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg
        else:
            player.setVP(player.getTmpVP())

            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg

    def decision(self, decision):
        player = self.gamestate.getPlayers()
#         if not player.exploded:
#             #print('Illegal Action')
#             return {'action':'Decision-Illegal'}
        turn = self.gamestate.getTurncount()
        if turn < 9:
            dec = decision
            player = self.gamestate.getPlayers()
            playerDict = player.as_dict()
            player_info = {
                'money': playerDict['money'],
                'ingredients_left': 2 - len(playerDict['bought']),
                'rubies': playerDict['rubies']
            }
            if dec == 'vp':
                player.setVP(player.getTmpVP())
                JSON_msg = {
                    'action': 'Decision-VP'
                }
                return JSON_msg
            if dec == 'buy':
                JSON_msg = {
                    'action': 'Decision-Buy'
                }
                return JSON_msg
        else:
            pass

    def buy_one(self, ingredient_param, cost_param):
#         if self.gamestate.getState() != 1:
#             #print('Illegal Action') 
#             player = self.gamestate.getPlayers()
#             playerDict = player.as_dict()
#             player_info = {
#             'money': playerDict['money'],
#             'ingredients_left': 2 - len(playerDict['bought']),
#             'rubies': playerDict['rubies']
#             }
#             JSON_msg = {
#                 'state': self.gamestate.getState(),
#                 'player_info': player_info
#             }
#             return JSON_msg
        turn = self.gamestate.getTurncount()
        ingredient = [ingredient_param[0], int(ingredient_param[1])]
        cost = int(cost_param)
        player = self.gamestate.getPlayers()
        #print(ingredient[0])
        if ingredient[0] == 'yellow':
            if turn < 2:
                #print('what?')
                return "You are not allowed to buy a yellow chip yet."
        if ingredient[0] == 'purple':
            if turn < 3:
                return "You are not allowed to buy a purple chip yet."
        player.buy(ingredient, cost)
        playerDict = player.as_dict()
        player_info = {
            'money': playerDict['money'],
            'ingredients_left': 2 - len(playerDict['bought']),
            'rubies': playerDict['rubies']
        }
        JSON_msg = {
            'state': 'Buying',
            'player_info': player_info
        }
        return JSON_msg


    def use_rubies(self):
#         if self.gamestate.getState() != 1:
#             #print('Illegal Action') 
#             player = self.gamestate.getPlayers()
#             playerDict = player.as_dict()
#             player_info = {
#             'money': playerDict['money'],
#             'ingredients_left': 2 - len(playerDict['bought']),
#             'rubies': playerDict['rubies']
#             }
#             JSON_msg = {
#                 'state': 'BUYING',
#                 'player_info': player_info
#             }
#             return JSON_msg
        #print("Exchanging rubies")
        player = self.gamestate.getPlayers()
        player.moveDrop()
        playerDict = player.as_dict()
        player_info = {
            'money': playerDict['money'],
            'ingredients_left': 2 - len(playerDict['bought']),
            'rubies': playerDict['rubies']
        }     
        JSON_msg = {
            'state': 'BUYING',
            'player_info': player_info
        }
        return JSON_msg

    def end_turn(self):
#         if self.gamestate.getState() != 1:
#             #print('Illegal Action') 
#             player = self.gamestate.getPlayers().as_dict()
#             player_info = {
#                 'pot': player['pot'],
#                 'drop_position': player['drop_pos'],
#                 'current_position': player['current_pos'],
#                 'current_score': player['current_score'],
#                 'money': player['money'],
#                 'total_vp': player['vp'],
#                 'rubies': player['rubies'],
#                 'exploded': player['exploded']
#             }

#             JSON_msg = {
#                 'state': self.gamestate.getState(),
#                 'player_info': player_info
#             }
#             return JSON_msg
        #print("Turn ends - You can start BREWING")
        self.gamestate.setState(0)
        turn = self.gamestate.next_turn()
        # save_gamestate_in_db()
        if turn <= 9:
            state = {
                'turn_count': self.gamestate.getTurncount(),
                'state': self.gamestate.getState(),
                'player_info': self.gamestate.getPlayers()
            }
            player = self.gamestate.getPlayers().as_dict()
            player_info = {
                'pot': player['pot'],
                'drop_position': player['drop_pos'],
                'current_position': player['current_pos'],
                'current_score': player['current_score'],
                'money': player['money'],
                'total_vp': player['vp'],
                'rubies': player['rubies'],
                'exploded': player['exploded']
            }

            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg

    def set_seed(self, seed):
        random.seed(seed)