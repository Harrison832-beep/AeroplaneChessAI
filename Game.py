from Agent import AeroplaneChessAgent, RandomAgent, ExpectimaxAgent
import random, os
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from GameBoard import Plane, GameBoard, GameState
from utils import NUM_SQUARES, OPPONENT, AGENT1

colorama_init()


class Player:
    def __init__(self, color: str, agent: AeroplaneChessAgent = None):
        if agent is None:
            self.agent = RandomAgent(color)
        else:
            self.agent = agent  # TODO: add agent
        self.planes = [Plane(color, i) for i in range(4)]
        self.color = color

    @staticmethod
    def roll_die():
        return random.randint(1, 6)

    def take_action(self, state: GameState) -> (Plane, int):
        die_v = Player.roll_die()
        a = self.agent.get_action(state, die_v)
        return a, die_v

    def get_movable_planes(self, die_v: int) -> list[int]:
        """
        Given die roll, list indices of all planes of a player
        Movable planes are:
        * On launch pad
        * On main track
        * On final stretch
        """
        inx = []
        for i in range(len(self.planes)):
            plane = self.planes[i]
            if plane.is_on_launch() or plane.is_on_main_track() or plane.is_on_final_stretch():
                inx.append(i)
            elif plane.is_on_hangar() and die_v == 6:
                inx.append(i)
        return inx

    def get_remaining_planes_count(self) -> int:
        """
        Check how many planes left to win
        """
        return sum([True for plane in self.planes if not plane.is_finished()])

    def __repr__(self):
        return self.color


class Game:
    def __init__(self, num_players: int):
        assert num_players == 2
        # Blue player has Green as opponent, green player is the only player that can catch blue in final stretch
        # Now consider only two players

        if AGENT1 == 'Expectimax':
            players = [Player('B', agent=ExpectimaxAgent('B')), Player('G')]
        else:
            players = [Player('B'), Player('G')]

        turn = 0  # Player 1
        self.is_over = False
        self.state = GameState(players, turn)

    def player_move(self):
        cur_player = self.state.players[self.state.turn]
        action, die_v = cur_player.take_action(self.state)
        print(f"{cur_player.color} player rolled Die: {die_v}")
        new_state = self.state.generateSuccessor(action, die_v, show_event=True)
        self.state = new_state

        if action is not None:
            print(f"{Fore.RED}Player {cur_player} moved plane {action}{Style.RESET_ALL}")
        # game over state: a player has all planes with state "Finish"
        if self.state.is_win(cur_player.color):
            print(f"{Fore.RED}Player {cur_player} wins the game!{Style.RESET_ALL}")
            self.is_over = True
        elif self.state.is_lose(cur_player.color):  # Consider only two players
            print(f"{Fore.RED}Player {OPPONENT[cur_player.color]} wins the game!{Style.RESET_ALL}")
            self.is_over = True
        else:
            print(f"{cur_player.get_remaining_planes_count()} planes left.")

    def show(self):
        print(self.state.gameboard)



def start_game():
    game = Game(num_players=2)
    game.show()
    while not game.is_over:
        input('Type enter to continue...')
        game.player_move()
        game.show()


if __name__ == '__main__':
    start_game()
