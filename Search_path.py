import dataclasses
import functools
from copy import deepcopy

import collections
from Get_Maze import Maze

import heapq


@dataclasses.dataclass
class FIFOQueue(collections.deque):
    """
    A First-In-First-Out Queue.
    """

    def __init__(self):
        collections.deque.__init__(self)

    def pop(self):
        return self.popleft()


@dataclasses.dataclass
class PriorityQueue:
    def __init__(self, function=lambda x: x):
        self.items = []
        self.f = function

    def append(self, new_item):
        heapq.heappush(self.items, (self.f(new_item), new_item))
        # Use heapq for a better speed (maybe?)
        # ref: https://www.geeksforgeeks.org/difference-between-heapq-and-priorityqueue-in-python/

    def pop(self):
        if self.items:
            return heapq.heappop(self.items)[1]
        else:
            raise Exception('Trying to pop from empty PriorityQueue.')

    def __contains__(self, key):
        return any([item == key for _, item in self.items])

    def __delitem__(self, key):
        try:
            del self.items[[item == key for _, item in self.items].index(True)]
        except ValueError:
            raise KeyError(str(key) + " is not in the priority queue")
        heapq.heapify(self.items)


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
        # Everything has its cost - Ca'i gi` cu~ng pha?i co' ca'i gia' cu?a no'
        raise NotImplementedError

    def goal_test(self, state):
        """Check given state"""
        raise NotImplementedError

    # def h(self, state):

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
                    problem.path_cost(self.Path_cost, deepcopy(self.State), action))

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


def graph_search(problem, frontier):
    """
    Generalize the Blind search without cost.
    """
    assert isinstance(problem, Problem)
    frontier.append(Node(problem.initial_state))
    explored = set()  # initial empty set of explored states
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.State):
            return node
        explored.add(node.State)
        frontier.extend(child for child in node.all_legit_child(problem)
                        if child.State not in explored
                        and child not in frontier)
    return None


def Priority_graph_search(problem, func):  # Using Priority Queue by default
    assert isinstance(problem, Problem)
    node = Node(problem.initial_state)
    if problem.goal_test(node.State):
        return node
    frontier = PriorityQueue(function=func)
    frontier.append(node)
    explored = set()
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.State):
            return node
        explored.add(node.State)
        for child in node.all_legit_child(problem):
            if child.State not in explored and child not in frontier:
                frontier.append(child)
            elif child in frontier:
                # Check if the new f_value of this state is less than the old value.
                if func(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)
    return None


def breadth_first_search(problem):
    """ Search the shallowest nodes in the search tree first. """
    return graph_search(problem, FIFOQueue())


def depth_first_search(problem):
    return graph_search(problem, [])  # List can handle all we need from Stack


def uniform_cost_search(problem):
    return Priority_graph_search(problem, func=lambda x: x.Path_cost)


def memoize(funct, slot=None, max_size=256):
    """
    Cache the calculated value to prevent recalculating
    """
    if slot:  # Attribute's name
        def memoized_function(obj, *args):
            if hasattr(__obj=obj, __name=slot):  # The Obj_value has already been calculated.
                return getattr(__o=obj, __name=slot)
            else:  # if it hasn't been calculated yet → Calculate the Value and cache.
                val = funct(obj, *args)
                setattr(__obj=obj, __name=slot, __value=val)
                return val
    else:  # If the attribute's name isn't provided.
        @functools.lru_cache(maxsize=max_size)
        def memoized_function(*args):
            return funct(*args)

    return memoized_function


def a_star_search(problem: Problem, h=None):
    """h: heuristic function """
    memoize(h or problem.h, slot='h')
    return Priority_graph_search(problem, lambda x: x.path_cost+h(x))


class SokobanProblem(Problem):
    def __init__(self, init_maze: Maze):
        super(SokobanProblem, self).__init__()
        assert isinstance(init_maze, Maze)
        self.Switches = maze.Switches
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
            attemp_coordinates = move_towards(state[0], Direction[move])
            if attemp_coordinates in self.Walls:
                continue
            if attemp_coordinates in state[1]:
                if move_towards(attemp_coordinates, Direction[move]) in self.Walls:
                    continue
                if move_towards(attemp_coordinates, Direction[move]) in self.taboo_cells:
                    continue
                if move_towards(attemp_coordinates, Direction[move]) in state[1]:
                    continue
                Valid.append(str.upper(move))
                continue
            Valid.append(move)
        return Valid

    def result_after_actions(self, state, action):
        Stones = list(deepcopy(state)[1])
        attemp_coordinates = move_towards(state[0], Direction[action])
        if attemp_coordinates in Stones:
            idx = Stones.index(attemp_coordinates)
            Stones[idx] = move_towards(attemp_coordinates, Direction[action])
        return attemp_coordinates, tuple(Stones)

    def path_cost(self, c, state1, action) -> int:
        attemp_coordinates = move_towards(state1[0], Direction[action])
        stone_Weight = 0
        move_cost = 1
        if attemp_coordinates in state1[1]:
            idx = state1[1].index(attemp_coordinates)
            stone_Weight += self.Stones_Weight[idx]
        return c + move_cost + stone_Weight


def Try_to_Solve(input_maze: Maze):
    sokoban = SokobanProblem(input_maze)
    solution = uniform_cost_search(sokoban)

    if solution is None:  # no Soultion
        return "Impossible", None
    else:
        path = solution.path_to_cur_state()[:-1]
        path.reverse()
        return path, len(path), solution.Path_cost, solution


def move_towards(p1, direct):
    return p1[0] + direct[0], p1[1] + direct[1]


maze = Maze('input2.txt')
sokoban = SokobanProblem(maze)
# tmp = sokoban.initial_state
# print(sokoban.valid_actions(sokoban.initial_state))
# print("________________")
# rootNode = Node(sokoban.initial_state, None, None, 0)
# children = rootNode.all_legit_child(sokoban)
# print("________________")
# print(children[2].State)
# print(sokoban.valid_actions(children[2].State))
# print("________________")
# children2 = children[2].all_legit_child(sokoban)
# for chil in children2:
#     print(chil.State, chil.Action)

out = Try_to_Solve(maze)
print(out)





