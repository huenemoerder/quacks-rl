import functools
import json
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.game_state import GameState
import random

bp = Blueprint('game', __name__)

## This is the class that collects all functionalities and actions the game has to offer.
# Each action is coupled with an html file to display the gamestate in a browser but also returns a JSON file
# if an Agent (see client.py) requests things.

# save the current gamestate in the database. You can use this to look it up later of read from the db.
def save_gamestate_in_db():
    t_c = int(gamestate.getTurncount())
    s = str(gamestate.getState())
    p = str(gamestate.getPlayers().as_dict())
    db = get_db()
    db.execute(
        'INSERT INTO gamestate (turn, state, player)'
        ' VALUES (?, ?, ?)',
        (t_c, s, p)
    )
    db.commit()
    print("Snapshot saved in db")


# Start a game with a certain number of players (1 for now).
# A new gamestate is created as well as the players taking part in the game.
@bp.route('/<int:num_player>/start', methods=('GET', 'POST'))
def start(num_player):
    print("Starting Game with", num_player, "player(s).")
    global gamestate
    gamestate = GameState(num_player)
    gs_dict = gamestate.as_dict()
    save_gamestate_in_db()
    print("Gamestate created")
    if request.method == 'GET':
        return render_template('game/brew.html', state=gs_dict, player={})
    if request.method == 'POST':
        JSON_msg = {
            'state': gs_dict,
            'player_info': ''
        }
        return JSON_msg


# this displays (or returns) the gamestate in the brewing state
@bp.route('/brew', methods=('GET', 'POST'))
def brew():
    state = {
        'turn_count' : gamestate.getTurncount(),
        'state' : gamestate.getState(),
        #'player_info' : gamestate.getPlayers()
    }
    player = gamestate.getPlayers().as_dict()
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
    if request.method == 'GET':
        return render_template('game/brew.html', state=state, player=player_info)
    if request.method == 'POST':
        JSON_msg = {
            'state': state,
            'player_info': player_info
        }
        return JSON_msg


# action: Draw an Ingredient from the players bag
@bp.route('/draw_one', methods=('GET', 'POST'))
def draw_one():
    player = gamestate.getPlayers()
    player.pick()
    return redirect(url_for('game.brew'))


# action: Stop brewing if you did not already explode.
# You will go to the next state, which is buying.
@bp.route('/stop_brewing', methods=('GET', 'POST'))
def stop_brewing():
    player = gamestate.getPlayers()
    player.stopBrewing(first=False)
    gamestate.setState('BUYING')
    state = gamestate.getState()
    turn = gamestate.getTurncount()
    save_gamestate_in_db()
    print("You stopped BREWING")

    playerDict = player.as_dict()
    player_info = {
        'money': playerDict['money'],
        'ingredients_left': 2 - len(playerDict['bought']),
        'rubies': playerDict['rubies']
    }
    if turn == 9:
        print("Last Turn - No buying phase!")
        player.setVP(player.getTmpVP())
        gamestate.end_game()
        player = gamestate.getPlayers().as_dict()
        player_info = {
            'total_vp': player['vp']
        }
        save_gamestate_in_db()
        if request.method == 'GET':
            return render_template('game/gameover.html', player=player_info)
        if request.method == 'POST':
            JSON_msg = {
                'state': 'GAME OVER',
                'player_info': player_info
            }
            return JSON_msg
    elif len(playerDict['bought']) >= 1:
        if request.method == 'GET':
            return render_template('game/buy.html', player=player_info)
        if request.method == 'POST':
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg
    elif player.exploded:
        if request.method == 'GET':
            return render_template('game/decide.html')
        if request.method == 'POST':
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg
    else:
        player.setVP(player.getTmpVP())
        if request.method == 'GET':
            return render_template('game/buy.html', player=player_info)
        if request.method == 'POST':
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg


