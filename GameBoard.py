from copy import deepcopy
from types import NoneType
from typing import Self

from colorama import Fore, Style

from utils import COLORS, ENTRY, NUM_SQUARES, FS, JUMP_POINT, OPPONENT


class Square:
    def __init__(self, ind: int, is_final_stretch: bool = False, color: str = None):
        # Square color order: Red -> Blue -> Yellow -> Green -> Red
        self.ind = ind
        if is_final_stretch:
            assert color is not None
            self.color = color
        else:
            self.color = COLORS[ind % 4]
        self.planes = []

    def is_jump_point(self):
        # special jump point
        return self.ind == JUMP_POINT[self.color]

    def __repr__(self):
        return self.color

    def __str__(self):
        return self.color


class Plane:
    def __init__(self, color: str, ind: int):
        self.pos = None
        self.ind = ind
        self.color = color
        self.pos_type = 'Hangar'
        self.total_steps = 0

    def move(self, steps: int):
        if self.pos_type == 'Hangar' and steps == 6:  # On Hangar
            self.launch()
        elif self.is_on_launch():  # At launch area
            self.pos = ENTRY[self.color] + steps - 1
            self.total_steps += steps
            self.pos_type = 'Main'
        elif self.is_on_final_stretch():  # Final stretch
            if self.pos + steps > 6:  # Bounce back
                self.pos = 6 - ((self.pos + steps) - 6)
            elif self.pos + steps == 6:
                self.finish()
            else:
                self.pos += steps
        elif self.is_on_main_track():  # Main track
            if self.total_steps + steps > 50:  # Enter final stretch
                self.pos_type = 'Final'
                self.pos = self.total_steps + steps - 50
                self.total_steps = 50
            else:  # Main track move
                self.pos = (self.pos + steps) % NUM_SQUARES
                self.total_steps += steps
        else:
            raise ValueError(f"Try to move plane {self.pos_type} when die roll {steps}.")

    @staticmethod
    def catch_plane(other_plane):
        other_plane.pos = None
        other_plane.pos_type = 'Hangar'
        other_plane.total_steps = 0

    def launch(self):
        self.pos = -1
        self.pos_type = 'Launch'

    def finish(self):
        self.pos = None
        self.pos_type = 'Finish'

    def is_on_hangar(self):
        return self.pos_type == 'Hangar'

    def is_on_main_track(self):
        return self.pos_type == 'Main'

    def is_on_final_stretch(self):
        return self.pos_type == 'Final'

    def is_on_launch(self):
        return self.pos_type == 'Launch'

    def is_finished(self):
        return self.pos_type == 'Finish'


class GameBoard:
    """
    Aeroplane chess gameboard, can be used as game state
    """

    def __init__(self, planes: list[Plane]):
        self.squares = [Square(i) for i in range(NUM_SQUARES)]
        self.final_stretches = [[Square(i, is_final_stretch=True, color=color) for i in range(7)]
                                for color in COLORS]

        self.planes = planes

    def __repr__(self):
        main_track_str = ' '.join([s.__repr__() for s in self.squares])
        # Initialize as list to align position
        # Main track display
        num_planes_str = ['0' for _ in range(len(self.squares))]
        plane_color_str = ['0' for _ in range(len(self.squares))]
        for i in range(len(self.planes)):
            if self.planes[i].is_on_main_track():
                pos = self.planes[i].pos
                num_planes_str[pos] = str(int(num_planes_str[pos]) + 1)
                plane_color_str[pos] = self.planes[i].color

        num_planes_str = ' '.join(num_planes_str).replace('0', ' ')
        plane_color_str = ' '.join(plane_color_str).replace('0', ' ')

        # Final stretches display
        fs_str_l = []
        num_planes_str_l = []
        plane_color_str_l = []
        for fs in self.final_stretches:
            fs_str = ' '.join([s.__repr__() for s in fs])
            fs_str_l.append(fs_str)
            nplanes_str = ['0' for _ in range(len(self.squares))]
            pc_str = ['0' for _ in range(len(self.squares))]
            for i in range(len(self.planes)):
                if self.planes[i].is_on_final_stretch() and self.planes[i].color == fs[0].color:
                    pos = self.planes[i].pos
                    nplanes_str[pos] = str(int(nplanes_str[pos]) + 1)
                    pc_str[pos] = self.planes[i].color
            nplanes_str = ' '.join(nplanes_str).replace('0', ' ')
            pc_str = ' '.join(pc_str).replace('0', ' ')
            num_planes_str_l.append(nplanes_str)
            plane_color_str_l.append(pc_str)

        # Entry and final stretches entry point annotation
        entries_str_l = ['0' for _ in range(len(self.squares))]
        for e in ENTRY.values():
            entries_str_l[e] = 'E'
        for f in FS.values():
            entries_str_l[f] = 'F'
        entries_str = ' '.join(entries_str_l).replace('0', ' ')

        return f'''
=================================Main track==============================================================
{entries_str}
{main_track_str}
{num_planes_str}
{plane_color_str}
========================================Final Stretches==================================================
=============================================B===========================================================
{fs_str_l[1]}
{num_planes_str_l[1]}
{plane_color_str_l[1]}
=============================================G===========================================================
{fs_str_l[3]}
{num_planes_str_l[3]}
{plane_color_str_l[3]}
'''


