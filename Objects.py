import string

import numpy as np
from numpy import ndarray

Directions = {
    'l': np.array([0, -1]),
    'r': np.array([0, 1]),
    'u': np.array([-1, 0]),
    'd': np.array([1, 0]),
    'L': np.array([0, -1]),
    'R': np.array([0, 1]),
    'U': np.array([-1, 0]),
    'D': np.array([1, 0]),
}
All_move = ['L', 'R', 'U', 'D']
All_Ares_move = ['l', 'r', 'u', 'd']


class Object:
    Map = None

    @staticmethod
    def valid_move(cur_pos: ndarray):
        pass

    def __init__(self, xpos, ypos):
        self.init_pos = np.array([xpos, ypos])
        self.pos = self.init_pos

    def get_valid_move(self):
        pass

    def Move(self, direction):
        pass


class Ares(Object):

    @staticmethod
    def valid_move(cur_pos: ndarray):
        valid_move = []
        for move in All_Ares_move:
            if Ares.Map[tuple(cur_pos + Directions[move])] in [' ', '.']:
                valid_move.append(move)
        return valid_move

    def __init__(self, xpos, ypos):
        super(Ares, self).__init__(xpos, ypos)
        self.Move_list = []

    def Move(self, direction: string):
        self.pos += Directions[direction]
        self.Move_list.append(direction)


class Stone(Object):
    @staticmethod
    def valid_move(cur_pos: ndarray):
        valid_move = []
        for move in All_move:
            if Stone.Map[tuple(cur_pos + Directions[move])] in [' ', '@', '.'] and Stone.Map[tuple(cur_pos + -1 * Directions[move])] in [' ', '@', '.']:
                valid_move.append(move)
        return valid_move

    def __init__(self, xpos, ypos, weight):
        super(Stone, self).__init__(xpos, ypos)
        self.weight = weight

    def Move(self, direction):
        self.pos += Directions[direction]
