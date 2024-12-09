import collections
import optparse
import time
from copy import deepcopy
from sys import argv
from typing_extensions import Self

from Agent import AeroplaneChessAgent, RandomAgent, ExpectimaxAgent, MCTSAgent, RLAgent
import random, os
from argparse import ArgumentParser

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

from GameBoard import Plane, GameBoard, GameState
from utils import NUM_SQUARES, OPPONENT, AGENT1, roll_die, CONFIG

colorama_init()


class Player:
    def __init__(self, color: str, agent: AeroplaneChessAgent = None):
        if agent is None:
            self.agent = RandomAgent(color)
        else:
            self.agent = agent
        self.planes = [Plane(color, i) for i in range(4)]
        self.color = color
        self.decision_time_record = []

    def take_action(self, state: GameState) -> (Plane, int):
        die_v = roll_die(state)

        start = time.time()
        a = self.agent.get_action(state, die_v)
        self.decision_time_record.append(time.time() - start)
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

    def __eq__(self, other: Self):
        if self.color != other.color:
            return False

        for i, plane1 in enumerate(self.planes):
            plane2 = other.planes[i]
            if plane1 != plane2:
                return False
        return True

    def __repr__(self):
        return self.color

    def __hash__(self):
        return hash(tuple([plane for plane in self.planes]))

    def __deepcopy__(self, memodict={}):
        copy_self = Player(self.color, self.agent)
        copy_self.planes = deepcopy(self.planes, memodict)
        copy_self.decision_time_record = deepcopy(self.decision_time_record, memodict)
        return copy_self


class Game:
    def __init__(self, num_players: int):
        assert num_players == 2
        # Blue player has Green as opponent, green player is the only player that can catch blue in final stretch
        # Now consider only two players

        if AGENT1 == 'Expectimax':
            players = [Player('B', agent=ExpectimaxAgent('B')), Player('G')]
        elif AGENT1 == 'MCTS':
            players = [Player('B', agent=MCTSAgent('B')), Player('G')]
        elif AGENT1 == 'RL':
            players = [Player('B', agent=RLAgent('B')), Player('G')]
        else:
            players = [Player('B'), Player('G')]

        turn = 0  # Player 1
        self.is_over = False
        self.state = GameState(players, turn)
        self.winner = None
        self.decision_time_sum = {}

    def player_move(self):
        cur_player = self.state.players[self.state.turn]
        action, die_v = cur_player.take_action(self.state)

        event_log = ""
        event_log += f"{cur_player.color} player rolled Die: {die_v}\n"

        self.state = self.state.generate_successor(action, die_v, show_event=CONFIG['display'])

        if action is not None:
            event_log += f"{Fore.RED}Player {cur_player} moved plane {action}{Style.RESET_ALL}\n"
        # game over state: a player has all planes with state "Finish"
        if self.state.is_win(cur_player.color):
            print(f"{Fore.RED}Player {cur_player} wins the game!{Style.RESET_ALL}")
            self.is_over = True
            self.winner = cur_player.color
        elif self.state.is_lose(cur_player.color):  # Consider only two players
            print(f"{Fore.RED}Player {OPPONENT[cur_player.color]} wins the game!{Style.RESET_ALL}")
            self.is_over = True
            self.winner = OPPONENT[cur_player.color]
        else:
            event_log += f"{cur_player.get_remaining_planes_count()} planes left.\n"

        if CONFIG['display']:
            print(event_log)

        if self.is_over:
            for player in self.state.players:
                self.decision_time_sum[str(player.agent)] = sum(player.decision_time_record)

    def show(self):
        print(self.state.gameboard)


def start_game():
    if CONFIG['no-graphics']:
        winner_history = []
        decision_time_history = {}  # Store total decision time for all games

        if AGENT1 == 'RL':
            for i in range(1000):
                print(f"Playing {i+1}th game (Training)...")
                game = Game(num_players=2)
                while not game.is_over:
                    game.player_move()

        for i in range(100):
            print(f"Playing {i+1}th game...")
            game = Game(num_players=2)
            start = time.time()
            while not game.is_over:
                game.player_move()
            print(f"Game finish time: {time.time() - start}")
            winner_history.append(game.winner)
            for k, v in game.decision_time_sum.items():
                decision_time_history[k] = decision_time_history.get(k, []) + [v]

        for k, v in decision_time_history.items():
            decision_time_history[k] = sum(v) / len(v)
        counter = collections.Counter(winner_history)
        print("Winner summary:", counter)
        print("Decision time average:", decision_time_history)

    else:
        game = Game(num_players=2)
        game.show()
        while not game.is_over:
            input('Type enter to continue...')
            game.player_move()
            game.show()


if __name__ == '__main__':
    start_game()
