import collections
import functools
import heapq

from Get_Maze import Maze
import time
import tracemalloc

Direction = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
    "u": (-1, 0),
    "d": (1, 0),
    "l": (0, -1),
    "r": (0, 1)
}


class FIFOQueue(collections.deque):
    """
    A First-In-First-Out Queue.
    """

    def __init__(self):
        collections.deque.__init__(self)

    def pop(self):
        return self.popleft()


# class PriorityQueue:
#     def __init__(self, function=lambda x: x):
#         self.items = []
#         self.f = function
#
#     def append(self, new_item):
#         heapq.heappush(self.items, (self.f(new_item), new_item))
#         # Use heapq for a better speed (maybe?)
#         # ref: https://www.geeksforgeeks.org/difference-between-heapq-and-priorityqueue-in-python/
#
#     def pop(self):
#         if self.items:
#             return heapq.heappop(self.items)[1]
#         else:
#             raise Exception('Trying to pop from empty PriorityQueue.')
#
#     def __contains__(self, key):
#         return any([item == key for _, item in self.items])
#
#     def __delitem__(self, key):
#         try:
#             del self.items[[item == key for _, item in self.items].index(True)]
#         except ValueError:
#             raise KeyError(str(key) + " is not in the priority queue")
#         heapq.heapify(self.items)
#
#     def __getitem__(self, key):
#         for value, item in self.items:
#             if item == key:
#                 return value
#         raise KeyError(str(key) + " is not in the priority queue")


class PriorityQueue:
    def __init__(self, function=lambda x: x):
        self.items = []
        self.f = function
        self.entry_finder = {}  # Map items to their priorities for fast lookups
        self.REMOVED = '<removed>'  # Placeholder for a removed item

    def append(self, new_item):
        # Add a new item with its priority
        priority = self.f(new_item)
        entry = (priority, new_item)
        heapq.heappush(self.items, entry)
        self.entry_finder[new_item] = priority

    def pop(self):
        while self.items:
            priority, item = heapq.heappop(self.items)
            if item is not self.REMOVED:
                del self.entry_finder[item]  # Remove from the dictionary
                return item
        raise Exception('Trying to pop from empty PriorityQueue.')

    def __contains__(self, key):
        # Return True if the item is still in the queue and not removed
        return key in self.entry_finder and self.entry_finder[key] is not self.REMOVED

    def __delitem__(self, key):
        # Instead of removing directly, mark it as removed
        if key in self.entry_finder:
            self.entry_finder[key] = self.REMOVED
        else:
            raise KeyError(str(key) + " is not in the priority queue")

    def __getitem__(self, key):
        # Return the priority of the item if it's still valid
        if key in self.entry_finder and self.entry_finder[key] is not self.REMOVED:
            return self.entry_finder[key]
        raise KeyError(str(key) + " is not in the priority queue")


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

class Problem(object):
    """
    Abstract Class, Make the code more readable (Maybe?)
    """

    def __init__(self, initial_State=None):
        self.initial_state = initial_State

    def valid_actions(self, state):
        """Return all valid action from given state"""
        raise NotImplementedError

    def result_after_actions(self, state, action):
        """Return the state after the given state received given action
            taken Action must belong to self.valid_actions
        """
        raise NotImplementedError

    def path_cost(self, c, state1, action) -> int:
        # Everything has its cost - Ca'i gi` cu~ng pha?i co' ca'i gia' cu?a no' '
        raise NotImplementedError

    def goal_test(self, state):
        """Check given state"""
        raise NotImplementedError

    def h(self, state):
        raise NotImplementedError


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

