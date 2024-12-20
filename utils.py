import random


COLORS = ['R', 'B', 'Y', 'G']
NUM_SQUARES = 52

# ENTRY = {'R': 39, 'B': 0, 'Y': 13, 'G': 26}
# FS = {'R': 36, 'B': 49, 'Y': 10, 'G': 23}
ENTRY = {'B': 0, 'G': 26}
FS = {'B': 49, 'G': 23}
JUMP_POINT = {'R': 4, 'B': 17, 'Y': 30, 'G': 43}
OPPONENT = {'R': 'Y', 'B': 'G', 'G': 'B', 'Y': 'R'}
MAX_DEPTH = 2
AGENT1 = "Expectimax"
# AGENT1 = "MCTS"
# AGENT1 = "RL"
# AGENT1 = None
DEBUG_EXPECTIMAX = False
CONFIG = {
    'no-graphics': True,
    'display': False,
}


def roll_die(state):
    die_roll = random.randint(1, 6)
    state.die_roll = die_roll
    return die_roll
