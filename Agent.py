import random
from abc import ABC

from GameBoard import GameBoard, Plane, GameState
from utils import MAX_DEPTH


class AeroplaneChessAgent:
    def __init__(self, color: str):
        self.color = color

    def get_action(self, state: GameState, die_v: int):
        NotImplementedError("Abstract Method")

    def evaluate_state(self, state: GameState):
        """
        Finished plane: 100
        Each plane on hangar: -50
        Each step: 0.05
        Opponent finished plane: -100
        Opponent plane on Hangar: 50
        Opponent step: -0.05
        """
        score = 0
        for player in state.players:
            player_score = 0
            for plane in player.planes:
                if plane.is_finished():
                    score += 100
                elif plane.is_on_hangar():
                    score -= 50
                if plane.is_on_final_stretch():
                    score += 50*0.05 + (6 - plane.pos)*0.05  # Distance to finish
                else:
                    score += plane.total_steps * 0.05
            if player.color == self.color:  # Agent color
                score += player_score
            else:
                score -= player_score

        return score


class RandomAgent(AeroplaneChessAgent):
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, state: GameState, die_v: int):
        movable_planes_inx = state.get_movable_planes(die_v)
        if len(movable_planes_inx) > 0:
            ind = random.randint(0, len(movable_planes_inx) - 1)
            return movable_planes_inx[ind]


class ExpectimaxAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)

    def get_action(self, state: GameState, die_v: int):
        movable_planes_inx = state.get_movable_planes(die_v)
        if len(movable_planes_inx) > 0:
            v, action = self._max(state, die_v, 1)
            assert action is not None
            return action
        return None

    def _max(self, state, die_v, depth):
        if state.is_win(self.color) or state.is_lose(self.color) or depth > MAX_DEPTH:
            return self.evaluate_state(state), None
        move = None
        v = -float('inf')
        movable_planes_inx = state.get_movable_planes(die_v)
        for a in movable_planes_inx:
            expected_v2 = 0
            new_state = state.generateSuccessor(a, die_v)
            # When die is 6, the next will still be max player
            for die_v2 in range(1, 7):
                if die_v == 6:
                    v2, _ = self._max(new_state, die_v2, depth + 1)
                else:
                    v2, _ = self._min(new_state, die_v2, depth + 1)
                expected_v2 += v2
            expected_v2 /= 6
            if expected_v2 > v:
                v, move = expected_v2, a
        return v, move

    def _min(self, state, die_v, depth):
        if state.is_win(self.color) or state.is_lose(self.color) or depth > MAX_DEPTH:
            return self.evaluate_state(state), None
        move = None
        expected_v = 0
        movable_planes_inx = state.get_movable_planes(die_v)
        for a in movable_planes_inx:
            expected_v2 = 0
            new_state = state.generateSuccessor(a, die_v)
            for die_v2 in range(1, 7):
                # When die is 6, the next will still be min player
                if die_v == 6:
                    v2, a2 = self._min(new_state, die_v2, depth + 1)
                else:
                    v2, a2 = self._max(new_state, die_v2, depth + 1)
                expected_v2 += v2
            expected_v2 /= 6
            expected_v += expected_v2
        return expected_v, move


class MCTSAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)

    def get_action(self, state: GameState, die_v: int):
        movable_planes = state.get_movable_planes(die_v)
        pass



