import random
from math import sqrt, log
from types import NoneType

from GameBoard import GameState
from utils import MAX_DEPTH, DEBUG_EXPECTIMAX, roll_die
from typing_extensions import Self


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
                    score += 50 * 0.05 + (6 - plane.pos) * 0.05  # Distance to finish
                else:
                    score += plane.total_steps * 0.05
            if player.color == self.color:  # Agent color
                score += player_score
            else:
                score -= player_score

        return score

    def __repr__(self):
        return "Abstract agent"


class RandomAgent(AeroplaneChessAgent):
    def __init__(self, color):
        super().__init__(color)

    def get_action(self, state: GameState, die_v: int):
        movable_planes_inx = state.get_movable_planes(die_v)
        if len(movable_planes_inx) > 0:
            ind = random.randint(0, len(movable_planes_inx) - 1)
            return movable_planes_inx[ind]

    def __repr__(self):
        return f"Random agent ({self.color})"


class ExpectimaxAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)

    def get_action(self, state: GameState, die_v: int):
        movable_planes_inx = state.get_movable_planes(die_v)
        if len(movable_planes_inx) > 0:
            v, action = self._max(state, die_v, 1)

            if DEBUG_EXPECTIMAX:
                try:
                    v, action = self._max(state, die_v, 1)
                    # As long as there is plane to move, it's impossible action is None
                    assert action is not None
                except Exception:
                    print("HERE")
                    v, action = self._max(state, die_v, 1)  # Debug
            return action
        return None

    def _max(self, state, die_v, depth):
        movable_planes_inx = state.get_movable_planes(die_v)
        if state.is_win(self.color) or state.is_lose(self.color) or depth > MAX_DEPTH or len(movable_planes_inx) == 0:
            return self.evaluate_state(state), None
        move = None
        v = -float('inf')

        for a in movable_planes_inx:
            expected_v2 = 0
            new_state = state.generate_successor(a, die_v)
            # When die is 6, the next will still be max player
            for die_v2 in range(1, 7):
                if die_v == 6:
                    v2, _ = self._max(new_state, die_v2, depth + 1)

                    if DEBUG_EXPECTIMAX:
                        try:
                            assert v2 != -float('inf')
                        except Exception:
                            print("HERE")
                            v2, _ = self._max(new_state, die_v2, depth + 1)
                else:
                    v2, _ = self._min(new_state, die_v2, depth + 1)

                    if DEBUG_EXPECTIMAX:
                        try:
                            assert v2 != -float('inf')
                        except Exception:
                            print("HERE")
                            v2, _ = self._min(new_state, die_v2, depth + 1)
                expected_v2 += v2
            expected_v2 /= 6
            if expected_v2 > v:
                v, move = expected_v2, a
        return v, move

    def _min(self, state, die_v, depth):
        movable_planes_inx = state.get_movable_planes(die_v)
        if state.is_win(self.color) or state.is_lose(self.color) or depth > MAX_DEPTH or len(movable_planes_inx) == 0:
            return self.evaluate_state(state), None
        move = None
        expected_v = 0

        for a in movable_planes_inx:
            expected_v2 = 0
            new_state = state.generate_successor(a, die_v)
            for die_v2 in range(1, 7):
                # When die is 6, the next will still be min player
                if die_v == 6:
                    v2, a2 = self._min(new_state, die_v2, depth + 1)

                    if DEBUG_EXPECTIMAX:
                        try:
                            assert v2 != -float('inf')
                        except Exception:
                            print("HERE")
                            v2, a2 = self._min(new_state, die_v2, depth + 1)
                else:
                    v2, a2 = self._max(new_state, die_v2, depth + 1)

                    if DEBUG_EXPECTIMAX:  # Use for debug mode
                        try:
                            assert v2 != -float('inf')
                        except Exception:
                            print("HERE")
                            v2, a2 = self._max(new_state, die_v2, depth + 1)
                expected_v2 += v2
            expected_v2 /= 6
            expected_v += expected_v2
        if len(movable_planes_inx) > 0:
            expected_v /= len(movable_planes_inx)
        return expected_v, move

    def __repr__(self):
        return f"Expectimax agent ({self.color})"


