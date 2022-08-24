import json
import requests

## This is a very(!) simple client that simply draws 3 Ingredients
#  and then stops. With 3 Chips it is impossible to explode (draw
#  3 + 2 + 2 <= 7 is worst case).

url = 'http://127.0.0.1:5000/'

def draw():
    # Send the request to buy a ingredient
    r = requests.post(url= url + 'draw_one')#, json=start_game)
    #print(r.status_code, r.reason, r.text)
    # call the brew function to receive active gamestate
    r2 = requests.post(url=url + 'brew')
    print(r2.text)


def main():
    #start game with one player
    r = requests.post(url=url + '1/start')
    #print(r.status_code, r.reason, r.text)

    for i in range(0, 3):
        draw()

    # stop brewing after drawing 3 Ingredients to be safe.
    r = requests.post(url=url + 'stop_brewing')
    print(r.status_code, r.reason, r.text)


if __name__ == "__main__":
    main()
