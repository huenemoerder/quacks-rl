from flaskr.player import Player

# The Gamestate as an Object.
# The Gamestate contains all information available: Players, the state the Game is in [BREWING, BUYING], and the
# turncounter from 1 to 9.
# STATE BREWING = 0, BUYING = 1, ENDED = 2

class GameState(object):

    def __init__(self, num_players):
        self.turn_count = 1
        self.state = 0
        self.players = []
        self.num_players = num_players
        self.rule_set = {'orange': 0, 'green': 0, 'red': 0, 'blue': 0, 'yellow': 0, 'purple': 0, 'black': 0}

        # Create as many players as selected, 1 for now
        for _ in range(num_players):
            self.players.append(Player(self.rule_set))

        #print('GameState Object created.')

    def as_dict(self):
        # Converts the object into a JSON object for easier parsability
        result = {
            'turn_count' : self.turn_count,
            'state' : self.state,
            'numberOfPlayers' : self.num_players,
            'players_info' : self.players[0].as_dict()
        }
        return result

    # Getter and setter for different variables
    def getTurncount(self):
        return self.turn_count

    def getState(self):
        return self.state

    def setState(self, state):
        self.state = state

    def getPlayers(self):
        return self.players[0]

    # end one turn and start the next one
    def next_turn(self):
        self.players[0].endTurn()
        if self.turn_count < 9: ### Added by Nanni and Miri 27.04
            self.turn_count += 1
        return self.turn_count

    # end the entire game and give VP to the players with remaining stuff
    def end_game(self):
        #print('Game Ended')
        self.state = 2
        # Each set of 2 rubies gives you 1 additional VP
        end_vp_rubies = self.players[0].rubies // 2
        #print("You got", end_vp_rubies, "VP from your Rubies, ")
        # For every 5 money you also get 1 VP
        end_vp_money = 0
        if not self.players[0].exploded:
            end_vp_money = self.players[0].money // 5
        #print("and", end_vp_money, "VP from your Money, total of ", end_vp_money + end_vp_rubies, "VP")
        self.players[0].setVP(end_vp_rubies + end_vp_money)
        self.players[0].endTurn()



