import random

from GameBoard import GameBoard, Plane


class AeroplaneChessAgent:
    def __init__(self, color: str):
        self.color = color

    def get_action(self, gameboard: GameBoard, movable_planes: list[Plane], die_v: int):
        NotImplementedError("Abstract Method")


class RandomAgent(AeroplaneChessAgent):
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, gameboard: GameBoard, movable_planes: list[Plane], die_v: int):
        ind = random.randint(0, len(movable_planes)-1)
        return movable_planes[ind]


class ExpectimaxAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)

    def get_action(self, gameboard: GameBoard, movable_planes: list[Plane], die_v: int):
        pass
