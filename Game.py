from Agent import AeroplaneChessAgent, RandomAgent
import random

from GameBoard import Plane, GameBoard


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

    def take_action(self, gameboard: GameBoard) -> (Plane, int):
        die_v = Player.roll_die()
        movable_planes = self.get_movable_planes(die_v)
        plane = None
        if len(movable_planes) > 0:
            plane = self.agent.get_action(gameboard, movable_planes, die_v)
            plane.move(die_v)
        return plane, die_v

    def get_movable_planes(self, die_v: int):
        planes = []
        for plane in self.planes:
            if plane.pos_type == 'Launch':
                planes.append(plane)
            elif plane.pos_type == 'Hanger' and die_v == 6:
                planes.append(plane)
        return planes

    def __repr__(self):
        return self.color


class Game:
    def __init__(self, num_players: int):
        assert num_players == 2
        # Blue player has Green as opponent, green player is the only player that can catch blue in final stretch
        # Now consider only two players
        self.players = [Player('B'), Player('G')]
        self.gameboard = GameBoard([plane for player in self.players for plane in player.planes])
        self.turn = 0  # Player 1
        self.is_over = False

    def player_move(self):
        cur_player = self.players[self.turn]
        plane_moved, die_v = cur_player.take_action(self.gameboard)
        # TODO: check plane current position for catching, jumping, etc.
        print(f"Die: {die_v}")
        if plane_moved is not None:
            print(f"{cur_player.color} player moved plane {plane_moved.ind}")
        if die_v != 6:
            self.next_player()

    def next_player(self):
        self.turn = (self.turn + 1) % len(self.players)

    def show(self):
        print(self.gameboard)


def start_game():

    game = Game(num_players=2)
    game.show()
    while not game.is_over:
        input('Type enter to continue...')
        game.player_move()
        game.show()


if __name__ == '__main__':
    start_game()
