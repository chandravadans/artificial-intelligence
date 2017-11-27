import sys
import math
import logging
import time
from collections import deque as dq
import resource


class State:
    """
    The underlying state of the board. Apart from the configuration, it stores a
    bunch of other meta data like what the parent was and what move on the parent
    resulted in this state
    """
    tiles = []
    dimensions = 0
    parent = None
    depth = 0
    empty_row = 0
    empty_col = 0
    number_of_moves = 0
    parent_move = None

    def __init__(self, state_array, parent=None, depth=0):
        """
        Initialises this state with a confguration, an optional parent and an optional depth
        """
        self.tiles = state_array
        self.dimensions = int(math.sqrt(len(self.tiles)))
        self.parent = parent
        empty_index = state_array.index(0)
        self.empty_row = int(empty_index / self.dimensions)
        self.empty_col = empty_index % self.dimensions
        self.depth = depth

    def __hash__(self):
        """
        Uniqueness of a state is defined just by the internal configuration
        of its tiles
        """
        return hash(str(self.tiles))

    def __str__(self):
        """
        A string representation of a state, just prints out the internal
        configuration of the tiles
        """
        res = ""
        for i in range(self.dimensions):
            for j in range(self.dimensions):
                res = res + str(self.tiles[i * self.dimensions + j]) + " "
            res = res + "\n"
        return res

    def __eq__(self, other):
        """
        Function overridden to make States valid candidates for insertion
        into sets
        """
        if isinstance(other, State):
            return other.tiles == self.tiles

    def __ne__(self, other):
        return (not self.__eq__(other))

    def move_up(self):
        """
        Returns a new state that is the result of moving the empty tile
        one space up
        """
        to_swap_row = self.empty_row - 1
        to_swap_col = self.empty_col
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_down(self):
        """
        Returns a new state that is the result of moving the empty tile
        one space down
        """
        to_swap_row = self.empty_row + 1
        to_swap_col = self.empty_col
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_left(self):
        """
        Returns a new state that is the result of moving the empty tile
        one space left
        """
        to_swap_row = self.empty_row
        to_swap_col = self.empty_col - 1
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_right(self):
        """
        Returns a new state that is the result of moving the empty tile
        one space right
        """
        to_swap_row = self.empty_row
        to_swap_col = self.empty_col + 1
        if (self.is_valid(to_swap_row, to_swap_col)):
            return self.move_empty_to(to_swap_row, to_swap_col)
        else:
            return None

    def move_empty_to(self, row, col):
        """
        Helper function used by the movement functions that actually
        does the work of shifting the empty space around
        """
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
        """
        Returns if a row, col configuration is valid for a given board
        """
        if (row >= 0 and row < self.dimensions and col >= 0 and col < self.dimensions):
            return True
        else:
            return False

    def generate_possible_states(self):
        """
        Generates all possible states given a state. Moves are performed using in UDLR order
        """
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
    """
    Uses the BFS algo to solve a given n-puzzle board
    """
    initial_state = None

    # The frontier in BFS is actually used as a queue
    frontier = dq()

    # All of the fully explored states in this set
    explored = set()

    def __init__(self, initial_state=None):
        self.initial_state = initial_state
        self.frontier.append(initial_state)

    def solve(self):
        """
        Attempts to solve an n-puzzle and returns a stats
        dict, or None if no solution exists
        """
        start_time = time.time()
        maxdepth = 0
        while(len(self.frontier) != 0):
            current_state = self.frontier.popleft()
            if (self.isFinalState(current_state)):
                soln = self.get_solution_moves(current_state)
                end_time = time.time()
                stats = {}
                stats["nodes_expanded"] = len(self.explored)
                stats["search_depth"] = current_state.depth
                stats["max_search_depth"] = maxdepth
                stats["cost_of_path"] = len(soln)
                stats["time"] = end_time - start_time
                stats["path"] = soln
                return stats
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
        logging.error("This is an unsolvable board!")
        return None

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


class DfsSolver:
    """
    Uses the DFS algo to solve a given n-puzzle board
    """
    initial_state = None

    # The frontier in DFS is actually used as a stack
    frontier = dq()
    frontierSet = set()

    # All of the fully explored states in this set
    explored = set()

    def __init__(self, initial_state=None):
        self.initial_state = initial_state
        self.frontier.append(initial_state)
        self.frontierSet.add(initial_state)

    def solve(self):
        """
        Attempts to solve an n-puzzle and returns a stats
        dict, or None if no solution exists
        """
        start_time = time.time()
        maxdepth = 0
        while(len(self.frontier) != 0):
            current_state = self.frontier.pop()
            self.frontierSet.remove(current_state)
            if (self.isFinalState(current_state)):
                soln = self.get_solution_moves(current_state)
                end_time = time.time()
                stats = {}
                stats["nodes_expanded"] = len(self.explored)
                stats["search_depth"] = current_state.depth
                stats["max_search_depth"] = maxdepth
                stats["cost_of_path"] = len(soln)
                stats["time"] = end_time - start_time
                stats["path"] = soln
                return stats
            neighbors = current_state.generate_possible_states()
            neighbors.reverse()
            for neighbor in neighbors:
                if neighbor.depth > maxdepth:
                    maxdepth = neighbor.depth
                if neighbor not in self.explored and neighbor not in self.frontierSet:
                    self.frontier.append(neighbor)
                    self.frontierSet.add(neighbor)
            self.explored.add(current_state)
            logging.debug("Frontier size = " +
                          str(len(self.frontier)) +
                          "; Explored size = " +
                          str(len(self.explored)))
        logging.error("This is an unsolvable board!")
        return None

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
    elif arguments[1] == "dfs":
        solver = DfsSolver(initial_board_state)
    elif arguments[1] == "ast":
        solver = BfsSolver(initial_board_state)
    stats = solver.solve()
    ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    op = open("output.txt", "w+")
    op.write(
        "path_to_goal: " + str(stats["path"]) +
        "\ncost_of_path: " + str(stats["cost_of_path"]) +
        "\nnodes_expanded: " + str(stats["nodes_expanded"]) +
        "\nsearch_depth: " + str(stats["search_depth"]) +
        "\nmax_search_depth: " + str(stats["max_search_depth"]) +
        "\nrunning_time: " + str(stats["time"]) +
        "\nmax_ram_usage: " + str(ram_usage)
    )
    op.close()
