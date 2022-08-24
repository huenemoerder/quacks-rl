import json
from flaskr.game_no_server import *

url = 'http://127.0.0.1:5000/'

prices = [["orange", 1, 3], ["green", 1, 4], ["green", 2, 8], ["green", 4, 14], ["red", 1, 6], ["red", 2, 10], ["red", 4, 16], ["blue", 1, 5], ["blue", 2, 10], ["blue", 4, 19]]
prices_orange_green = [["orange", 1, 3], ["green", 1, 4], ["green", 2, 8], ["green", 4, 14]]
prices_orange_red = [["orange", 1, 3], ["red", 1, 6], ["red", 2, 10], ["red", 4, 16]]
prices_orange_blue = [["orange", 1, 3], ["blue", 1, 5], ["blue", 2, 10], ["blue", 4, 19]]

rubies = [False, False, False, False, False, True, False, False, False, True,
          False, False, False, True, False, False, True, False, False, False,
          True, False, False, False, True, False, False, False, True, False,
          True, False, False, False, True, False, True, False, False, False,
          True, False, True, False, False, False, True, False, False, False,
          True, False, True, False]

GS = game_server()

def draw():
    #print('draw')
    #print('Turn ' + str(GS.brew()['state']['turn_count']))
    return GS.draw_one()


def stop_brewing():
    #print('Turn ' + str(game_no_server.brew()['state']['turn_count']))
    #print('stop_brewing')
    #print('Turn ' + str(GS.brew()['state']['turn_count']))
    GS.stop_brewing()


def buy_one(ingredient_name, ingredient_worth, cost):
    #print('buy_one')
    GS.buy_one([ingredient_name, ingredient_worth], cost)


def decision(decision):
    #print('decision')
    GS.decision(decision)


def end_turn():
    #print('Turn ' + str(game_no_server.brew()['state']['turn_count']))
    #print('end_turn')
    #print('Turn ' + str(GS.brew()['state']['turn_count']))
    #print('VP ' + str(GS.brew()['player_info']['total_vp']))
    #print(game_no_server.brew())
    return GS.end_turn()
    

def use_rubies():
    #print('use_rubies')
    return GS.use_rubies()


def start_game():
    #print('start_game')
    GS.start(1)

def get_state():
    return GS.brew()

def set_random_seed(seed):
    GS.set_seed(seed)