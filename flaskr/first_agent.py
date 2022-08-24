import json
import requests
from util import *
from types import SimpleNamespace
## This is a very(!) simple client that simply draws 3 Ingredients
#  and then stops. With 3 Chips it is impossible to explode (draw
#  3 + 2 + 2 <= 7 is worst case).

url = 'http://127.0.0.1:5000/'
EXPLODE_THRESHOLD = 7
NUM_ROUNDS = 9


def brewing():
    global gamestate
    exploded = False
    chance_to_explode = 0
    threshold = 0.3
    while (not exploded) and chance_to_explode < threshold:
        # print(str(draw()))
        state = draw().json()
        gamestate = json.loads(json.dumps(state["player_info"]), object_hook=lambda d: SimpleNamespace(**d))
        bag = gamestate.bag
        exploded = gamestate.exploded
        pot = state["player_info"]["pot"]
        white_sum = sum(list(map(lambda white: white[1], list(filter(lambda ingredient: ingredient[0] == "white", pot)))))
        whites_allowed = EXPLODE_THRESHOLD - white_sum
        whites_that_would_explode = len(list(filter(lambda ingredient: ingredient[0] == "white" and ingredient[1] > whites_allowed, bag)))
        chance_to_explode = 0 if whites_that_would_explode == 0 else whites_that_would_explode / len(bag) 
        # print("chance to explode = " + str(chance_to_explode))
        # print(f"droplet position: {gamestate.drop_position}")
    stop_brewing()
    return exploded
         

def buying(turn):
    affordable = list(filter(lambda ingredient: ingredient[2] <=gamestate.money, prices_orange_blue))
    most_expensive = max(affordable, key = lambda ingredient: ingredient[2])
    buy_one(*most_expensive)
    money_left = gamestate.money - most_expensive[2]
    if money_left >= 3:
        buy_one("orange", 1, 1)
    # if turn < 7:
    for i in range(gamestate.rubies//2):
        use_rubies()
    if turn != 9:
        end_turn()
    return get_state()



def main():
    vps = []
    for i in range(0,100):
        print(f"Playing game {i}. ", end="") 
        #start game with one player
        start_game()

        #print(r.status_code, r.reason, r.text)

        for i in range(0,NUM_ROUNDS):
            exploded = brewing()
            if exploded:
                if i < 5:
                    decision("buy")
                    re = buying(i)
                else:
                    decision("vp")
                    if i != NUM_ROUNDS - 1:
                        end_turn()
                    re = get_state()

            else:
                re = buying(i)
        vp = re.json()["player_info"]["total_vp"]
        vps.append(vp)
        print(f"Received {vp} victory points.")
    avg_vp = sum(vps)/len(vps)
    print(f"Over 100 games the agent received {avg_vp} on average")


if __name__ == "__main__":
    main()