# If you did explode you need to decide if you want Victory Points or Buy Ingredients
@bp.route('/decision', methods=('GET', 'POST'))
def decision():
    turn = gamestate.getTurncount()
    if turn < 9:
        dec = request.args.get('decision')
        player = gamestate.getPlayers()
        playerDict = player.as_dict()
        player_info = {
            'money': playerDict['money'],
            'ingredients_left': 2 - len(playerDict['bought']),
            'rubies': playerDict['rubies']
        }
        if dec == 'vp':
            player.setVP(player.getTmpVP())
            if request.method == 'GET':
                return redirect(url_for('game.end_turn'))
            if request.method == 'POST':
                JSON_msg = {
                    'action': 'Decision-VP'
                }
                return JSON_msg
        if dec == 'buy':
            if request.method == 'GET':
                return render_template('game/buy.html', player=player_info)
            if request.method == 'POST':
                JSON_msg = {
                    'action': 'Decision-Buy'
                }
                return JSON_msg
    else:
        pass


# action: Get the prices for the selected rules
@bp.route('/get_prices', methods=('GET', 'POST'))
def get_prices():
    player = gamestate.getPlayers()
    prices = player.getPrices()
    if request.method == 'GET':
        return 0
    if request.method == 'POST':
        JSON_msg = {
            'prices': prices
        }
        return JSON_msg


# action: Buy a certain ingredient
@bp.route('/buy_one', methods=('GET', 'POST'))
def buy_one():
    turn = gamestate.getTurncount()
    ingredient_param = request.args.getlist('ingredient')
    ingredient = [ingredient_param[0], int(ingredient_param[1])]
    cost_param = request.args.get('cost')
    cost = int(cost_param)
    player = gamestate.getPlayers()
    if ingredient[0] == 'yellow':
        if turn < 2:
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
    if request.method == 'GET':
        return render_template('game/buy.html', player=player_info)
    if request.method == 'POST':
        JSON_msg = {
            'state': 'BUYING',
            'player_info': player_info
        }
        return JSON_msg


# action: Spend 2 rubies to move your drop ((Later: Fill up your potion))
@bp.route('/use_rubies', methods=('GET', 'POST'))
def use_rubies():
    print("Exchange your rubies")
    player = gamestate.getPlayers()
    player.moveDrop()
    playerDict = player.as_dict()
    player_info = {
        'money': playerDict['money'],
        'ingredients_left': 2 - len(playerDict['bought']),
        'rubies': playerDict['rubies']
    }
    if request.method == 'GET':
        return render_template('game/buy.html', player=player_info)
    if request.method == 'POST':
        JSON_msg = {
            'state': 'BUYING',
            'player_info': player_info
        }
        return JSON_msg


# End the buying state and your turn. The next turn will start with BREWING again.
# If you already played 9 turns the game will end.
@bp.route('/end_turn', methods=('GET', 'POST'))
def end_turn():
    print("Turn ends - You can start BREWING")
    gamestate.setState('BREWING')
    turn = gamestate.next_turn()
    ### Was an idea when debugging Nanni and Miri on 27.04
    #if gamestate.turn_count() < 9:
    #    turn = gamestate.next_turn()
    #else:
    #    turn = gamestate.turn_count()
    save_gamestate_in_db()
    if turn <= 9:
        state = {
            'turn_count': gamestate.getTurncount(),
            'state': gamestate.getState(),
            'player_info': gamestate.getPlayers()
        }
        player = gamestate.getPlayers().as_dict()
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
        if request.method == 'GET':
            return render_template('game/brew.html', state=state, player=player_info)
        if request.method == 'POST':
            JSON_msg = {
                'state': state,
                'player_info': player_info
            }
            return JSON_msg
    else:
        print("Some Error that should never occur...")

@bp.route('/setseed', methods=('GET', 'POST'))
def set_seed():
    random.seed(request.args['seed'])
    return render_template('game/index.html')


# Redirect for anything not implemented yet.
@bp.route('/notimplemented', methods=('GET', 'POST'))
def not_implemented():
    # This is a redirector for everything that is not implemented yet.
    return render_template('game/index.html')


# Access to the database. Simply type url+/histoy to see all safed gamestates
@bp.route('/history', methods=('GET', 'POST'))
def history():
    db = get_db()
    gs_db = db.execute(
        'SELECT *'
        ' FROM gamestate'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('game/history.html', gamestate=gs_db)

#'starting page when you enter the url
@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'GET':
        return render_template('game/index.html')
    if request.method == 'POST':
        JSON_msg = {
            'state': 'START GAME'}
        return JSON_msg

