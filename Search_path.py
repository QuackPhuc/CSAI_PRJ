from typing import Optional

import Get_Maze
import sys
import itertools
import functools
import heapq

from copy import deepcopy

import collections
from queue import PriorityQueue, Queue, LifoQueue
from Get_Maze import Maze


class FIFOQueue(collections.deque):
    """
    A First-In-First-Out Queue.
    """

    def __init__(self):
        collections.deque.__init__(self)

    def pop(self):
        return self.popleft()


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
    Abstract Class
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

    def path_cost(self, c, state1, action, state2) -> int:
        return 1

    def goal_test(self, state):
        """Check given state"""
        raise NotImplementedError


class Node:
    def __init__(self, state,
                 parents=None,
                 action: str = None,
                 path_cost=0):
        self.Daddy = parents
        self.State = state
        self.Action = action
        self.Path_cost = 0
        self.Depth = 0
        if self.Daddy:
            self.Depth = self.Daddy.Depth

    def child_gen(self, problem: Problem, action):
        child_state = problem.result_after_actions(self.State, action)
        return Node(child_state,
                    self,
                    action,
                    problem.path_cost(self.Path_cost, deepcopy(self.State), action, child_state))

    def path_to_cur_state(self):  # As it sounds
        node, path = self, []
        while node:
            path.append(node.Action)
            node = node.Daddy
        return path

    def all_legit_child(self, problem):
        return [self.child_gen(problem, action) for action in problem.valid_actions(self.State)]


def graph_search(problem, frontier):
    """
    Search through the successors of a problem to find a goal.
    The argument frontier should be an empty queue.
    If two paths reach a state, only use the first one. [Fig. 3.7]
    Return
        the node of the first goal state found
        or None is no goal state is found
    """
    assert isinstance(problem, Problem)
    frontier.append(Node(problem.initial_state))
    explored = set()  # initial empty set of explored states
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.State):
            return node
        try:
            explored.add(node.State)
        except:
            print(node.State)
            raise NotImplementedError
        # Python note: next line uses of a generator
        frontier.extend(child for child in node.all_legit_child(problem)
                        if child.State not in explored
                        and child not in frontier)
    return None


def breadth_first_search(problem):
    "Search the shallowest nodes in the search tree first."
    return graph_search(problem, FIFOQueue())


class SokobanProblem(Problem):
    def __init__(self, maze: Maze):
        super(SokobanProblem, self).__init__()
        assert isinstance(maze, Maze)
        self.maze = maze
        self.taboo_cells = maze.taboo_cells
        self.Walls = maze.Walls
        self.Stones_Weight = maze.Stones_Weight
        self.Ares = maze.Ares
        self.initial_state = (maze.Ares,
                              maze.Stones)

    def goal_test(self, state):
        return set(state[1]) == set(self.maze.Switches)

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


def Try_to_Solve(input_maze: Maze):
    sokoban = SokobanProblem(input_maze)
    solution = breadth_first_search(sokoban)

    if solution is None:  # no Soultion
        return "Impossible", None
    else:
        path = solution.path_to_cur_state()[:-1]
        path.reverse()
        return path
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

print(Try_to_Solve(maze))