class Node:
    def __init__(self, state,
                 parents=None,
                 action: str = None,
                 path_cost=0):
        self.Daddy = parents
        self.State = state
        self.Action = action
        self.Path_cost = path_cost
        self.Depth = 0
        if self.Daddy:
            self.Depth = self.Daddy.Depth

    def child_gen(self, problem: Problem, action):
        child_state = problem.result_after_actions(self.State, action)
        return Node(child_state,
                    self,
                    action,
                    problem.path_cost(self.Path_cost, self.State, action))

    def path_to_cur_state(self):  # As it sounds
        node, path = self, []
        while node:
            path.append(node.Action)
            node = node.Daddy
        return path

    def all_legit_child(self, problem):
        return [self.child_gen(problem, action) for action in problem.valid_actions(self.State)]

    def __lt__(self, node):
        return self.State < node.State


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

def graph_search(problem, frontier):
    """
    Generalize the Blind search without cost.
    """
    assert isinstance(problem, Problem)
    frontier.append(Node(problem.initial_state))
    explored = set()  # initial empty set of explored states
    total_node = 1
    while len(frontier):
        node = frontier.pop()
        if problem.goal_test(node.State):
            return node, total_node
        explored.add(node.State)
        old_len = len(frontier)
        frontier.extend(child for child in node.all_legit_child(problem)
                        if child.State not in explored
                        and child not in frontier)
        total_node += len(frontier) - old_len
    return None, total_node


def breadth_first_search(problem):
    """ Search the shallowest nodes in the search tree first. """
    return graph_search(problem, FIFOQueue())


def depth_first_search(problem):
    return graph_search(problem, [])  # List can handle all we need from Stack


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#

def Priority_graph_search(problem, func):  # Using Priority Queue by default
    assert isinstance(problem, Problem)
    node = Node(problem.initial_state)
    total_node = 0
    if problem.goal_test(node.State):
        return node, total_node
    frontier = PriorityQueue(function=func)
    frontier.append(node)
    total_node += 1
    explored = set()
    while len(frontier.items):
        node = frontier.pop()
        if problem.goal_test(node.State):
            return node, total_node
        explored.add(node.State)
        for child in node.all_legit_child(problem):
            if child.State not in explored and child not in frontier:
                frontier.append(child)
                total_node += 1
            elif child in frontier:
                # Check if the new f_value of this state is less than the old value.
                if func(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
                    total_node += 1
    return None, total_node


def uniform_cost_search(problem):
    return Priority_graph_search(problem, func=lambda x: x.Path_cost)


def memoize(funct, slot=None, max_size=4096):
    """
    Cache the calculated value to prevent recalculating
    """
    if slot:  # Attribute's name
        def memoized_function(obj, *args):
            if hasattr(obj, slot):  # The Obj_value has already been calculated.
                return getattr(obj, slot)
            else:  # if it hasn't been calculated yet → Calculate the Value and cache.
                val = funct(obj, *args)
                setattr(obj, slot, val)
                return val
    else:  # If the attribute's name isn't provided.
        @functools.lru_cache(maxsize=max_size)
        def memoized_function(*args):
            return funct(*args)

    return memoized_function


def a_star_search(problem: Problem, h=None):
    """h: heuristic function """
    h = memoize(h if h is not None else problem.h, slot='h')
    return Priority_graph_search(problem, lambda x: x.Path_cost + h(x))


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
class SokobanProblem(Problem):
    def __init__(self, init_maze: Maze):
        super(SokobanProblem, self).__init__()
        assert isinstance(init_maze, Maze)
        self.Switches = init_maze.Switches
        self.taboo_cells = init_maze.taboo_cells
        self.Walls = init_maze.Walls
        self.Stones_Weight = init_maze.Stones_Weight
        self.Ares = init_maze.Ares
        self.initial_state = (init_maze.Ares,
                              init_maze.Stones)

    def goal_test(self, state):
        return set(state[1]) == set(self.Switches)

    def valid_actions(self, state):
        Valid = []
        for move in ["u", "d", "r", "l"]:
            attempt_coordinates = move_towards(state[0], Direction[move])
            if attempt_coordinates in self.Walls:
                continue
            if attempt_coordinates in state[1]:
                if move_towards(attempt_coordinates, Direction[move]) in self.Walls:
                    continue
                if move_towards(attempt_coordinates, Direction[move]) in self.taboo_cells:
                    continue
                if move_towards(attempt_coordinates, Direction[move]) in state[1]:
                    continue
                Valid.append(str.upper(move))
                continue
            Valid.append(move)
        return Valid

    def result_after_actions(self, state, action):
        Stones = list(state[1])
        attempt_coordinates = move_towards(state[0], Direction[action])
        if attempt_coordinates in Stones:
            idx = Stones.index(attempt_coordinates)
            Stones[idx] = move_towards(attempt_coordinates, Direction[action])
        return attempt_coordinates, tuple(Stones)

    def path_cost(self, c, state1, action) -> int:
        attempt_coordinates = move_towards(state1[0], Direction[action])
        stone_Weight = 0
        move_cost = 1
        if attempt_coordinates in state1[1]:
            idx = state1[1].index(attempt_coordinates)
            stone_Weight += self.Stones_Weight[idx]
        return c + move_cost + stone_Weight

    def h(self, node: Node):
        """
        Heuristic function =
1/(N_stone_out_of_switch !=0 | 0) * Sum_over_Stones{[min_Distance(Box, Switch) *Stone_Weight]+Distance(Ares, Box)}

        """
        h_stones = 0
        not_in_Switches = 0
        for i, Stone in enumerate(node.State[1]):
            if Stone not in self.Switches:
                not_in_Switches += 1
            Ares_dis = Manhattan_distance(node.State[0], Stone)
            min_stone_switch_dis = Manhattan_distance(Stone, self.Switches[0])
            for switch in self.Switches:
                stone_switch_dis = Manhattan_distance(Stone, switch)
                if stone_switch_dis < min_stone_switch_dis:
                    min_stone_switch_dis = stone_switch_dis
            h_stones += Ares_dis + min_stone_switch_dis * self.Stones_Weight[i]
        return h_stones / not_in_Switches if not_in_Switches != 0 else 0


# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#
# -----------------------------------------------------------------------------#


Solution_type = {
    "DFS": depth_first_search,
    "BFS": breadth_first_search,
    "UCS": uniform_cost_search,
    "A*": a_star_search
}


def move_towards(p1, direct):
    return p1[0] + direct[0], p1[1] + direct[1]


def Manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p2[1] - p1[1])

