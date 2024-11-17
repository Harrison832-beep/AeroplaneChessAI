from utils import COLORS, ENTRY


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

        # TODO: special jump point

    def __repr__(self):
        return self.color

    def __str__(self):
        return self.color


class Plane:
    def __init__(self, color: str, ind: int):
        self.pos = -1
        self.ind = ind
        self.color = color
        self.pos_type = 'Hanger'
        self.total_steps = 0

    def move(self, steps: int):
        if self.pos_type == 'Hanger' and steps == 6:  # On hanger
            self.launch()
        elif self.pos_type == 'Launch':  # At launch area
            self.pos = ENTRY[self.color] + steps - 1
            self.total_steps += steps  # TODO: if catched, reset total steps
        elif self.pos_type == 'Final':
            if self.pos + steps > 6:
                self.pos = 6 - ((self.pos + steps) - 6)
            elif self.pos + steps == 6:
                self.pos = -1
                self.pos_type = 'Finish'
            else:
                self.pos += steps
        else:  # Main track
            if self.total_steps + steps > 50:
                self.pos_type = 'Final'
                self.pos = self.total_steps + steps - 50

    def launch(self):
        self.pos_type = 'Launch'

    def finish(self):
        self.pos_type = 'Finish'


class GameBoard:
    """
    Aeroplane chess gameboard, can be used as game state
    """
    def __init__(self, planes: list[Plane]):
        self.squares = [Square(i) for i in range(52)]
        self.final_stretches = [[Square(i, is_final_stretch=True, color=color) for i in range(7)]
                                for color in COLORS]

        self.planes = planes

    def __repr__(self):
        main_track_str = ' '.join([s.__repr__() for s in self.squares])
        # Initialize as list to align position
        num_planes_str = ['0' for _ in range(len(self.squares))]
        plane_color_str = ['0' for _ in range(len(self.squares))]
        for i in range(len(self.planes)):
            if self.planes[i].pos >= 0:
                num_planes_str[i] = str(int(num_planes_str[i]) + 1)
                plane_color_str[i] = self.planes[i].color

        num_planes_str = ' '.join(num_planes_str).replace('0', ' ')
        plane_color_str = ' '.join(plane_color_str).replace('0', ' ')

        fs_str_l = []
        num_planes_str_l = []
        plane_color_str_l = []
        for fs in self.final_stretches:
            fs_str = ' '.join([s.__repr__() for s in fs])
            fs_str_l.append(fs_str)
            nplanes_str = ['0' for _ in range(len(self.squares))]
            pc_str = ['0' for _ in range(len(self.squares))]
            for i in range(len(self.planes)):
                if self.planes[i].pos >= 0:
                    nplanes_str[i] = str(int(nplanes_str[i]) + 1)
                    pc_str[i] = self.planes[i].color
            nplanes_str = ' '.join(nplanes_str).replace('0', ' ')
            pc_str = ' '.join(pc_str).replace('0', ' ')
            num_planes_str_l.append(nplanes_str)
            plane_color_str_l.append(pc_str)

        return f'''
=================================Main track==============================================================
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
