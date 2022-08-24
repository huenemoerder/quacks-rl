import requests
import json

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


def draw():
    # Send the request to buy a ingredient
    r = requests.post(url=url + 'draw_one')  # , json=start_game)
    #print(r.status_code, r.reason, r.text)
    # call the brew function to receive active gamestate
    r2 = requests.post(url=url + 'brew')
    # print(r2.text)
    return r2


def stop_brewing():
    r = requests.post(url=url + 'stop_brewing')
    # print(r.status_code, r.reason, r.text)


def buy_one(ingredient_name, ingredient_worth, cost):
    r = requests.post(url=url + 'buy_one',
                      params={"ingredient": [ingredient_name, ingredient_worth], "cost": cost})
    # print(r)


def decision(decision):
    r = requests.post(url=url + 'decision', params={"decision": decision})


def end_turn():
    r = requests.post(url=url + 'end_turn')
    return r

def use_rubies():
    r = requests.post(url=url + 'use_rubies')


def start_game():
    print('here')
    r = requests.post(url=url + '1/start')
    #print(r)

def get_state():
    r = requests.post(url=url + 'brew')

    return r

def set_random_seed(seed):
    r  = requests.post(url=url + 'setseed?seed=' + str(seed))
    return r