'''
=================================Main track==============================================================
{entries_str}
{main_track_str}
{num_planes_str}
{plane_color_str}
========================================Final Stretches==================================================
==============================================R==========================================================
{fs_str_l[0]}
{num_planes_str_l[0]}
{plane_color_str_l[0]}
=============================================B===========================================================
{fs_str_l[1]}
{num_planes_str_l[1]}
{plane_color_str_l[1]}
=============================================Y===========================================================
{fs_str_l[2]}
{num_planes_str_l[2]}
{plane_color_str_l[2]}
=============================================G===========================================================
{fs_str_l[3]}
{num_planes_str_l[3]}
{plane_color_str_l[3]}
'''


class GameState:
    def __init__(self, players, turn: int):
        self.players = players
        self.gameboard = GameBoard([plane for player in players for plane in player.planes])
        self.turn = turn

    def get_movable_planes(self, die_v: int):
        return self.players[self.turn].get_movable_planes(die_v)

    def generateSuccessor(self, action: [NoneType, int], die_v: int, show_event: bool = False) -> Self:
        # Create new state
        succ_state = GameState(deepcopy(self.players), self.turn)
        event_log = ""
        cur_player = succ_state.players[succ_state.turn]
        if action is not None:
            # Move plane
            plane_moved = cur_player.planes[action]
            plane_moved.move(die_v)

            # Can catch planes both before and after jump
            pos = plane_moved.pos

            # catching planes
            caught_plane, inx = self.catch_planes(succ_state, plane_moved, pos)
            if caught_plane:
                event_log += f"{Fore.RED}{cur_player.color} player's plane {plane_moved.ind} caught {OPPONENT[cur_player.color]} " \
                             f"player's plane {inx}!{Style.RESET_ALL}\n"
            # Handle jump

            if plane_moved.is_on_main_track() and \
                    succ_state.gameboard.squares[pos].color == plane_moved.color:  # Jump
                if succ_state.gameboard.squares[pos].is_jump_point() or \
                        succ_state.gameboard.squares[(pos + 4) % NUM_SQUARES].is_jump_point():  # Jump point
                    plane_moved.move(16)
                    event_log += f"{Fore.RED}{cur_player.color} player's plane {plane_moved.ind} took a big jump!{Style.RESET_ALL}\n"
                    # catch opponent planes on final stretch
                    opponent = succ_state.get_opponent(cur_player)
                    for plane in opponent.planes:
                        if plane.is_on_final_stretch() and plane.pos == 3:
                            plane_moved.catch_plane(plane)
                            event_log += f"{Fore.RED}{cur_player.color} player's plane {plane_moved.ind} catched {plane.color} " \
                                         f"player's plane {plane.ind}!{Style.RESET_ALL}\n"
                else:
                    plane_moved.move(4)
                    event_log += f"{Fore.RED}{cur_player.color} player's plane {plane_moved.ind} took a jump!{Style.RESET_ALL}\n"
            # Update pos
            pos = plane_moved.pos
            # catching planes
            caught_plane, inx = self.catch_planes(succ_state, plane_moved, pos)
            if caught_plane:
                event_log += f"{Fore.RED}{cur_player.color} player's plane {plane_moved.ind} caught {OPPONENT[cur_player.color]} " \
                            f"player's plane {inx}!{Style.RESET_ALL}\n"
            # Check if finished
            if plane_moved.is_finished():
                event_log += f"{Fore.RED}{cur_player} player got a plane finished!\n"

        if show_event:
            print(event_log)

        if die_v != 6:
            new_turn = (succ_state.turn + 1) % len(succ_state.players)  # Next player
        else:
            new_turn = succ_state.turn
        succ_state.turn = new_turn

        return succ_state

    @staticmethod
    def catch_planes(succ_state, plane_moved: Plane, pos: int):
        other_planes = succ_state.get_planes(pos)
        caught_plane = False
        inx = []
        if len(other_planes) > 0:
            caught_plane = True
            for plane in other_planes:
                inx.append(plane.ind)
                plane_moved.catch_plane(plane)
        return caught_plane, inx

    def get_opponent(self, cur_player):
        if cur_player.color == 'B':
            for player in self.players:
                if player.color == 'G':
                    return player
        elif cur_player.color == 'G':
            for player in self.players:
                if player.color == 'B':
                    return player
        else:
            raise NotImplemented("Not implemented for other colors yet")

    def get_planes(self, pos: int):
        planes = []
        for i in range(len(self.players)):
            if i != self.turn:
                for plane in self.players[i].planes:
                    if plane.is_on_main_track() and plane.pos == pos:
                        planes.append(plane)
        return planes

    def is_win(self, color: str):
        for player in self.players:
            if player.color == color:
                return player.get_remaining_planes_count() == 0

    def is_lose(self, color: str):
        for player in self.players:
            if player.color != color and player.get_remaining_planes_count() == 0:
                return True
        return False
