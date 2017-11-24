import sys
import math


class State(object):
    tiles = []
    dimensions = 0
    parent = None
    depth = 0

    def __init__(self, state_array, parent=None):
        self.tiles = state_array
        self.dimensions = int(math.sqrt(self.tiles.__len__()))
        self.parent = parent

    def __hash__(self):
        return str(self.tiles)

    def move_up(self):
        print("Moved up, now the board state is %s" % str(self.tiles))
        return self.tiles

    def move_down(self):
        print("Moved down, now the board state is %s" % str(self.tiles))
        return self.tiles

    def move_left(self):
        print("Moved left, now the board state is %s" % str(self.tiles))
        return self.tiles

    def move_right(self):
        print("Moved right, now the board state is %s" % str(self.tiles))
        return self.tiles


if __name__ == '__main__':
    arguments = sys.argv
    initial_board_state = State(str(arguments[1]).split(","))
    initial_board_state.dimensions = 3