class MCTSNode:
    def __init__(self, state: GameState, parent: [Self, NoneType], action: int = None):
        self.state = state
        self.n = 1
        self.u = 0
        self.action = action  # Action taken from parent state to this state
        self.parent = parent
        self.children = []

    def fully_expanded(self):
        """
        A node is fully expanded if:
        * It has multiple movable planes, then # children = movable planes
        * It doesn't have any movable plane, then should have one child
        """
        movable_plane_inx = self.state.get_turn_player().get_movable_planes(self.state.die_roll)
        if len(movable_plane_inx) > 0:
            return len(self.children) == len(movable_plane_inx)
        else:
            return len(self.children) == 1


class MCTSAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)
        self.root = None

    def get_action(self, state: GameState, die_v: int):
        """
        Start new root for each state or search?
        """
        movable_planes_inx = state.get_movable_planes(die_v)

        if len(movable_planes_inx) > 0:
            self.root = MCTSNode(state, parent=None)

            for i in range(200):
                # print("Iteration:", i)
                leaf = self.select()
                if leaf.state.is_win(self.color) or leaf.state.is_lose(self.color):
                    break

                child = self.expand(leaf)

                result = self.simulate(child)
                self.backpropagate(result, child)

            best_child: MCTSNode = max(self.root.children, key=lambda x: x.u)
            action = best_child.action
            assert action is not None
            return action
        return None

    def select(self) -> Self:
        """
        Repetitively select node using selection policy until leaf is reached
        """
        node = self.root
        node.n += 1
        while node.fully_expanded() and len(node.children) > 0:
            node = max(node.children, key=lambda x: self.UCB1(x))
            node.n += 1
        return node

    @staticmethod
    def expand(leaf: MCTSNode) -> MCTSNode:
        """
        Generate random successor state as new child
        """
        # If fully expanded, the leaf should not be chosen, should be its children instead
        assert not leaf.fully_expanded()

        state = leaf.state
        player = state.get_turn_player()  # Player of current turn
        die_roll = state.die_roll
        movable_plane_inx = player.get_movable_planes(die_roll)
        actions_taken = set([child.action for child in leaf.children])

        diff = list(set(movable_plane_inx) - actions_taken)

        a = None
        if len(diff) > 0:
            a = random.choice(diff)
        assert not len(
            movable_plane_inx) > 0 or a is not None  # if has movable planes, then must be an available action
        new_state = state.generate_successor(a, die_roll)
        roll_die(new_state)
        child = MCTSNode(new_state, leaf, action=a)
        leaf.children.append(child)
        return child

    def simulate(self, node: MCTSNode) -> float:
        state = node.state
        for _ in range(10):
            if state.is_win(self.color) or state.is_lose(self.color):
                break

            player = state.get_turn_player()  # Player of current turn
            if state.die_roll is None:
                die_roll = roll_die(node.state)
            else:
                die_roll = state.die_roll
            movable_plane_inx = player.get_movable_planes(die_roll)

            if len(movable_plane_inx) > 0:
                new_state = state.generate_successor(random.choice(movable_plane_inx), die_roll)
            else:
                new_state = state.generate_successor(None, die_roll)
            state = new_state
        return self.evaluate_state(state)

    @staticmethod
    def backpropagate(result, child):
        node = child
        node.u += result
        while node.parent is not None:
            node = node.parent
            node.u += result

    def UCB1(self, node: MCTSNode):
        # Selection policy
        C = 2 ** .5  # Recommended in textbook
        return node.u / node.n + C * sqrt(log(node.parent.n) / node.n)

    def __repr__(self):
        return f"MCTS agent ({self.color})"


Q = {}


class RLAgent(AeroplaneChessAgent):
    def __init__(self, color: str):
        super().__init__(color)
        self.alpha = 1.0
        self.gamma = 0.9
        self.epsilon = 0.2
        self.prev_state = None
        self.prev_action = None

    def get_action(self, state: GameState, die_v: int):
        movable_planes_inx = state.get_movable_planes(die_v)

        action = None
        if len(movable_planes_inx) > 0:
            reward = self.evaluate_state(state)

            if random.uniform(0, 1) < self.epsilon or state not in Q:
                action = random.choice(movable_planes_inx)
                Q[state] = {a: 0 for a in movable_planes_inx}
            else:
                action = max(Q[state], key=lambda act: Q[state][act])

            best_q = Q[state][action]
            if self.prev_state is not None:
                Q[self.prev_state][self.prev_action] += self.alpha * (reward + self.gamma * best_q - Q[state][action])

            self.prev_state = state
            self.prev_action = action

        return action

    def __repr__(self):
        return f"RL agent ({self.color})"
