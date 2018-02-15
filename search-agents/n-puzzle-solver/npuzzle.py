import sys
import math
import logging
import time
from collections import deque as dq
from queue import PriorityQueue
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

    # Stats for astar
    f = 0           # f = g + h
    g = 0           # g, cost of reaching this state (Equal to the depth of the node)
    h = 0           # h, heuristic value, here manhattan score

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
    
    def __lt__(self, other):
        """
        Compares states by their manhattan scores. 
        Useful in A* 
        """
        return other.f >= self.f
        

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
        new_state.process_astar_stats()
        logging.debug("\n" + str(new_state))
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
    
    def process_astar_stats(self):
        """
        Computes a stats needed for astar: f,g, and h
        """
        self.g = self.depth
        self.h = self.compute_manhattan()
        self.f = self.g + self.h
    
    def compute_manhattan(self):
        """
        Computes manhattan heuristic for this state, the sum of manhattan
        distances of all misplaced non empty tiles from their actual positions
        """
        dist = 0
        for i in range(0,len(self.tiles)):
            tile = self.tiles[i]
            if tile != 0:
                rowTile = i // self.dimensions
                colTile = i % self.dimensions
                correctRow = tile // self.dimensions
                correctCol = tile % self.dimensions
                md = abs(rowTile - correctRow) + abs(colTile - correctCol)
                dist = dist + md
        return dist


class NPuzzleSolver:
    """
        Uses the BFS/DFS/A* algos to solve a given n-puzzle board
    """
    initial_state = None
    algo = ""

    # The frontier in BFS/DFS is a queue/stack and for A*, its a heap (PriorityQueue)
    # Frontier set made to test membership in O(1)
    frontier = None
    frontier_set = set()

    # All of the fully explored states in this set
    explored = set()

    def __init__(self, algo, initial_state=None):
        self.initial_state = initial_state
        if algo == "bfs" or algo == "dfs":
            self.frontier = dq()
            self.frontier.append(initial_state)
        else:
            self.frontier = PriorityQueue()
            self.frontier.put(initial_state)
        self.frontier_set.add(initial_state)
        self.algo = algo

    def solve(self):
        """
        Attempts to solve an n-puzzle and returns a stats
        dict, or None if no solution exists
        """
        start_time = time.time()
        maxdepth = 0
        break_cond = False

        while(not break_cond):
            if self.algo == "bfs":
                # Pop the leftmost element if doing a bfs (Queue)
                current_state = self.frontier.popleft()
            elif self.algo == "dfs":
                # Pop the rightmost element if doing a dfs (Stack)
                current_state = self.frontier.pop()
            else:
                # Get element with highest priority if doing A* (Heap)
                current_state = self.frontier.get()
            self.frontier_set.remove(current_state)
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
            if self.algo == "dfs":
                neighbors.reverse()

            for neighbor in neighbors:
                if neighbor not in self.explored and neighbor not in self.frontier_set:
                    if self.algo == "bfs" or self.algo == "dfs":
                        self.frontier.append(neighbor)
                    else:
                        self.frontier.put(neighbor)
                    self.frontier_set.add(neighbor)
                    if neighbor.depth > maxdepth:
                        maxdepth = neighbor.depth
            self.explored.add(current_state)
            if self.algo == "bfs" or self.algo == "dfs":
                frontier_sz = len(self.frontier)
            else:
                frontier_sz = self.frontier.qsize()
            logging.debug("Frontier size = " +
                          str(frontier_sz) +
                          "; Explored size = " +
                          str(len(self.explored)))
            if self.algo == "bfs" or self.algo == "dfs":
                break_cond = len(self.frontier) == 0
            else:
                break_cond = self.frontier.empty()
        logging.error("This is an unsolvable board!")
        return None

    def get_solution_moves(self, final_state):
        """
        Gets the sequence of moves from parent to this state
        """
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
        """
        Checks if this is the final state (0,1,2...m^2-1)
        """
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
    logging.debug("MD of initial state = %d", initial_board_state.compute_manhattan())
    if arguments[1] == "bfs":
        solver = NPuzzleSolver("bfs", initial_board_state)
    elif arguments[1] == "dfs":
        solver = NPuzzleSolver("dfs", initial_board_state)
    elif arguments[1] == "ast":
        solver = NPuzzleSolver("ast", initial_board_state)
    stats = solver.solve()
    ram_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(
        "path_to_goal: " + str(stats["path"]) +
        "\ncost_of_path: " + str(stats["cost_of_path"]) +
        "\nnodes_expanded: " + str(stats["nodes_expanded"]) +
        "\nsearch_depth: " + str(stats["search_depth"]) +
        "\nmax_search_depth: " + str(stats["max_search_depth"]) +
        "\nrunning_time: " + str(stats["time"]) +
        "\nmax_ram_usage: " + str(ram_usage)
    )
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