def Try_to_Solve(input_maze: Maze, solution_type="A*"):
    sokoban_prob = SokobanProblem(input_maze)
    t1 = time.time()
    tracemalloc.start()
    solution = Solution_type[solution_type](sokoban_prob)
    peak_memory = tracemalloc.get_traced_memory()[1] / (2 ** 20)
    t2 = time.time()
    time_consume = (t2 - t1) * 1000

    if solution[0] is None:  # no Solution
        lines = [solution_type.upper(),
                 f"Steps: 0, Weight: 0, Node: {solution[1]}, Time (ms): {time_consume:.2f}, Memory (MB): {peak_memory:.2f}",
                 "No path found"]
        result = {'path': None}
    else:
        path = solution[0].path_to_cur_state()[:-1]
        path.reverse()
        steps = len(path)
        path_cost = solution[0].Path_cost
        lines = [solution_type.upper(),
                 f"Steps: {steps}, Weight: {path_cost - steps}, Node: {solution[1]}, Time (ms): {time_consume:.2f}, Memory (MB): {peak_memory:.2f}",
                 "".join(path)]
        result = {'path': path,
                  'total step': len(path),
                  'total generated nodes': solution[1],
                  'total cost': path_cost,
                  'peak memory usage': peak_memory,
                  'Time consume': time_consume}
    with open('Output/output-' + str(input_maze.name) + '.txt', 'a') as f:
        for line in lines:
            f.writelines(line + '\n')
    return result

def run_solver(maze_path, algorithm, conn):
    _maze = Maze(maze_path)
    _algorithm = algorithm.upper()
    result = Try_to_Solve(_maze, _algorithm)
    conn.send(result)
    conn.close()
