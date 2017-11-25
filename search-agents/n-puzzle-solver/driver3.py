import sys
import math
import logging
import time
from collections import deque as dq


class State:
    tiles = []
    dimensions = 0
    parent = None
    depth = 0
    empty_row = 0
    empty_col = 0
    number_of_moves = 0
    parent_move = None

    def __init__(self, state_array, parent=None, depth=0):
        self.tiles = state_array
        self.dimensions = int(math.sqrt(len(self.tiles)))
        self.parent = parent
        empty_index = state_array.index(0)
        self.empty_row = int(empty_index / self.dimensions)
        self.empty_col = empty_index % self.dimensions
        self.depth = depth

    def __hash__(self):
        return hash(str(self.tiles))

    def __str__(self):
        res = ""
        for i in range(self.dimensions):
            for j in range(self.dimensions):
                res = res + str(self.tiles[i * self.dimensions + j]) + " "
            res = res + "\n"
        return res

    def __eq__(self, other):
        if isinstance(other, State):
            return other.tiles == self.tiles

    def __ne__(self, other):
        return (not self.__eq__(other))

    def move_up(self):
        to_swap_row = self.empty_row - 1
        to_swap_col = self.empty_col
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_down(self):
        to_swap_row = self.empty_row + 1
        to_swap_col = self.empty_col
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_left(self):
        to_swap_row = self.empty_row
        to_swap_col = self.empty_col - 1
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_right(self):
        to_swap_row = self.empty_row
        to_swap_col = self.empty_col + 1
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_empty_to(self, row, col):
        new_list = list(self.tiles)
        existing_element = new_list[row *
                                    self.dimensions + col]
        new_list[row * self.dimensions + col] = 0
        new_list[self.empty_row * self.dimensions +
                 self.empty_col] = existing_element
        new_state = State(new_list, self, self.depth + 1)
        # logging.debug("\n" + str(new_state))
        return new_state

    def is_valid(self, row, col):
        if (row >= 0 and row < self.dimensions and col >= 0 and col < self.dimensions):
            return True
        else:
            return False

    def generate_possible_states(self):
        children = []
        up = self.move_up()
        if up is not None:
            up.parent_move = "Up"
            up.number_of_moves = self.number_of_moves + 1
            children.append(up)

        down = self.move_down()
        if down is not None:
            down.parent_move = "Down"
            down.number_of_moves = self.number_of_moves + 1
            children.append(down)

        left = self.move_left()
        if left is not None:
            left.parent_move = "Left"
            left.number_of_moves = self.number_of_moves + 1
            children.append(left)

        right = self.move_right()
        if right is not None:
            right.parent_move = "Right"
            right.number_of_moves = self.number_of_moves + 1
            children.append(right)

        return children


class BfsSolver:
    initial_state = None
    frontier = dq()
    explored = set()

    def __init__(self, initial_state=None):
        self.initial_state = initial_state
        self.frontier.append(initial_state)

    def solve(self):
        start_time = time.time()
        maxdepth = 0
        while(len(self.frontier) != 0):
            current_state = self.frontier.popleft()
            if (self.isFinalState(current_state)):
                soln = self.get_solution_moves(current_state)
                end_time = time.time()
                logging.info("Final state reached! \n " +
                             "nodes_expanded : " + str(len(self.explored)) +
                             "\n search_depth :" + str(current_state.depth) +
                             "\n max_search_depth : " + str(maxdepth) +
                             "\n cost_of_path : " + str(len(soln)) +
                             "\n path : " + str(soln) +
                             "\n time : " + str(end_time - start_time)
                             )
                return
            neighbors = current_state.generate_possible_states()
            for neighbor in neighbors:
                if neighbor.depth > maxdepth:
                    maxdepth = neighbor.depth
                if neighbor not in self.explored:
                    self.frontier.append(neighbor)
            self.explored.add(current_state)
            logging.debug("Frontier size = " +
                          str(len(self.frontier)) +
                          "; Explored size = " +
                          str(len(self.explored)))

    def get_solution_moves(self, final_state):
        moves = dq()
        current_state = final_state
        while current_state is not None:
            if current_state.parent_move is not None:
                moves.appendleft(current_state.parent_move)
            current_state = current_state.parent
        res = []
        [res.append(move) for move in moves]
        return res

    def isFinalState(self, state):
        internal_state = state.tiles
        for i in range(len(internal_state) - 1):
            if internal_state[i] != i:
                return False
        return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    arguments = sys.argv
    initial_board_state = State([int(x) for x in str(arguments[2]).split(",")])
    if arguments[1] == "bfs":
        solver = BfsSolver(initial_board_state)
        solver.solve()
